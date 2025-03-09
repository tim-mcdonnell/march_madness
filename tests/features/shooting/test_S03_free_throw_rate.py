"""Tests for Free Throw Rate feature."""

import polars as pl
import pytest

from src.features.shooting.S04_free_throw_rate import FreeThrowRate
from tests.features.test_utils import validate_feature_output


class TestFreeThrowRate:
    """Tests for the Free Throw Rate feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = FreeThrowRate()
        assert feature.id == "S04"
        assert feature.name == "Free Throw Rate"
        assert feature.category == "shooting"
        assert feature.description is not None

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = FreeThrowRate()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        feature = FreeThrowRate()
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_name" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "free_throw_rate" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "free_throw_rate", 
            min_val=0.0,  # FTR can range from 0 to potentially high values
            # No strict max value as it could be high for teams that get to the line often
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with two teams
        test_data = pl.DataFrame([
            # Team A
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "free_throws_attempted": 30, "field_goals_attempted": 60},
            
            # Team B
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "free_throws_attempted": 10, "field_goals_attempted": 50},
        ])
        
        feature = FreeThrowRate()
        result = feature.calculate({"team_box": test_data})
        
        # Team A: FTR = 30 / 60 = 0.5
        # Team B: FTR = 10 / 50 = 0.2
        
        # Get FTR for Team A
        team_a_ftr = result.filter(pl.col("team_id") == 1)["free_throw_rate"][0]
        assert abs(team_a_ftr - 0.5) < 0.001, f"Expected Team A FTR to be 0.5, got {team_a_ftr}"
        
        # Get FTR for Team B
        team_b_ftr = result.filter(pl.col("team_id") == 2)["free_throw_rate"][0]
        assert abs(team_b_ftr - 0.2) < 0.001, f"Expected Team B FTR to be 0.2, got {team_b_ftr}"

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        feature = FreeThrowRate()
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["free_throws_attempted"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing})

    def test_handles_zero_field_goal_attempts(self) -> None:
        """Test that the feature handles zero field goal attempts correctly."""
        # Create a dataset with a team that has zero field goal attempts
        test_data = pl.DataFrame([
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "free_throws_attempted": 10, "field_goals_attempted": 0},
        ])
        
        feature = FreeThrowRate()
        result = feature.calculate({"team_box": test_data})
        
        # Team with zero field goal attempts should be filtered out
        assert result.filter(pl.col("team_id") == 1).height == 0 