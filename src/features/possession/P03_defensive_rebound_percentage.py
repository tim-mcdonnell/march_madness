"""Defensive Rebound Percentage implementation.

This module implements the Defensive Rebound Percentage feature, which measures
the percentage of available defensive rebounds a team captures.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class DefensiveReboundPercentage(BaseFeature):
    """Defensive Rebound Percentage feature.
    
    Defensive Rebound Percentage measures the percentage of available defensive rebounds
    that a team captures. It provides insight into a team's ability to end opponent possessions
    after a missed shot.
    
    Formula: DRB / (DRB + Opponent ORB)
    """
    
    id = "P03"
    name = "Defensive Rebound Percentage"
    category = "possession"
    description = "Percentage of defensive rebounds captured"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Defensive Rebound Percentage.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and defensive_rebound_pct columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Defensive Rebound Percentage calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "game_id", "offensive_rebounds", 
            "defensive_rebounds", "season"
        ]
        
        missing_cols = [col for col in required_cols if col not in team_box.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Check for team_display_name column
        has_display_name = "team_display_name" in team_box.columns
        
        # Create a copy with renamed columns to prepare for self-join
        opponent_box = team_box.select([
            pl.col("game_id"),
            pl.col("team_id").alias("opponent_id"),
            pl.col("offensive_rebounds").alias("opponent_offensive_rebounds")
        ])
        
        # Join team data with opponent data by game_id
        joined_data = team_box.join(
            opponent_box,
            on="game_id",
            how="inner"
        ).filter(
            pl.col("team_id") != pl.col("opponent_id")
        )
        
        # Group by team_id, team_name, and season
        group_cols = ["team_id", "team_name", "season"]
        if has_display_name:
            group_cols.append("team_display_name")
            
        # Calculate Defensive Rebound Percentage
        result = (
            joined_data
            .group_by(group_cols)
            .agg([
                pl.sum("defensive_rebounds").alias("total_defensive_rebounds"),
                pl.sum("opponent_offensive_rebounds").alias("total_opponent_offensive_rebounds")
            ])
            .with_columns([
                (
                    pl.col("total_defensive_rebounds") / 
                    (pl.col("total_defensive_rebounds") + pl.col("total_opponent_offensive_rebounds"))
                ).alias("defensive_rebound_pct")
            ])
        )
        
        # Drop intermediate columns
        result = result.drop(["total_defensive_rebounds", "total_opponent_offensive_rebounds"])
        
        # Handle case where team_display_name is missing
        if has_display_name:
            result = result.rename({"team_display_name": "team_location"})
        else:
            # Use team_name as team_location if team_display_name is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 