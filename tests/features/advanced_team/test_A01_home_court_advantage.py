"""Tests for Home Court Advantage feature."""

import polars as pl
import pytest

from src.features.advanced_team.A06_home_court_advantage import HomeCourtAdvantage
from tests.features.test_utils import validate_feature_output


class TestHomeCourtAdvantage:
    """Tests for the Home Court Advantage feature."""

    def test_instantiation(self) -> None:
        """Test that the feature can be instantiated correctly."""
        feature = HomeCourtAdvantage()
        assert feature.id == "A06"
        assert feature.name == "Home Court Advantage"
        assert feature.category == "advanced_team"
        assert feature.description is not None
        
        # Test with custom parameters
        feature = HomeCourtAdvantage(min_home_games=3, min_away_games=3)
        assert feature.min_home_games == 3
        assert feature.min_away_games == 3

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = HomeCourtAdvantage()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        feature = HomeCourtAdvantage(min_home_games=1, min_away_games=1)  # Lower minimum for test data
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "team_name" in result.columns
        assert "team_location" in result.columns
        assert "season" in result.columns
        assert "home_court_advantage" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "home_court_advantage",
            min_val=-60.0,  # Reasonable lower bound for point differential
            max_val=50.0,   # Reasonable upper bound for point differential
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with two teams
        test_data = pl.DataFrame([
            # Team A - Home Games
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 80, "opponent_points": 70, "venue_type": "home"},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 85, "opponent_points": 75, "venue_type": "home"},
            
            # Team A - Away Games
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 70, "opponent_points": 75, "venue_type": "away"},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 65, "opponent_points": 70, "venue_type": "away"},
            
            # Team B - Home Games
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 90, "opponent_points": 70, "venue_type": "home"},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 85, "opponent_points": 65, "venue_type": "home"},
            
            # Team B - Away Games
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 75, "opponent_points": 80, "venue_type": "away"},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 70, "opponent_points": 75, "venue_type": "away"},
        ])
        
        feature = HomeCourtAdvantage(min_home_games=2, min_away_games=2)
        result = feature.calculate({"team_box": test_data})
        
        # Team A: 
        # Home point diff = (80-70 + 85-75)/2 = 10
        # Away point diff = (70-75 + 65-70)/2 = -5
        # Home court advantage = 10 - (-5) = 15
        
        # Team B:
        # Home point diff = (90-70 + 85-65)/2 = 20
        # Away point diff = (75-80 + 70-75)/2 = -5
        # Home court advantage = 20 - (-5) = 25
        
        # Get HCA for Team A
        team_a_hca = result.filter(pl.col("team_id") == 1)["home_court_advantage"][0]
        assert abs(team_a_hca - 15.0) < 0.001, f"Expected Team A HCA to be 15.0, got {team_a_hca}"
        
        # Get HCA for Team B
        team_b_hca = result.filter(pl.col("team_id") == 2)["home_court_advantage"][0]
        assert abs(team_b_hca - 25.0) < 0.001, f"Expected Team B HCA to be 25.0, got {team_b_hca}"

    def test_handles_missing_required_columns(self, mock_team_box_data) -> None:
        """Test that the feature handles missing required columns."""
        feature = HomeCourtAdvantage()
        
        # Create a copy with missing columns
        df_missing = mock_team_box_data.drop(["venue_type"])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": df_missing})
            
    def test_min_games_filter(self) -> None:
        """Test that the feature filters out teams with fewer than min_games."""
        # Create a test case with one team having fewer games
        test_data = pl.DataFrame([
            # Team A - 3 home games, 3 away games
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 80, "opponent_points": 70, "venue_type": "home"},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 85, "opponent_points": 75, "venue_type": "home"},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 90, "opponent_points": 80, "venue_type": "home"},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 70, "opponent_points": 75, "venue_type": "away"},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 65, "opponent_points": 70, "venue_type": "away"},
            {"team_id": 1, "team_name": "Team A", "team_display_name": "Team A Univ", "season": 2023, 
             "points": 75, "opponent_points": 80, "venue_type": "away"},
            
            # Team B - 2 home games, 1 away game (insufficient away games)
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 90, "opponent_points": 70, "venue_type": "home"},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 85, "opponent_points": 65, "venue_type": "home"},
            {"team_id": 2, "team_name": "Team B", "team_display_name": "Team B Univ", "season": 2023, 
             "points": 75, "opponent_points": 80, "venue_type": "away"},
        ])
        
        # Set min games requirements
        feature = HomeCourtAdvantage(min_home_games=2, min_away_games=2)
        result = feature.calculate({"team_box": test_data})
        
        # Only Team A should be in the results
        assert result.filter(pl.col("team_id") == 1).height == 1
        assert result.filter(pl.col("team_id") == 2).height == 0 