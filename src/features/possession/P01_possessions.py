"""Possessions implementation.

This module implements the Possessions feature, which estimates 
the number of possessions a team has during a game.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class Possessions(BaseFeature):
    """Possessions feature.
    
    Possessions estimates the number of possessions a team has during a game.
    This is a fundamental metric for calculating possession-based efficiency statistics.
    
    Formula: FGA + 0.475*FTA - ORB + TO
    """
    
    id = "P01"
    name = "Possessions"
    category = "possession"
    description = "Estimated number of possessions per game"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Possessions.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and possessions columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Possessions calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "field_goals_attempted", "free_throws_attempted",
            "offensive_rebounds", "turnovers", "season"
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
            
        # Calculate Possessions
        result = (
            team_box
            .group_by(group_cols)
            .agg([
                pl.len().alias("games_played"),
                pl.sum("field_goals_attempted").alias("fga"),
                pl.sum("free_throws_attempted").alias("fta"),
                pl.sum("offensive_rebounds").alias("orb"),
                pl.sum("turnovers").alias("to")
            ])
            .with_columns([
                (
                    pl.col("fga") + 
                    0.475 * pl.col("fta") - 
                    pl.col("orb") + 
                    pl.col("to")
                ).alias("total_possessions")
            ])
            .with_columns([
                (pl.col("total_possessions") / pl.col("games_played")).alias("possessions")
            ])
        )
        
        # Drop intermediate columns
        result = result.drop([
            "games_played", "fga", "fta", "orb", "to", "total_possessions"
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