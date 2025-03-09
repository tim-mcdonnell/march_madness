"""Win Percentage implementation.

This module implements the Win Percentage feature, which measures the
proportion of games won by a team.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class WinPercentage(BaseFeature):
    """Win Percentage feature.
    
    Win Percentage is the proportion of games won by a team.
    
    Formula: win_percentage = wins / (wins + losses)
    """
    
    id = "T01"
    name = "Win Percentage"
    category = "team_performance"
    description = "Proportion of games won by a team"
    
    def get_required_data(self) -> list[str]:
        """Get the required data sources for this feature.
        
        Returns:
            List of data source names required by this feature.
        """
        return ["schedules"]
    
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate Win Percentage.
        
        Args:
            data: Either a DataFrame or a dictionary of DataFrames.
                If a dictionary, should contain a "schedules" key.
        
        Returns:
            DataFrame with team_id, team_location, team_name, season, 
            win_percentage, home_win_percentage, away_win_percentage,
            and neutral_win_percentage columns.
        """
        # Get the schedules DataFrame
        if isinstance(data, dict):
            if "schedules" not in data:
                raise ValueError("schedules data is required for Win Percentage calculation")
            schedules = data["schedules"]
        else:
            schedules = data
        
        # Verify required columns are present
        required_cols = [
            "game_id", "season", "home_id", "home_name", "home_score", "away_id", 
            "away_name", "away_score", "neutral_site"
        ]
        
        missing_cols = [col for col in required_cols if col not in schedules.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Check for team_location column or equivalent (home_display_name, away_display_name)
        has_home_location = "home_display_name" in schedules.columns
        has_away_location = "away_display_name" in schedules.columns
        
        # Create home team results
        home_cols = [
            pl.col("home_id").alias("team_id"),
            pl.col("home_name").alias("team_name"),
            pl.col("season"),
            pl.col("neutral_site"),
            (pl.col("home_score") > pl.col("away_score")).alias("win"),
            pl.lit(1).alias("games"),
            pl.lit(1).alias("home_games"),
            pl.lit(0).alias("away_games"),
        ]
        
        # Add team_location if available
        if has_home_location:
            home_cols.append(pl.col("home_display_name").alias("team_location"))
        else:
            # Use team_name as location if display_name not available
            home_cols.append(pl.col("home_name").alias("team_location"))
            
        home_results = schedules.select(home_cols)
        
        # Create away team results
        away_cols = [
            pl.col("away_id").alias("team_id"),
            pl.col("away_name").alias("team_name"),
            pl.col("season"),
            pl.col("neutral_site"),
            (pl.col("away_score") > pl.col("home_score")).alias("win"),
            pl.lit(1).alias("games"),
            pl.lit(0).alias("home_games"),
            pl.lit(1).alias("away_games"),
        ]
        
        # Add team_location if available
        if has_away_location:
            away_cols.append(pl.col("away_display_name").alias("team_location"))
        else:
            # Use team_name as location if display_name not available
            away_cols.append(pl.col("away_name").alias("team_location"))
            
        away_results = schedules.select(away_cols)
        
        # Combine results
        all_results = pl.concat([home_results, away_results])
        
        # Calculate neutral site games
        all_results = all_results.with_columns([
            pl.col("neutral_site").cast(pl.Int64).alias("neutral_games")
        ])
        
        # Group by team_id, team_name, and season
        group_cols = ["team_id", "team_name", "season"]
        if has_home_location and has_away_location:
            group_cols.append("team_location")
        
        # Calculate win percentages
        result = (
            all_results
            .group_by(group_cols)
            .agg([
                pl.col("win").sum().alias("wins"),
                pl.col("games").sum().alias("total_games"),
                pl.col("home_games").sum().alias("home_games"),
                pl.col("away_games").sum().alias("away_games"),
                pl.col("neutral_games").sum().alias("neutral_games"),
                (pl.col("win") & (pl.col("home_games") == 1)).sum().alias("home_wins"),
                (pl.col("win") & (pl.col("away_games") == 1)).sum().alias("away_wins"),
                (pl.col("win") & (pl.col("neutral_games") == 1)).sum().alias("neutral_wins"),
            ])
        )
        
        # Calculate win percentages
        result = result.with_columns([
            (pl.col("wins") / pl.col("total_games")).alias("win_percentage"),
            (pl.col("home_wins") / 
             pl.when(pl.col("home_games") > 0)
             .then(pl.col("home_games"))
             .otherwise(1)).alias("home_win_percentage"),
            (pl.col("away_wins") / 
             pl.when(pl.col("away_games") > 0)
             .then(pl.col("away_games"))
             .otherwise(1)).alias("away_win_percentage"),
            (pl.col("neutral_wins") / 
             pl.when(pl.col("neutral_games") > 0)
             .then(pl.col("neutral_games"))
             .otherwise(1)).alias("neutral_win_percentage"),
        ])
        
        # Drop intermediate columns
        result = result.drop([
            "wins", "total_games", "home_games", "away_games", 
            "neutral_games", "home_wins", "away_wins", "neutral_wins"
        ])
        
        # Handle case where team_location is missing
        if "team_location" not in result.columns:
            # Use team_name as team_location if team_location is missing
            result = result.with_columns([
                pl.col("team_name").alias("team_location")
            ])
        
        return result 