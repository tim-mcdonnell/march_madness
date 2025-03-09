"""Tests for Offensive Efficiency feature."""

import polars as pl
import pytest

from src.features.advanced_team.A01_offensive_efficiency import OffensiveEfficiency
from tests.features.test_utils import validate_feature_output


class TestOffensiveEfficiency:
    """Tests for the Offensive Efficiency feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = OffensiveEfficiency()
        assert feature.id == "A01"
        assert feature.name == "Offensive Efficiency"
        assert feature.category == "advanced_team"
        assert feature.description is not None
        
        # Test with custom parameters if applicable
        if hasattr(feature, 'min_games'):
            feature = OffensiveEfficiency(min_games=3)
            assert feature.min_games == 3

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = OffensiveEfficiency()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        # For this test, we may need to ensure mock_data_dict has necessary columns
        # If there's a min_games parameter, set it low for testing
        feature = OffensiveEfficiency()
        if hasattr(feature, 'min_games'):
            feature = OffensiveEfficiency(min_games=1)
            
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_name" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "offensive_efficiency" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "offensive_efficiency", 
            min_val=0.0,    # Offensive efficiency shouldn't be negative
            max_val=150.0,  # Reasonable upper bound for offensive efficiency
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with teams
        test_data = pl.DataFrame([
            # Team A
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 80, "possessions": 70, "field_goals_attempted": 60, "free_throws_attempted": 20,
             "offensive_rebounds": 10, "turnovers": 12},
            
            # Team B
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 60, "possessions": 80, "field_goals_attempted": 70, "free_throws_attempted": 15,
             "offensive_rebounds": 8, "turnovers": 15},
        ])
        
        feature = OffensiveEfficiency()
        result = feature.calculate({"team_box": test_data})
        
        # Team A: Offensive Efficiency = 80 / 70 * 100 = 114.29
        # Team B: Offensive Efficiency = 60 / 80 * 100 = 75.0
        
        # Get offensive efficiency for Team A
        team_a_oe = result.filter(pl.col("team_id") == 1)["offensive_efficiency"][0]
        assert abs(team_a_oe - 114.29) < 5.0, f"Expected Team A offensive efficiency to be ~114.29, got {team_a_oe}"
        
        # Get offensive efficiency for Team B
        team_b_oe = result.filter(pl.col("team_id") == 2)["offensive_efficiency"][0]
        assert abs(team_b_oe - 75.0) < 5.0, f"Expected Team B offensive efficiency to be ~75.0, got {team_b_oe}"

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        feature = OffensiveEfficiency()
        
        # Make sure the mock data has the required columns first
        required_cols = ["field_goals_attempted", "free_throws_attempted", "offensive_rebounds", "turnovers"]
        for col in required_cols:
            if col not in mock_team_box_data.columns:
                mock_team_box_data = mock_team_box_data.with_columns([
                    pl.lit(0).alias(col)
                ])
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["points"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing}) 