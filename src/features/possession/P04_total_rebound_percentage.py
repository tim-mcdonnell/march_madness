"""Total Rebound Percentage implementation.

This module implements the Total Rebound Percentage feature, which measures
the overall rebounding efficiency of a team.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature
from src.features.possession.P02_offensive_rebound_percentage import OffensiveReboundPercentage
from src.features.possession.P03_defensive_rebound_percentage import DefensiveReboundPercentage

logger = logging.getLogger(__name__)


class TotalReboundPercentage(BaseFeature):
    """Total Rebound Percentage feature.
    
    Total Rebound Percentage measures a team's overall rebounding efficiency,
    combining both offensive and defensive rebounding.
    
    Formula: (ORB + DRB) / (ORB + DRB + Opponent ORB + Opponent DRB)
    
    Alternatively: (ORB% + DRB%) / 2  (weighted by opportunities)
    """
    
    id = "P04"
    name = "Total Rebound Percentage"
    category = "possession"
    description = "Overall rebounding efficiency"
    
    def __init__(
        self, 
        offensive_rebound_pct_feature: OffensiveReboundPercentage | None = None,
        defensive_rebound_pct_feature: DefensiveReboundPercentage | None = None
    ) -> None:
        """Initialize the feature.
        
        Args:
            offensive_rebound_pct_feature: An instance of the OffensiveReboundPercentage feature.
                If not provided, a new one will be created.
            defensive_rebound_pct_feature: An instance of the DefensiveReboundPercentage feature.
                If not provided, a new one will be created.
        """
        super().__init__()
        self._offensive_rebound_pct_feature = offensive_rebound_pct_feature or OffensiveReboundPercentage()
        self._defensive_rebound_pct_feature = defensive_rebound_pct_feature or DefensiveReboundPercentage()
    
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
        return [
            self._offensive_rebound_pct_feature,
            self._defensive_rebound_pct_feature
        ]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Total Rebound Percentage.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and total_rebound_pct columns.
        """
        # Calculate offensive and defensive rebound percentages
        orb_pct_df = self._offensive_rebound_pct_feature.calculate(data)
        drb_pct_df = self._defensive_rebound_pct_feature.calculate(data)
        
        # Join the two DataFrames
        join_cols = ["team_id", "team_name", "team_location", "season"]
        result = orb_pct_df.join(
            drb_pct_df,
            on=join_cols,
            how="inner"
        )
        
        # Calculate total rebound percentage (weighted equally)
        result = result.with_columns([
            (
                (pl.col("offensive_rebound_pct") + pl.col("defensive_rebound_pct")) / 2
            ).alias("total_rebound_pct")
        ])
        
        # Drop intermediate columns
        return result.drop(["offensive_rebound_pct", "defensive_rebound_pct"])
        
