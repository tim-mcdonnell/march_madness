"""True Shooting Percentage implementation.

This module implements the True Shooting Percentage feature, which measures
shooting efficiency inclusive of three-pointers and free throws.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class TrueShootingPercentage(BaseFeature):
    """True Shooting Percentage feature.
    
    True Shooting Percentage is a measure of shooting efficiency that takes into account
    field goals, 3-point field goals, and free throws.
    
    Formula: TS% = Points / (2 * (FGA + 0.44 * FTA))
    """
    
    id = "S02"
    name = "True Shooting Percentage"
    category = "shooting"
    description = "Shooting efficiency including free throws"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate True Shooting Percentage.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and ts_pct columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for True Shooting Percentage calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "field_goals_attempted", 
            "free_throws_attempted", "season"
        ]
        
        # Check for either team_score or points
        if "points" not in team_box.columns and "team_score" not in team_box.columns:
            raise ValueError("Either 'points' or 'team_score' column is required")
        
        # Determine which score column to use
        score_col = "points" if "points" in team_box.columns else "team_score"
        
        missing_cols = [col for col in required_cols if col not in team_box.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Check for team_display_name column
        has_display_name = "team_display_name" in team_box.columns
        
        # Group by team_id, team_name, and season
        group_cols = ["team_id", "team_name", "season"]
        if has_display_name:
            group_cols.append("team_display_name")
            
        # Calculate TS% by team and season
        result = (
            team_box
            .group_by(group_cols)
            .agg([
                pl.sum(score_col).alias("points"),
                pl.sum("field_goals_attempted").alias("fga"),
                pl.sum("free_throws_attempted").alias("fta")
            ])
            .with_columns([
                (pl.col("points") / (2 * (pl.col("fga") + 0.44 * pl.col("fta")))).alias("ts_pct")
            ])
        )
        
        # Drop intermediate columns
        result = result.drop(["points", "fga", "fta"])
        
        # Handle case where team_display_name is missing
        if has_display_name:
            result = result.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 