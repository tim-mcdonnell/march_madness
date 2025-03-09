"""Tests for Consistency Rating feature."""

import polars as pl
import pytest

from src.features.team_performance.T10_consistency_rating import ConsistencyRating
from tests.features.test_utils import validate_feature_output


class TestConsistencyRating:
    """Tests for the Consistency Rating feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = ConsistencyRating()
        assert feature.id == "T10"
        assert feature.name == "Consistency Rating"
        assert feature.category == "team_performance"
        assert feature.description is not None
        
        # Test with custom parameters
        feature = ConsistencyRating(min_games=3)
        assert feature.min_games == 3

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = ConsistencyRating()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        feature = ConsistencyRating(min_games=3)  # Lower minimum for test data
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_name" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "consistency_rating" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "consistency_rating", 
            min_val=0.0,  # Standard deviation is always non-negative
            max_val=50.0,  # Reasonable upper bound for point differential std
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with two teams
        test_data = pl.DataFrame([
            # Team A - consistent point differentials
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 80, "opponent_points": 70},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 80, "opponent_points": 70},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 80, "opponent_points": 70},
            
            # Team B - variable point differentials
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 70, "opponent_points": 60},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 90, "opponent_points": 70},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 80, "opponent_points": 90},
        ])
        
        feature = ConsistencyRating(min_games=3)
        result = feature.calculate({"team_box": test_data})
        
        # Team A: All point differentials are 10, so std = 0
        # Team B: Point differentials are [10, 20, -10], so std ≈ 15.28
        
        # Get consistency rating for Team A
        team_a_rating = result.filter(pl.col("team_id") == 1)["consistency_rating"][0]
        assert team_a_rating == 0.0, f"Expected Team A consistency rating to be 0.0, got {team_a_rating}"
        
        # Get consistency rating for Team B
        team_b_rating = result.filter(pl.col("team_id") == 2)["consistency_rating"][0]
        
        # Standard deviation of [10, 20, -10] is approximately 15.28
        expected_rating = 15.28
        assert abs(team_b_rating - expected_rating) < 0.1, \
            f"Expected Team B consistency rating to be ~{expected_rating}, got {team_b_rating}"

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        feature = ConsistencyRating()
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["opponent_points"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing})
            
    def test_min_games_filter(self) -> None:
        """Test that the feature filters out teams with fewer than min_games."""
        # Create a test case with one team having fewer games
        test_data = pl.DataFrame([
            # Team A - 5 games
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 80, "opponent_points": 70},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 75, "opponent_points": 65},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 90, "opponent_points": 80},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 85, "opponent_points": 75},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 70, "opponent_points": 65},
            
            # Team B - 3 games
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 70, "opponent_points": 60},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 75, "opponent_points": 70},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 80, "opponent_points": 75},
        ])
        
        # Set min_games to 4
        feature = ConsistencyRating(min_games=4)
        result = feature.calculate({"team_box": test_data})
        
        # Only Team A should be in the results
        assert result.filter(pl.col("team_id") == 1).height == 1
        assert result.filter(pl.col("team_id") == 2).height == 0 