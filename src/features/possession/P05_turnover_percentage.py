"""Turnover Percentage implementation.

This module implements the Turnover Percentage feature, which measures
the percentage of possessions that end in a turnover.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature
from src.features.possession.P01_possessions import Possessions

logger = logging.getLogger(__name__)


class TurnoverPercentage(BaseFeature):
    """Turnover Percentage feature.
    
    Turnover Percentage measures the percentage of possessions that end in a turnover.
    It provides insight into a team's ball security.
    
    Formula: (Turnovers / Possessions) * 100
    """
    
    id = "P05"
    name = "Turnover Percentage"
    category = "possession"
    description = "Turnovers per 100 possessions"
    
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
        """Calculate Turnover Percentage.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and turnover_pct columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Turnover Percentage calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "turnovers", "season"
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
            
        # Create aggregation expressions list
        agg_exprs = [
            pl.sum("field_goals_attempted").alias("total_fga"),
            pl.sum("free_throws_attempted").alias("total_fta"),
            pl.sum("turnovers").alias("total_turnovers"),
            pl.sum("offensive_rebounds").alias("total_orb"),
        ]
        
        # Add optional columns if they exist
        if "team_rebounds" in team_box.columns:
            agg_exprs.append(pl.sum("team_rebounds").alias("total_team_rebounds"))
        else:
            logger.warning("team_rebounds column not found, using 0 as placeholder")
            # Add a placeholder column filled with 0
            team_box = team_box.with_columns(pl.lit(0).alias("team_rebounds_placeholder"))
            agg_exprs.append(pl.sum("team_rebounds_placeholder").alias("total_team_rebounds"))
            
        if "opponent_defensive_rebounds" in team_box.columns:
            agg_exprs.append(pl.sum("opponent_defensive_rebounds").alias("total_opp_drb"))
        else:
            logger.warning("opponent_defensive_rebounds column not found, using 0 as placeholder")
            # Add a placeholder column filled with 0
            team_box = team_box.with_columns(pl.lit(0).alias("opp_drb_placeholder"))
            agg_exprs.append(pl.sum("opp_drb_placeholder").alias("total_opp_drb"))
        
        # Calculate possessions
        result = (
            team_box
            .group_by(group_cols)
            .agg(agg_exprs)
        )
        
        # Drop intermediate columns from possessions_df
        try:
            possessions_df = possessions_df.drop([
                "total_fga", "total_fta", "total_orb", 
                "total_team_rebounds", "total_opp_drb"
            ])
        except Exception as e:
            # If columns don't exist, that's okay
            logger.warning(f"Could not drop intermediate columns: {e}")
        
        # Handle case where team_display_name is missing in possessions_df
        if has_display_name:
            try:
                possessions_df = possessions_df.rename({"team_display_name": "team_location"})
            except Exception as e:
                logger.warning(f"Could not rename team_display_name: {e}")
                # If team_location already exists, we don't need to do anything
                if "team_location" not in possessions_df.columns:
                    possessions_df = possessions_df.with_columns([
                        pl.col("team_name").alias("team_location")
                    ])
        else:
            # Use team_name as team_location if team_display_name is missing
            if "team_location" not in possessions_df.columns:
                possessions_df = possessions_df.with_columns([
                    pl.col("team_name").alias("team_location")
                ])
        
        # Join possessions_df with result
        join_cols = ["team_id", "team_name", "season"]
        if "team_location" in result.columns and "team_location" in possessions_df.columns:
            join_cols.append("team_location")
            
        try:
            result = result.join(possessions_df, on=join_cols, how="inner")
        except Exception as e:
            logger.warning(f"Join failed: {e}")
            # Try a simpler join if the first one fails
            simple_join_cols = ["team_id", "team_name", "season"]
            result = result.join(possessions_df, on=simple_join_cols, how="inner")
        
        # Calculate turnovers per game
        result = result.with_columns([
            (pl.col("total_turnovers") / pl.col("possessions")).alias("turnovers_per_game")
        ])
        
        # Calculate turnover percentage (turnovers per 100 possessions)
        result = result.with_columns([
            ((pl.col("turnovers_per_game") / pl.col("possessions")) * 100).alias("turnover_pct")
        ])
        
        # Drop intermediate columns
        return result.drop(["turnovers_per_game", "possessions"])
        
