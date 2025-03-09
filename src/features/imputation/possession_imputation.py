"""
Module for imputing missing possession metrics using play-by-play data.

This is used when possession data is missing from team box scores.
"""

import logging
from pathlib import Path

import polars as pl

logger = logging.getLogger(__name__)

class PossessionImputation:
    """
    Imputation system for calculating possession metrics from play-by-play data.
    
    This class processes play-by-play data to calculate team possessions when this
    information is missing from the team box score data.
    
    Possession is calculated using the formula:
    Possessions = FGA + 0.475*FTA + TO - ORB
    
    Where:
    - FGA: Field Goal Attempts
    - FTA: Free Throw Attempts
    - TO: Turnovers
    - ORB: Offensive Rebounds
    """
    
    # Constants for possessions calculation
    FTA_FACTOR = 0.475
    
    def __init__(
        self,
        processed_dir: str | Path = "data/processed",
        features_dir: str | Path = "data/features",
        pbp_filename: str = "play_by_play.parquet",
    ) -> None:
        """
        Initialize the possession imputation system.
        
        Args:
            processed_dir: Directory containing processed data
            features_dir: Directory to store feature outputs
            pbp_filename: Filename for play-by-play data
        """
        self.processed_dir = Path(processed_dir)
        self.features_dir = Path(features_dir)
        self.pbp_filename = pbp_filename
        
        # Make sure the features directory exists
        self.features_dir.mkdir(exist_ok=True, parents=True)
        
        # PBP data source
        self.pbp_file = self.processed_dir / self.pbp_filename
        
        # Output file
        self.possession_file = self.features_dir / "possession_metrics.parquet"
    
    def _load_team_box_data(self) -> pl.DataFrame:
        """
        Load team box score data.
        
        Returns:
            DataFrame containing team box scores
        """
        team_box_file = self.processed_dir / "team_box.parquet"
        
        if not team_box_file.exists():
            raise FileNotFoundError(f"Team box file not found: {team_box_file}")
        
        return pl.read_parquet(team_box_file)
    
    def _load_pbp_data(self) -> pl.DataFrame:
        """
        Load play-by-play data.
        
        Returns:
            DataFrame containing play-by-play data
        """
        if not self.pbp_file.exists():
            raise FileNotFoundError(f"Play-by-play file not found: {self.pbp_file}")
        
        logger.info(f"Loading play-by-play data from {self.pbp_file}")
        return pl.read_parquet(self.pbp_file)
    
    def _extract_game_stats(self, pbp_data: pl.DataFrame) -> pl.DataFrame:
        """
        Extract game statistics from play-by-play data.
        
        Args:
            pbp_data: Play-by-play data
            
        Returns:
            DataFrame with game statistics for possession calculation
        """
        logger.info("Extracting game statistics from play-by-play data")
        
        # Filter for shot and turnover events
        type_filter = (
            (pl.col("type_text").str.contains("Shot")) | 
            (pl.col("type_text") == "Turnover") |
            (pl.col("type_text") == "Rebound") |
            (pl.col("type_text").str.contains("Free Throw"))
        )
        
        filtered_data = pbp_data.filter(type_filter)
        
        # Determine field goal attempts (shots)
        fga_data = (
            filtered_data
            .filter(
                pl.col("type_text").str.contains("Shot")
            )
            .group_by(["game_id", "team_id"])
            .agg(
                pl.count().alias("field_goals_attempted")
            )
        )
        
        # Free throw attempts
        fta_data = (
            filtered_data
            .filter(
                pl.col("type_text").str.contains("Free Throw")
            )
            .group_by(["game_id", "team_id"])
            .agg(
                pl.count().alias("free_throws_attempted")
            )
        )
        
        # Turnovers
        to_data = (
            filtered_data
            .filter(
                pl.col("type_text") == "Turnover"
            )
            .group_by(["game_id", "team_id"])
            .agg(
                pl.count().alias("turnovers")
            )
        )
        
        # Offensive rebounds
        orb_data = (
            filtered_data
            .filter(
                (pl.col("type_text") == "Rebound") &
                (pl.col("text").str.contains("Offensive"))
            )
            .group_by(["game_id", "team_id"])
            .agg(
                pl.count().alias("offensive_rebounds")
            )
        )
        
        # Join all stats
        game_stats = (
            fga_data
            .join(fta_data, on=["game_id", "team_id"], how="outer")
            .join(to_data, on=["game_id", "team_id"], how="outer")
            .join(orb_data, on=["game_id", "team_id"], how="outer")
        )
        
        # Fill NAs with 0
        game_stats = game_stats.fill_null(0)
        
        # Add season information
        if "season" in pbp_data.columns:
            seasons = (
                pbp_data
                .select(["game_id", "season"])
                .unique()
            )
            game_stats = game_stats.join(seasons, on="game_id", how="left")
        
        logger.info(f"Extracted stats for {game_stats.height} team-games")
        return game_stats
    
    def _calculate_possessions(self, game_stats: pl.DataFrame) -> pl.DataFrame:
        """
        Calculate possessions from game statistics.
        
        Args:
            game_stats: Game statistics
            
        Returns:
            DataFrame with possession calculations
        """
        logger.info("Calculating possessions from game statistics")
        
        return game_stats.with_columns([
            (
                pl.col("field_goals_attempted") + 
                pl.col("free_throws_attempted") * self.FTA_FACTOR +
                pl.col("turnovers") - 
                pl.col("offensive_rebounds")
            ).alias("possessions")
        ])
    
    def impute_possession_metrics(
        self, 
        possession_metrics: pl.DataFrame | None = None
    ) -> pl.DataFrame:
        """Impute missing possession metrics from play-by-play data.
        
        This method calculates possessions using the play-by-play data for games
        where the box score data does not include possessions.
        
        Args:
            possession_metrics: Optional existing possession metrics to augment
            
        Returns:
            DataFrame with possession metrics for all games
        """
        logger.info("Imputing possession metrics from play-by-play data")
        
        # If we already have possession metrics, use them
        if possession_metrics is not None:
            logger.info(f"Using provided possession metrics with {possession_metrics.height} rows")
            result = possession_metrics
        else:
            # Try to load existing possession metrics
            if self.possession_file.exists():
                logger.info(f"Loading existing possession metrics from {self.possession_file}")
                result = pl.read_parquet(self.possession_file)
            else:
                # Create empty DataFrame with the right columns
                result = pl.DataFrame({
                    "game_id": [],
                    "team_id": [],
                    "possessions": [],
                    "season": []
                })
        
        # Load team box data to see where we're missing possessions
        team_box = self._load_team_box_data()
        
        # Get unique game IDs where we have box score data
        box_games = team_box.select(["game_id", "team_id", "season"]).unique()
        
        # Determine which games already have possession metrics
        if not result.is_empty():
            games_with_metrics = result.select(["game_id", "team_id"]).unique()
            
            # Find games that need metrics
            missing_games = box_games.join(
                games_with_metrics,
                on=["game_id", "team_id"],
                how="anti"
            )
        else:
            # All games need metrics
            missing_games = box_games
        
        if missing_games.height == 0:
            logger.info("No missing possession metrics found")
            return result
        
        logger.info(f"Found {missing_games.height} team-games missing possession metrics")
        
        # Load play-by-play data
        pbp_data = self._load_pbp_data()
        
        # Extract game stats from PBP
        game_stats = self._extract_game_stats(pbp_data)
        
        # Calculate possessions
        possession_data = self._calculate_possessions(game_stats)
        
        # Filter for games we need
        needed_possessions = possession_data.join(
            missing_games,
            on=["game_id", "team_id"],
            how="inner"
        )
        
        if needed_possessions.height == 0:
            logger.warning(
                "Could not find any matching play-by-play data for games missing possession metrics"
            )
            return result
        
        logger.info(f"Calculated {needed_possessions.height} new possession metrics")
        
        # Add to existing metrics using ternary expression
        result = pl.concat([result, needed_possessions]) if not result.is_empty() else needed_possessions
        
        # Save to file
        result.write_parquet(self.possession_file)
        logger.info(f"Saved possession metrics to {self.possession_file}")
        
        return result

def impute_possession_metrics(
    processed_dir: str | Path = "data/processed",
    features_dir: str | Path = "data/features"
) -> Path:
    """Impute missing possession metrics from play-by-play data.
    
    Args:
        processed_dir: Directory containing processed data
        features_dir: Directory to store feature outputs
        
    Returns:
        Path to the possession metrics file
    """
    imputation = PossessionImputation(
        processed_dir=processed_dir,
        features_dir=features_dir
    )
    
    imputation.impute_possession_metrics()
    
    return imputation.possession_file 