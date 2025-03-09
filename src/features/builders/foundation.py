"""Foundation feature builder for March Madness predictor.

This module implements the Phase 1 foundation features:
1. Simple Shooting Metrics (eFG%, TS%, Three-Point Rate, Free Throw Rate)
2. Basic Possession Metrics (Rebound Percentages, Assist Rate, Turnover Percentage)
3. Win Percentage breakdowns (home, away, neutral)
4. Recent Form and Consistency metrics
5. Home Court Advantage rating
"""


import logging

import numpy as np
import polars as pl

from src.features.core.base import BaseFeature as BaseFeatureBuilder

logger = logging.getLogger(__name__)


class FoundationFeatureBuilder(BaseFeatureBuilder):
    """Builder for foundation-level features."""
    
    def __init__(self, config: dict[str, object] | None = None) -> None:
        """Initialize the foundation feature builder.
        
        Args:
            config: Configuration parameters including:
                - recent_form_games: Number of games to consider for recent form (default: 10)
                - output_file: Name of the output file (default: team_performance.parquet)
        """
        super().__init__(config)
        self.name = "foundation"
        self.recent_form_games = self.config.get("recent_form_games", 10)
        self.output_file = self.config.get("output_file", "team_performance.parquet")
        
    def safe_join(
        self, 
        left: pl.DataFrame, 
        right: pl.DataFrame, 
        on: str | list[str], 
        how: str = "inner", 
        suffix: str = "_right"
    ) -> pl.DataFrame:
        """Safely join two DataFrames with handling for duplicate columns.
        
        This utility method wraps polars join operations to consistently handle
        column name conflicts during joins.
        
        Args:
            left: Left DataFrame in the join
            right: Right DataFrame in the join
            on: Column name(s) to join on
            how: Join type ('inner', 'left', 'outer', etc.)
            suffix: Suffix to add to duplicate column names from the right DataFrame
            
        Returns:
            Joined DataFrame with duplicate columns properly suffixed
        """
        try:
            return left.join(right, on=on, how=how, suffix=suffix)
        except Exception as e:
            logger.error(f"Join error in foundation feature builder: {e}")
            # Try to provide more helpful error message
            if "duplicate" in str(e).lower():
                common_cols = set(left.columns).intersection(set(right.columns))
                join_cols = [on] if isinstance(on, str) else on
                duplicate_cols = common_cols - set(join_cols)
                logger.warning(f"Duplicate columns detected: {duplicate_cols}")
            raise
    
    def build_features(self, 
                      team_season_stats: pl.DataFrame,
                      team_box: pl.DataFrame) -> pl.DataFrame:
        """Build foundation features.
        
        Args:
            team_season_stats: Team season statistics DataFrame 
            team_box: Team box scores DataFrame
            
        Returns:
            DataFrame with foundation features
        """
        # Start with the base dataset
        features = team_season_stats.clone()
        
        # Load schedules data to get accurate neutral site information
        try:
            schedules = pl.read_parquet("data/processed/schedules.parquet")
        except Exception as e:
            # If schedules data cannot be loaded, log a warning and continue without it
            logger.warning(f"Could not load schedules data: {e}. Neutral site win percentage may be inaccurate.")
            schedules = None
        
        # Generate shooting metrics
        shooting_metrics = self._calculate_shooting_metrics(team_box)
        
        # Generate possession metrics
        possession_metrics = self._calculate_possession_metrics(team_box)
        
        # Generate win percentage breakdowns
        win_pct_metrics = self._calculate_win_percentage_breakdowns(team_box, schedules)
        
        # Generate recent form and consistency metrics
        form_metrics = self._calculate_form_metrics(team_box)
        
        # Generate home court advantage rating
        hca_metrics = self._calculate_home_court_advantage(team_box)
        
        # Combine all metrics into a single DataFrame
        all_metrics = shooting_metrics
        for df in [possession_metrics, win_pct_metrics, form_metrics, hca_metrics]:
            all_metrics = self.safe_join(
                all_metrics, df, on=["team_id", "season"], how="left"
            )
        
        # Join with the base team_season_stats DataFrame and return
        return features.join(
            all_metrics, on=["team_id", "season"], how="left"
        )
    
    def _calculate_shooting_metrics(self, team_box: pl.DataFrame) -> pl.DataFrame:
        """Calculate shooting metrics for each team and season.
        
        Includes: 
        - Effective Field Goal Percentage (eFG%)
        - True Shooting Percentage (TS%)
        - Three-Point Rate
        - Free Throw Rate
        
        Args:
            team_box: Team box scores DataFrame
            
        Returns:
            DataFrame with shooting metrics by team and season
        """
        return (
            team_box
            .group_by(["team_id", "season"])
            .agg([
                # Effective Field Goal Percentage: (FG + 0.5 * 3PM) / FGA
                ((pl.col("field_goals_made") + 0.5 * pl.col("three_point_field_goals_made")) / 
                 pl.col("field_goals_attempted")).mean().alias("efg_pct"),
                
                # True Shooting Percentage: PTS / (2 * (FGA + 0.44 * FTA))
                (pl.col("team_score") / (2 * (pl.col("field_goals_attempted") + 
                                             0.44 * pl.col("free_throws_attempted")))).mean().alias("ts_pct"),
                
                # Three-Point Rate: 3PA / FGA
                (pl.col("three_point_field_goals_attempted") / 
                 pl.col("field_goals_attempted")).mean().alias("three_point_rate"),
                
                # Free Throw Rate: FTA / FGA
                (pl.col("free_throws_attempted") / 
                 pl.col("field_goals_attempted")).mean().alias("ft_rate"),
            ])
        )
    
    def _calculate_possession_metrics(self, team_box: pl.DataFrame) -> pl.DataFrame:
        """Calculate possession metrics for each team and season.
        
        Includes:
        - Offensive Rebound Percentage
        - Defensive Rebound Percentage
        - Total Rebound Percentage
        - Assist Rate
        - Turnover Percentage
        
        Args:
            team_box: Team box scores DataFrame
            
        Returns:
            DataFrame with possession metrics by team and season
        """
        # Create a temporary DataFrame with opponent stats for the same game
        team_box_with_opp = team_box.join(
            team_box.select(
                pl.col("game_id"),
                pl.col("team_id").alias("opp_team_id"),
                pl.col("offensive_rebounds").alias("opp_offensive_rebounds"),
                pl.col("defensive_rebounds").alias("opp_defensive_rebounds"),
                pl.col("field_goals_attempted").alias("opp_fga"),
                pl.col("field_goals_made").alias("opp_fgm"),
            ),
            on="game_id",
            how="left"
        ).filter(
            pl.col("team_id") != pl.col("opp_team_id")
        )
        
        return (
            team_box_with_opp
            .group_by(["team_id", "season"])
            .agg([
                # Offensive Rebound Percentage: ORB / (ORB + Opp DRB)
                (pl.col("offensive_rebounds") / 
                 (pl.col("offensive_rebounds") + pl.col("opp_defensive_rebounds"))).mean().alias("orb_pct"),
                
                # Defensive Rebound Percentage: DRB / (DRB + Opp ORB)
                (pl.col("defensive_rebounds") / 
                 (pl.col("defensive_rebounds") + pl.col("opp_offensive_rebounds"))).mean().alias("drb_pct"),
                
                # Total Rebound Percentage: TRB / (TRB + Opp TRB)
                (pl.col("total_rebounds") / 
                 (pl.col("total_rebounds") + 
                  (pl.col("opp_offensive_rebounds") + pl.col("opp_defensive_rebounds")))).mean().alias("trb_pct"),
                
                # Assist Rate: AST / FGM
                (pl.col("assists") / pl.col("field_goals_made")).mean().alias("ast_rate"),
                
                # Turnover Percentage: TOV / (FGA + 0.44 * FTA + TOV)
                (pl.col("turnovers") / 
                 (pl.col("field_goals_attempted") + 0.44 * pl.col("free_throws_attempted") + 
                  pl.col("turnovers"))).mean().alias("tov_pct"),
                
                # Assist-to-Turnover Ratio: AST / TOV
                (pl.col("assists") / pl.col("turnovers")).mean().alias("ast_to_tov_ratio"),
            ])
        )
    
    def _calculate_win_percentage_breakdowns(
        self, 
        team_box: pl.DataFrame, 
        schedules: pl.DataFrame | None
    ) -> pl.DataFrame:
        """Calculate win percentage breakdowns for each team and season.
        
        Includes:
        - Win percentages by venue type (home, away, neutral)
        
        Args:
            team_box: Team box scores DataFrame
            schedules: Schedules DataFrame
            
        Returns:
            DataFrame with win percentage breakdowns by team and season
        """
        # For each game location (home, away, neutral), calculate wins and games played
        if schedules is None:
            # If schedules data is not available, use the old method (less accurate)
            is_neutral = (pl.col("team_home_away") != "home").and_(pl.col("team_home_away") != "away")
        else:
            # Extract just the columns we need from schedules
            neutral_info = schedules.select(
                ["game_id", "neutral_site"]
            )
            
            # Join team_box with schedules to get accurate neutral site information
            team_box = team_box.join(
                neutral_info,
                on="game_id",
                how="left"
            )
            
            # If neutral_site is null (couldn't find in schedules), use the old method
            team_box = team_box.with_columns(
                pl.when(pl.col("neutral_site").is_null())
                  .then((pl.col("team_home_away") != "home").and_(pl.col("team_home_away") != "away"))
                  .otherwise(pl.col("neutral_site"))
                  .alias("neutral_site")
            )
            
            # Use the neutral_site column from schedules
            is_neutral = pl.col("neutral_site")
        
        return (
            team_box
            .with_columns([
                # Convert team_winner to numeric
                pl.col("team_winner").cast(pl.Int32).alias("win")
            ])
            .group_by(["team_id", "season"])
            .agg([
                # Home win percentage (non-neutral home games)
                pl.col("win")
                  .filter((pl.col("team_home_away") == "home") & (~is_neutral))
                  .mean()
                  .alias("home_win_pct_detailed"),
                
                # Away win percentage (non-neutral away games)
                pl.col("win")
                  .filter((pl.col("team_home_away") == "away") & (~is_neutral))
                  .mean()
                  .alias("away_win_pct_detailed"),
                
                # Neutral site win percentage
                pl.col("win")
                  .filter(is_neutral)
                  .mean()
                  .alias("neutral_win_pct"),
                
                # Games played by location
                pl.col("win")
                  .filter((pl.col("team_home_away") == "home") & (~is_neutral))
                  .count()
                  .alias("home_games_played"),
                
                pl.col("win")
                  .filter((pl.col("team_home_away") == "away") & (~is_neutral))
                  .count()
                  .alias("away_games_played"),
                
                pl.col("win")
                  .filter(is_neutral)
                  .count()
                  .alias("neutral_games_played"),
            ])
        )
    
    def _calculate_form_metrics(self, team_box: pl.DataFrame) -> pl.DataFrame:
        """Calculate recent form and consistency metrics for each team and season.
        
        Includes:
        - Recent form (weighted average of recent performance)
        - Performance consistency (standard deviation of scoring)
        
        Args:
            team_box: Team box scores DataFrame
            
        Returns:
            DataFrame with form metrics by team and season
        """
        # Add game sequence number within each season for each team
        team_box_with_seq = (
            team_box
            .sort(["team_id", "season", "game_date"])
            .with_columns([
                pl.col("team_score").alias("points"),
                pl.col("opponent_team_score").alias("opponent_points"),
                (pl.col("team_score") - pl.col("opponent_team_score")).alias("point_diff"),
                pl.col("team_winner").cast(pl.Int32).alias("win")
            ])
            .with_columns([
                pl.col("win").cum_sum().over(["team_id", "season"]).alias("cumulative_wins"),
                pl.col("game_id").count().over(["team_id", "season"]).alias("game_num"),
            ])
        )
        
        # Calculate metrics for each team and season
        return (
            team_box_with_seq
            .group_by(["team_id", "season"])
            .agg([
                # Point differential consistency (std dev)
                pl.col("point_diff").std().alias("point_diff_stddev"),
                # Scoring consistency (std dev)
                pl.col("points").std().alias("scoring_stddev"),
                # Recent form - need to calculate outside of group_by
                pl.col("game_date").max().alias("last_game_date"),
                pl.col("game_num").max().alias("total_games"),
            ])
            .join(
                # Calculate recent form as exponentially weighted average
                self._calculate_recent_form(team_box_with_seq),
                on=["team_id", "season"],
                how="left"
            )
        )
    
    def _calculate_recent_form(self, team_box: pl.DataFrame) -> pl.DataFrame:
        """Calculate the recent form metrics based on recent games.
        
        Args:
            team_box: Team box scores DataFrame with game sequence number
            
        Returns:
            DataFrame with recent form metrics
        """
        results = []
        
        # Process each team-season separately to handle exponential weighting
        for team_id in team_box["team_id"].unique():
            for season in team_box.filter(pl.col("team_id") == team_id)["season"].unique():
                team_season_games = (
                    team_box
                    .filter(
                        (pl.col("team_id") == team_id) & 
                        (pl.col("season") == season)
                    )
                    .sort("game_date")
                )
                
                if team_season_games.height == 0:
                    continue
                
                # Get recent games
                recent_games = team_season_games.tail(self.recent_form_games)
                
                if recent_games.height == 0:
                    continue
                
                # Calculate exponentially weighted metrics
                game_weights = np.exp(np.linspace(-3, 0, min(self.recent_form_games, recent_games.height)))
                game_weights = game_weights / game_weights.sum()
                
                # Calculate weighted averages
                weighted_point_diff = np.average(
                    recent_games["point_diff"].to_numpy(), 
                    weights=game_weights
                )
                
                weighted_win_pct = np.average(
                    recent_games["win"].to_numpy(), 
                    weights=game_weights
                )
                
                results.append({
                    "team_id": team_id,
                    "season": season,
                    "recent_point_diff": weighted_point_diff,
                    "recent_win_pct": weighted_win_pct,
                })
        
        return pl.DataFrame(results) if results else pl.DataFrame({
            "team_id": [],
            "season": [],
            "recent_point_diff": [],
            "recent_win_pct": []
        })
    
    def _calculate_home_court_advantage(self, team_box: pl.DataFrame) -> pl.DataFrame:
        """Calculate home court advantage rating for each team and season.
        
        Args:
            team_box: Team box scores DataFrame
            
        Returns:
            DataFrame with home court advantage metrics by team and season
        """
        # Calculate scoring margin difference between home and away/neutral games
        team_box_with_margin = (
            team_box
            .with_columns([
                (pl.col("team_score") - pl.col("opponent_team_score")).alias("margin"),
                (pl.col("team_home_away") == "home").cast(pl.Int32).alias("is_home")
            ])
        )
        
        return (
            team_box_with_margin
            .group_by(["team_id", "season", "is_home"])
            .agg([
                pl.col("margin").mean().alias("avg_margin"),
                pl.col("team_winner").cast(pl.Int32).mean().alias("win_pct")
            ])
            .pivot(values=["avg_margin", "win_pct"], index=["team_id", "season"], on="is_home")
            .with_columns([
                # Home court advantage = difference between home and away margin
                (pl.col("avg_margin_1") - pl.col("avg_margin_0")).alias("home_court_advantage"),
                # Home court win boost = difference between home and away win percentage
                (pl.col("win_pct_1") - pl.col("win_pct_0")).alias("home_win_boost")
            ])
            .select(["team_id", "season", "home_court_advantage", "home_win_boost"])
        ) 