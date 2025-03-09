"""Home Court Advantage implementation.

This module implements the Home Court Advantage feature, which measures
how much better a team performs at home compared to away games.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class HomeCourtAdvantage(BaseFeature):
    """Home Court Advantage feature.
    
    Home Court Advantage measures how much better a team performs at home compared to away games.
    This is calculated as the difference in point differential between home and away games.
    
    Formula: (Home Point Differential) - (Away Point Differential)
    """
    
    id = "A06"
    name = "Home Court Advantage"
    category = "advanced_team"
    description = "Rating of how much better a team performs at home"
    
    def __init__(self, min_home_games: int = 5, min_away_games: int = 5) -> None:
        """Initialize the Home Court Advantage feature.
        
        Args:
            min_home_games: Minimum number of home games required for calculation.
            min_away_games: Minimum number of away games required for calculation.
        """
        super().__init__()
        self.min_home_games = min_home_games
        self.min_away_games = min_away_games
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box", "schedules"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Home Court Advantage.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and home_court_advantage columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Home Court Advantage calculation")
            team_box = data["team_box"]
            schedules = data.get("schedules")
        else:
            team_box = data
            schedules = None
        
        # Log available columns to help with debugging
        logger.info(f"Team box columns: {team_box.columns}")
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "points", "opponent_points", "season", "venue_type"
        ]
        
        missing_cols = [col for col in required_cols if col not in team_box.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Check for team_display_name column
        has_display_name = "team_display_name" in team_box.columns
        
        # Process with neutral site data if available
        if schedules is not None and "neutral_site" in schedules.columns:
            logger.info("Enhancing Home Court Advantage calculation with neutral site information")
            
            # Extract neutral site games
            neutral_games = (
                schedules
                .filter(pl.col("neutral_site"))
                .select(["game_id", "neutral_site"])
            )
            
            # Join with team_box to identify neutral games
            team_box = (
                team_box
                .join(neutral_games, on="game_id", how="left")
                .with_columns([
                    pl.when(pl.col("neutral_site"))
                    .then(pl.lit("neutral"))
                    .otherwise(pl.col("venue_type"))
                    .alias("game_venue_type")
                ])
            )
        else:
            # If no schedules data, just use venue_type directly
            team_box = team_box.with_columns([
                pl.col("venue_type").alias("game_venue_type")
            ])
        
        # Create base group columns
        group_cols = ["team_id", "team_name", "season"]
        if has_display_name:
            group_cols.append("team_display_name")
        
        # Calculate point differential for home games
        home_games = (
            team_box
            .filter(pl.col("game_venue_type") == "home")
            .group_by(group_cols)
            .agg([
                pl.len().alias("home_games"),
                (pl.sum("points") - pl.sum("opponent_points")).alias("home_point_diff")
            ])
            .with_columns([
                (pl.col("home_point_diff") / pl.col("home_games")).alias("home_point_diff_per_game")
            ])
        )
        
        # Calculate point differential for away games
        away_games = (
            team_box
            .filter(pl.col("game_venue_type") == "away")
            .group_by(group_cols)
            .agg([
                pl.len().alias("away_games"),
                (pl.sum("points") - pl.sum("opponent_points")).alias("away_point_diff")
            ])
            .with_columns([
                (pl.col("away_point_diff") / pl.col("away_games")).alias("away_point_diff_per_game")
            ])
        )
        
        # Join the home and away data
        if has_display_name:
            join_cols = ["team_id", "team_name", "team_display_name", "season"]
        else:
            join_cols = ["team_id", "team_name", "season"]
            
        result = home_games.join(away_games, on=join_cols, how="inner")
        
        # Filter teams with sufficient games
        result = result.filter(
            (pl.col("home_games") >= self.min_home_games) & 
            (pl.col("away_games") >= self.min_away_games)
        )
        
        # Calculate Home Court Advantage
        result = result.with_columns([
            (
                pl.col("home_point_diff_per_game") - pl.col("away_point_diff_per_game")
            ).alias("home_court_advantage")
        ])
        
        # Drop intermediate columns
        result = result.drop([
            "home_games", "home_point_diff", "home_point_diff_per_game",
            "away_games", "away_point_diff", "away_point_diff_per_game"
        ])
        
        # Handle case where team_display_name is missing
        if has_display_name:
            result = result.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 