"""Offensive Efficiency implementation.

This module implements the Offensive Efficiency feature, which measures
the number of points scored per 100 possessions.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature
from src.features.possession.P01_possessions import Possessions

logger = logging.getLogger(__name__)


class OffensiveEfficiency(BaseFeature):
    """Offensive Efficiency feature.
    
    Offensive Efficiency (also called Offensive Rating) measures how many points
    a team scores per 100 possessions. It's a tempo-free measure of offensive performance.
    
    Formula: (Points / Possessions) * 100
    """
    
    id = "A01"
    name = "Offensive Efficiency"
    category = "advanced_team"
    description = "Points scored per 100 possessions"
    
    def __init__(self, possessions_feature: Possessions | None = None) -> None:
        """Initialize the feature.
        
        Args:
            possessions_feature: An instance of the Possessions feature.
                If not provided, a new one will be created.
        """
        super().__init__()
        self._possessions_feature = possessions_feature or Possessions()
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def get_dependencies(self) -> list[BaseFeature]:
        """Get features this feature depends on.
        
        Returns:
            List of features this feature depends on.
        """
        return [self._possessions_feature]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Offensive Efficiency.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and offensive_efficiency columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Offensive Efficiency calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "points", "season"
        ]
        
        missing_cols = [col for col in required_cols if col not in team_box.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Calculate possessions using the Possessions feature
        possessions_df = self._possessions_feature.calculate(data)
        
        # Check for team_display_name column
        has_display_name = "team_display_name" in team_box.columns
        
        # Group by team_id, team_name, and season
        group_cols = ["team_id", "team_name", "season"]
        if has_display_name:
            group_cols.append("team_display_name")
            
        # Calculate points per game
        points_df = (
            team_box
            .group_by(group_cols)
            .agg([
                pl.len().alias("games_played"),
                pl.sum("points").alias("total_points")
            ])
            .with_columns([
                (pl.col("total_points") / pl.col("games_played")).alias("points_per_game")
            ])
        )
        
        # Drop intermediate columns from points_df
        points_df = points_df.drop(["games_played", "total_points"])
        
        # Handle case where team_display_name is missing in points_df
        if has_display_name:
            points_df = points_df.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            points_df = points_df.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        # Join points_df with possessions_df
        join_cols = ["team_id", "team_name", "team_location", "season"]
        result = points_df.join(possessions_df, on=join_cols, how="inner")
        
        # Calculate offensive efficiency (points per 100 possessions)
        result = result.with_columns([
            ((pl.col("points_per_game") / pl.col("possessions")) * 100).alias("offensive_efficiency")
        ])
        
        # Drop intermediate columns
        return result.drop(["points_per_game", "possessions"])
        
