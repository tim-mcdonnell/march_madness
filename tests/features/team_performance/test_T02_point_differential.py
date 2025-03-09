"""Tests for Point Differential feature."""

import polars as pl
import pytest

from src.features.team_performance.T02_point_differential import PointDifferential
from tests.features.test_utils import validate_feature_output


class TestPointDifferential:
    """Tests for the Point Differential feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = PointDifferential()
        assert feature.id == "T02"
        assert feature.name == "Point Differential"
        assert feature.category == "team_performance"
        assert feature.description is not None

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = PointDifferential()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        feature = PointDifferential()
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_name" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "point_differential" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "point_differential", 
            min_val=-50.0,  # Reasonable range for college basketball
            max_val=50.0,
            max_missing_pct=0.0  # Point differential should never have missing values
        )
        
    def test_calculation_logic(self, mock_team_box_data) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case
        test_data = pl.DataFrame([
            {"team_id": 1, "team_name": "Team A", "season": 2023, "points": 80, "opponent_points": 70},
            {"team_id": 1, "team_name": "Team A", "season": 2023, "points": 90, "opponent_points": 80},
            {"team_id": 2, "team_name": "Team B", "season": 2023, "points": 70, "opponent_points": 80},
            {"team_id": 2, "team_name": "Team B", "season": 2023, "points": 80, "opponent_points": 90},
        ])
        
        feature = PointDifferential()
        result = feature.calculate({"team_box": test_data})
        
        # Team A: (80-70 + 90-80) / 2 = 10
        # Team B: (70-80 + 80-90) / 2 = -10
        
        # Get point differential for Team A
        team_a_diff = result.filter(pl.col("team_id") == 1)["point_differential"][0]
        assert team_a_diff == 10.0, f"Expected Team A point differential to be 10.0, got {team_a_diff}"
        
        # Get point differential for Team B
        team_b_diff = result.filter(pl.col("team_id") == 2)["point_differential"][0]
        assert team_b_diff == -10.0, f"Expected Team B point differential to be -10.0, got {team_b_diff}"

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        feature = PointDifferential()
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["opponent_points"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing}) 