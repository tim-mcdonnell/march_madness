"""Tests for Effective Field Goal Percentage feature."""

import polars as pl
import pytest

from src.features.shooting.S01_effective_field_goal_percentage import EffectiveFieldGoalPercentage
from tests.features.test_utils import validate_feature_output


class TestEffectiveFieldGoalPercentage:
    """Tests for the Effective Field Goal Percentage feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = EffectiveFieldGoalPercentage()
        assert feature.id == "S01"
        assert feature.name == "Effective Field Goal Percentage"
        assert feature.category == "shooting"
        assert feature.description is not None

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = EffectiveFieldGoalPercentage()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        feature = EffectiveFieldGoalPercentage()
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "effective_field_goal_percentage" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "effective_field_goal_percentage", 
            min_val=0.0,  # eFG% is between 0 and 1
            max_val=1.0,
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with two teams
        test_data = pl.DataFrame([
            # Team A
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "field_goals_made": 10, "field_goals_attempted": 20, 
             "three_point_field_goals_made": 5, "three_point_field_goals_attempted": 10},
            
            # Team B
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "field_goals_made": 12, "field_goals_attempted": 30, 
             "three_point_field_goals_made": 2, "three_point_field_goals_attempted": 8},
        ])
        
        feature = EffectiveFieldGoalPercentage()
        result = feature.calculate({"team_box": test_data})
        
        # Team A: eFG% = (10 + 0.5 * 5) / 20 = 0.625
        # Team B: eFG% = (12 + 0.5 * 2) / 30 = 0.433
        
        # Get eFG% for Team A
        team_a_efg = result.filter(pl.col("team_id") == 1)["effective_field_goal_percentage"][0]
        assert abs(team_a_efg - 0.625) < 0.001, f"Expected Team A eFG% to be 0.625, got {team_a_efg}"
        
        # Get eFG% for Team B
        team_b_efg = result.filter(pl.col("team_id") == 2)["effective_field_goal_percentage"][0]
        assert abs(team_b_efg - 0.433) < 0.001, f"Expected Team B eFG% to be 0.433, got {team_b_efg}"

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        feature = EffectiveFieldGoalPercentage()
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["field_goals_attempted"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing})

    def test_handles_zero_attempts(self) -> None:
        """Test that the feature handles zero field goal attempts correctly."""
        # Create a dataset with a team that has zero field goal attempts
        test_data = pl.DataFrame([
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "field_goals_made": 0, "field_goals_attempted": 0, 
             "three_point_field_goals_made": 0, "three_point_field_goals_attempted": 0},
        ])
        
        feature = EffectiveFieldGoalPercentage()
        result = feature.calculate({"team_box": test_data})
        
        # Team with zero attempts should have an eFG% of 0.0
        team_data = result.filter(pl.col("team_id") == 1)
        assert team_data.height == 1
        assert team_data["effective_field_goal_percentage"][0] == 0.0 