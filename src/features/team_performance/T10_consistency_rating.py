"""Consistency Rating implementation.

This module implements the Consistency Rating feature, which measures
the variance in a team's game-to-game performance.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class ConsistencyRating(BaseFeature):
    """Consistency Rating feature.
    
    Consistency Rating measures how variable a team's performance is from game to game.
    A lower value indicates more consistent performance, while a higher value
    indicates more unpredictable performance with higher variability.
    
    The feature is calculated as the standard deviation of point differentials,
    with a minimum of 5 games required for reliable calculation.
    """
    
    id = "T10"
    name = "Consistency Rating"
    category = "team_performance"
    description = "Variance in game-to-game performance"
    
    def __init__(self, min_games: int = 5) -> None:
        """Initialize the feature.
        
        Args:
            min_games: Minimum number of games required for calculation.
        """
        super().__init__()
        self.min_games = min_games
        
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Consistency Rating.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and consistency_rating columns.
            Lower values indicate more consistent performance.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Consistency Rating calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "points", "opponent_points", "season"
        ]
        
        missing_cols = [col for col in required_cols if col not in team_box.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Check for team_display_name column
        has_display_name = "team_display_name" in team_box.columns
        
        # Calculate point differential for each game
        with_diff = team_box.with_columns([
            (pl.col("points") - pl.col("opponent_points")).alias("point_differential")
        ])
        
        # Group by team and season
        group_cols = ["team_id", "team_name", "season"]
        if has_display_name:
            group_cols.append("team_display_name")
            
        # Calculate standard deviation of point differentials
        result = (
            with_diff
            .group_by(group_cols)
            .agg([
                pl.len().alias("games_played"),
                pl.std("point_differential").alias("consistency_rating")
            ])
            .filter(pl.col("games_played") >= self.min_games)
            .drop("games_played")
        )
        
        # Handle case where team_display_name is missing
        if has_display_name:
            result = result.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 