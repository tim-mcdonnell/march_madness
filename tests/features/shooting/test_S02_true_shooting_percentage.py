"""Tests for True Shooting Percentage feature."""

import pandas as pd
import polars as pl
import pytest

from src.features.shooting.S02_true_shooting_percentage import TrueShootingPercentage
from tests.features.test_utils import validate_feature_output


class TestTrueShootingPercentage:
    """Tests for the True Shooting Percentage feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = TrueShootingPercentage()
        assert feature.id == "S02"
        assert feature.name == "True Shooting Percentage"
        assert feature.category == "shooting"
        assert feature.description is not None

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = TrueShootingPercentage()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        # Add team_score column if it doesn't exist
        if "team_box" in mock_data_dict:
            team_box = mock_data_dict["team_box"]
            if "team_score" not in team_box.columns and "points" in team_box.columns:
                team_box = team_box.with_columns([
                    pl.col("points").alias("team_score")
                ])
                mock_data_dict["team_box"] = team_box
        
        feature = TrueShootingPercentage()
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_name" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "ts_pct" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "ts_pct", 
            min_val=0.0,  # TS% is between 0 and 1
            max_val=1.0,
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with two teams
        test_data = pl.DataFrame([
            # Team A
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "team_score": 80, "field_goals_attempted": 50, "free_throws_attempted": 20},
            
            # Team B
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "team_score": 60, "field_goals_attempted": 60, "free_throws_attempted": 10},
        ])
        
        feature = TrueShootingPercentage()
        result = feature.calculate({"team_box": test_data})
        
        # Team A: TS% = 80 / (2 * (50 + 0.44 * 20)) = 80 / (2 * (50 + 8.8)) = 80 / 117.6 = 0.68
        # Team B: TS% = 60 / (2 * (60 + 0.44 * 10)) = 60 / (2 * (60 + 4.4)) = 60 / 128.8 = 0.466
        
        # Get TS% for Team A
        team_a_ts = (
            result.filter(pl.col("team_id") == 1)["ts_pct"][0] 
            if not pd.isna(result.filter(pl.col("team_id") == 1)["ts_pct"][0]) 
            else float("nan")
        )
        
        # Should be around 0.68
        assert abs(team_a_ts - 0.68) < 0.01, (
            f"Expected Team A TS% to be ~0.68, got {team_a_ts}"
        )
        
        # Get TS% for Team B
        team_b_ts = result.filter(pl.col("team_id") == 2)["ts_pct"][0]
        assert abs(team_b_ts - 0.466) < 0.01, f"Expected Team B TS% to be ~0.466, got {team_b_ts}"

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        feature = TrueShootingPercentage()
        
        # Add team_score column if it doesn't exist
        if "team_score" not in mock_team_box_data.columns and "points" in mock_team_box_data.columns:
            mock_team_box_data = mock_team_box_data.with_columns([
                pl.col("points").alias("team_score")
            ])
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["free_throws_attempted"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing})

    def test_handles_zero_attempts(self) -> None:
        """Test that the feature handles teams with zero field goal attempts."""
        # Create a dataset with a team that has no field goal attempts
        test_data = pl.DataFrame([
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "field_goals_attempted": 0, "field_goals_made": 0, "free_throws_attempted": 0, "free_throws_made": 0,
             "team_score": 0},
        ])
        
        feature = TrueShootingPercentage()
        result = feature.calculate({"team_box": test_data})
        
        # Team with zero attempts should be included but may have a NaN value
        assert result.filter(pl.col("team_id") == 1).height == 1
        
        # The implementation may set TS% to NaN for zero attempted shots
        # Check if the result is either 0.0 or NaN (both are acceptable)
        team_a_ts = (
            result.filter(pl.col("team_id") == 1)["ts_pct"][0] 
            if not pd.isna(result.filter(pl.col("team_id") == 1)["ts_pct"][0]) 
            else float("nan")
        )
        
        # Should be 0.0 or NaN
        assert pd.isna(team_a_ts) or abs(team_a_ts - 0.0) < 0.001, (
            f"Expected Team A TS% to be 0.0 or NaN, got {team_a_ts}"
        ) 