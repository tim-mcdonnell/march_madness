"""Point Differential implementation.

This module implements the Point Differential feature, which measures
the average point difference between a team's score and their opponent's score.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class PointDifferential(BaseFeature):
    """Point Differential feature.
    
    Point Differential measures the average point difference between a team's score
    and their opponent's score. A positive value indicates the team scores more points
    than they allow, while a negative value indicates the opposite.
    """
    
    id = "T02"
    name = "Point Differential"
    category = "team_performance"
    description = "Average point margin between a team's score and their opponent's score"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Point Differential.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and point_differential columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Point Differential calculation")
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
        
        # Group by team_id, team_name, and season
        group_cols = ["team_id", "team_name", "season"]
        if has_display_name:
            group_cols.append("team_display_name")
            
        # Calculate Point Differential (points scored minus points allowed)
        result = (
            team_box
            .group_by(group_cols)
            .agg([
                pl.len().alias("games_played"),
                pl.sum("points").alias("total_points_for"),
                pl.sum("opponent_points").alias("total_points_against")
            ])
            .with_columns([
                (pl.col("total_points_for") - pl.col("total_points_against")).alias("total_point_diff"),
                (pl.col("total_points_for") / pl.col("games_played")).alias("points_per_game"),
                (pl.col("total_points_against") / pl.col("games_played")).alias("opp_points_per_game")
            ])
            .with_columns([
                (pl.col("total_point_diff") / pl.col("games_played")).alias("point_differential")
            ])
        )
        
        # Drop intermediate columns
        result = result.drop([
            "games_played", "total_points_for", "total_points_against", 
            "total_point_diff", "points_per_game", "opp_points_per_game"
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