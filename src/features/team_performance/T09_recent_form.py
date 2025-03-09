"""Recent Form implementation.

This module implements the Recent Form feature, which measures
the performance trend of a team over its most recent games.
"""

import logging

import numpy as np
import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class RecentForm(BaseFeature):
    """Recent Form feature.
    
    Recent Form measures a team's performance trend over its most recent games,
    with more recent games weighted more heavily. This provides insight into
    whether a team is improving, declining, or maintaining its performance level.
    
    The feature uses an exponentially weighted average of point differentials,
    with a default window size of 5 games and a decay factor of 0.7.
    """
    
    id = "T09"
    name = "Recent Form"
    category = "team_performance"
    description = "Performance trend over the last N games (weighted recency)"
    
    def __init__(self, window_size: int = 5, decay_factor: float = 0.7) -> None:
        """Initialize the feature.
        
        Args:
            window_size: Number of recent games to consider.
            decay_factor: Weight decay factor for older games (0-1).
                Higher values give more weight to recent games.
        """
        super().__init__()
        self.window_size = window_size
        self.decay_factor = decay_factor
        
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["team_box"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Recent Form.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "team_box" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, and recent_form columns.
        """
        # Get the team_box DataFrame
        if isinstance(data, dict):
            if "team_box" not in data:
                raise ValueError("team_box data is required for Recent Form calculation")
            team_box = data["team_box"]
        else:
            team_box = data
            
        # Verify required columns are present
        required_cols = [
            "team_id", "team_name", "points", "opponent_points", 
            "season", "game_date", "game_id"
        ]
        
        missing_cols = [col for col in required_cols if col not in team_box.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Check for team_display_name column
        has_display_name = "team_display_name" in team_box.columns
        
        # Calculate point differential for each game
        with_diff = team_box.with_columns([
            (pl.col("points") - pl.col("opponent_points")).alias("point_differential")
        ])
        
        # Sort by team_id, season, and game_date to ensure chronological order
        sorted_data = with_diff.sort(["team_id", "season", "game_date"])
        
        # Group by team and season
        group_cols = ["team_id", "team_name", "season"]
        if has_display_name:
            group_cols.append("team_display_name")
        
        # Function to calculate exponentially weighted average over last N games
        def calc_recent_form(group_df: pl.DataFrame) -> float | None:
            # Convert to pandas for windowing operations (more flexible than polars for this case)
            pd_df = group_df.to_pandas()
            
            # If we have fewer games than window_size, use all available games
            n_games = len(pd_df)
            window = min(self.window_size, n_games)
            
            if n_games < 2:
                # Need at least 2 games to compute a trend
                return None
            
            # Calculate weights based on recency
            weights = np.power(self.decay_factor, np.arange(window-1, -1, -1))
            weights = weights / weights.sum()  # Normalize weights
            
            # Get point differentials from most recent games
            recent_diffs = pd_df["point_differential"].values[-window:]
            
            # Calculate weighted average
            return np.sum(recent_diffs * weights)
        
        # Apply the calculation to each group
        result_data = []
        for group_key, group_df in sorted_data.group_by(group_cols):
            recent_form = calc_recent_form(group_df)
            
            if recent_form is not None:
                # Create a row for this team's recent form
                row = {}
                
                # Add the group keys to the row
                if isinstance(group_key, tuple):
                    for i, col in enumerate(group_cols):
                        row[col] = group_key[i]
                else:
                    row[group_cols[0]] = group_key
                
                row["recent_form"] = recent_form
                result_data.append(row)
        
        # Create DataFrame from results
        if not result_data:
            # If no teams have sufficient games, return empty DataFrame with correct schema
            schema = {"team_id": pl.Int64, "team_name": pl.Utf8, "season": pl.Int64, 
                     "team_location": pl.Utf8, "recent_form": pl.Float64}
            return pl.DataFrame(schema=schema)
        
        result = pl.DataFrame(result_data)
        
        # Handle case where team_display_name is missing
        if has_display_name:
            try:
                result = result.rename({"team_display_name": "team_location"})
            except Exception as e:
                logger.warning(f"Could not rename team_display_name: {e}")
        
        # If team_location doesn't exist yet, create it from team_name
        if "team_location" not in result.columns:
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 