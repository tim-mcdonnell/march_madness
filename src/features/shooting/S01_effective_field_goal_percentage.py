"""Effective Field Goal Percentage (eFG%) implementation.

This module implements the Effective Field Goal Percentage feature,
which adjusts field goal percentage to account for the higher value
of three-point shots.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class EffectiveFieldGoalPercentage(BaseFeature):
    """Effective Field Goal Percentage (eFG%) feature.
    
    eFG% adjusts for the fact that three-point field goals are worth more
    than two-point field goals by giving 50% more credit for made three-pointers.
    
    Formula: eFG% = (FGM + 0.5 * 3PM) / FGA
    
    where:
    - FGM: Field Goals Made
    - 3PM: Three-Point Field Goals Made
    - FGA: Field Goals Attempted
    """
    
    id = "S01"
    name = "Effective Field Goal Percentage"
    category = "shooting"
    description = "Field goal percentage adjusted for three-pointers"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Effective Field Goal Percentage.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and
            effective_field_goal_percentage columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for eFG% calculation")
            team_box = data["team_box"]
        else:
            team_box = data
        
        # Verify required columns are present
        required_cols = [
            "team_id", "field_goals_made", "three_point_field_goals_made", 
            "field_goals_attempted", "season"
        ]
        
        missing_cols = [col for col in required_cols if col not in team_box.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure we have team name column(s)
        has_location = "team_location" in team_box.columns
        has_name = "team_name" in team_box.columns
        
        # Determine which columns to use for grouping
        group_cols = ["team_id", "season"]
        if has_location:
            group_cols.append("team_location")
        if has_name:
            group_cols.append("team_name")
        
        # Calculate eFG% by team and season
        result = (
            team_box
            .group_by(group_cols)
            .agg([
                pl.col("field_goals_made").sum().alias("total_field_goals_made"),
                pl.col("three_point_field_goals_made").sum().alias("total_three_point_field_goals_made"),
                pl.col("field_goals_attempted").sum().alias("total_field_goals_attempted"),
            ])
        )
        
        # Add the eFG% column using the formula
        result = result.with_columns([
            (
                (pl.col("total_field_goals_made") + 0.5 * pl.col("total_three_point_field_goals_made")) / 
                pl.when(pl.col("total_field_goals_attempted") > 0)
                .then(pl.col("total_field_goals_attempted"))
                .otherwise(1.0)  # Avoid division by zero
            ).alias("effective_field_goal_percentage")
        ])
        
        # Drop the intermediate columns
        result = result.drop([
            "total_field_goals_made", 
            "total_three_point_field_goals_made", 
            "total_field_goals_attempted"
        ])
        
        # Handle case where team_location or team_name is missing
        if not has_location and "team_name" in team_box.columns:
            # Use team_name as team_location if team_location is missing
            result = result.rename({"team_name": "team_location"})
            has_location = True
        
        if not has_name and "team_location" in team_box.columns:
            # Use team_location as team_name if team_name is missing
            result = result.rename({"team_location": "team_name"})
            has_name = True
        
        # Ensure we have both team_location and team_name
        if not has_location:
            # Add a placeholder team_location column
            result = result.with_columns([
                pl.lit("Unknown").alias("team_location")
            ])
        
        if not has_name:
            # Add a placeholder team_name column
            result = result.with_columns([
                pl.lit("Unknown").alias("team_name")
            ])
        
        return result 