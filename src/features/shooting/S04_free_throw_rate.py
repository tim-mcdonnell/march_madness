"""Free Throw Rate implementation.

This module implements the Free Throw Rate feature, which measures
the ratio of free throw attempts to field goal attempts.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class FreeThrowRate(BaseFeature):
    """Free Throw Rate feature.
    
    Free Throw Rate measures how often a team gets to the free throw line
    relative to their field goal attempts.
    
    Formula: FTA / FGA
    """
    
    id = "S04"
    name = "Free Throw Rate"
    category = "shooting"
    description = "Free throw attempts relative to field goal attempts"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Free Throw Rate.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and free_throw_rate columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Free Throw Rate calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "free_throws_attempted", 
            "field_goals_attempted", "season"
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
            
        # Calculate Free Throw Rate
        result = (
            team_box
            .filter(pl.col("field_goals_attempted") > 0)
            .group_by(group_cols)
            .agg([
                pl.sum("field_goals_attempted").alias("fga"),
                pl.sum("free_throws_attempted").alias("fta")
            ])
            .with_columns([
                (pl.col("fta") / pl.col("fga")).alias("free_throw_rate")
            ])
        )
        
        # Drop intermediate columns
        result = result.drop(["fga", "fta"])
        
        # Handle case where team_display_name is missing
        if has_display_name:
            result = result.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 