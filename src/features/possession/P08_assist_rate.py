"""Assist Rate implementation.

This module implements the Assist Rate feature, which measures
the percentage of field goals that are assisted.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class AssistRate(BaseFeature):
    """Assist Rate feature.
    
    Assist Rate measures the percentage of field goals that are assisted.
    It provides insight into a team's ball movement and team play.
    
    Formula: Assists / Field Goals Made
    """
    
    id = "P08"
    name = "Assist Rate"
    category = "possession"
    description = "Percentage of field goals that are assisted"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Assist Rate.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and assist_rate columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Assist Rate calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "assists", "field_goals_made", "season"
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
            
        # Calculate Assist Rate
        result = (
            team_box
            .group_by(group_cols)
            .agg([
                pl.sum("assists").alias("total_assists"),
                pl.sum("field_goals_made").alias("total_field_goals_made")
            ])
            .filter(pl.col("total_field_goals_made") > 0)  # Avoid division by zero
            .with_columns([
                (pl.col("total_assists") / pl.col("total_field_goals_made")).alias("assist_rate")
            ])
        )
        
        # Drop intermediate columns
        result = result.drop(["total_assists", "total_field_goals_made"])
        
        # Handle case where team_display_name is missing
        if has_display_name:
            result = result.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 