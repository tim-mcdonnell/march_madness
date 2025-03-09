"""Assist-to-Turnover Ratio implementation.

This module implements the Assist-to-Turnover Ratio feature, which measures
the ratio of assists to turnovers for a team.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class AssistToTurnoverRatio(BaseFeature):
    """Assist-to-Turnover Ratio feature.
    
    Assist-to-Turnover Ratio measures a team's ball handling efficiency by comparing
    assists to turnovers. A higher ratio indicates more efficient ball movement and 
    better ball security.
    
    Formula: Assists / Turnovers
    """
    
    id = "P07"
    name = "Assist-to-Turnover Ratio"
    category = "possession"
    description = "Team's ratio of assists to turnovers"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Assist-to-Turnover Ratio.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and assist_turnover_ratio columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Assist-to-Turnover Ratio calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "assists", "turnovers", "season"
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
            
        # Calculate Assist-to-Turnover Ratio
        result = (
            team_box
            .group_by(group_cols)
            .agg([
                pl.sum("assists").alias("total_assists"),
                pl.sum("turnovers").alias("total_turnovers")
            ])
            .filter(pl.col("total_turnovers") > 0)  # Avoid division by zero
            .with_columns([
                (pl.col("total_assists") / pl.col("total_turnovers")).alias("assist_turnover_ratio")
            ])
        )
        
        # Drop intermediate columns
        result = result.drop(["total_assists", "total_turnovers"])
        
        # Handle case where team_display_name is missing
        if has_display_name:
            result = result.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 