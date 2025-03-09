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

    def test_required_data(self) -> None:
        """Test that the feature reports its required data sources."""
        feature = HomeCourtAdvantage()
        required_data = feature.get_required_data()
        assert "team_box" in required_data

    def test_calculation_with_mock_data(self, mock_data_dict) -> None:
        """Test the feature calculates correctly with mock data."""
        # Add required columns if not present
        if "team_box" in mock_data_dict:
            columns_to_add = []
            team_box = mock_data_dict["team_box"]
            
            if "venue_type" not in team_box.columns:
                columns_to_add.append(pl.lit("home").alias("venue_type"))
                
            if "points" not in team_box.columns:
                columns_to_add.append(pl.lit(80).alias("points"))
                
            if "opponent_points" not in team_box.columns:
                columns_to_add.append(pl.lit(70).alias("opponent_points"))
                
            if columns_to_add:
                mock_data_dict["team_box"] = team_box.with_columns(columns_to_add)
            
        feature = HomeCourtAdvantage(min_home_games=1, min_away_games=1)
        result = feature.calculate(mock_data_dict)
        
        # Check result structure
        assert isinstance(result, pl.DataFrame)
        assert "team_id" in result.columns
        assert "season" in result.columns
        assert "home_court_advantage" in result.columns
        
        # Validate the feature output
        validate_feature_output(
            result, 
            "home_court_advantage",
            min_val=-60.0,  # Home advantage could be negative (worse at home)
            max_val=60.0,   # Increased maximum to accommodate mock data range
        )
        
    def test_calculation_logic(self) -> None:
        """Test that the calculation logic is correct by using a simplified dataset."""
        # Create a simplified test case with two teams, each with home and away games
        test_data = pl.DataFrame([
            # Team A - Home games (scores more at home)
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "home", "points": 80, "opponent_points": 70
            },
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "home", "points": 85, "opponent_points": 75
            },
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "home", "points": 90, "opponent_points": 80
            },
            
            # Team A - Away games
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "away", "points": 70, "opponent_points": 75
            },
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "away", "points": 75, "opponent_points": 80
            },
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "away", "points": 80, "opponent_points": 85
            },
            
            # Team B - Home games (scores less at home)
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "home", "points": 65, "opponent_points": 70
            },
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "home", "points": 70, "opponent_points": 75
            },
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "home", "points": 75, "opponent_points": 80
            },
            
            # Team B - Away games
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "away", "points": 80, "opponent_points": 75
            },
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "away", "points": 85, "opponent_points": 80
            },
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "away", "points": 90, "opponent_points": 85
            },
        ])
        
        feature = HomeCourtAdvantage(min_home_games=1, min_away_games=1)
        result = feature.calculate({"team_box": test_data})
        
        # Team A's home court advantage calculation:
        # Home point diff: (80-70 + 85-75 + 90-80) / 3 = 10
        # Away point diff: (70-75 + 75-80 + 80-85) / 3 = -5
        # Home court advantage: 10 - (-5) = 15
        
        # Team B's home court advantage calculation:
        # Home point diff: (65-70 + 70-75 + 75-80) / 3 = -5
        # Away point diff: (80-75 + 85-80 + 90-85) / 3 = 5
        # Home court advantage: -5 - 5 = -10
        
        # Get home court advantage for Team A
        team_a_hca = result.filter(pl.col("team_id") == 1)["home_court_advantage"][0]
        assert abs(team_a_hca - 15.0) < 0.001, f"Expected Team A HCA to be ~15.0, got {team_a_hca}"
        
        # Get home court advantage for Team B
        team_b_hca = result.filter(pl.col("team_id") == 2)["home_court_advantage"][0]
        assert abs(team_b_hca - (-10.0)) < 0.001, f"Expected Team B HCA to be ~-10.0, got {team_b_hca}"

    def test_handles_missing_required_columns(self) -> None:
        """Test that the feature handles missing required columns."""
        feature = HomeCourtAdvantage()
        
        # Create data missing required columns
        test_data = pl.DataFrame([
            {"team_id": 1, "team_name": "Team A", "season": 2023, "points": 80},  # Missing venue_type
        ])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": test_data})
            
        # Create data missing score columns
        test_data = pl.DataFrame([
            {"team_id": 1, "team_name": "Team A", "season": 2023, "venue_type": "home"},  # Missing points
        ])
        
        # Should raise a ValueError
        with pytest.raises(ValueError):
            feature.calculate({"team_box": test_data})

    def test_handles_insufficient_games(self) -> None:
        """Test that the feature handles teams with insufficient games correctly."""
        # Teams need both home and away games to calculate home court advantage
        test_data = pl.DataFrame([
            # Team A has only home games
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "home", "points": 80, "opponent_points": 70
            },
            {
                "team_id": 1, "team_name": "Team A", "season": 2023, 
                "venue_type": "home", "points": 85, "opponent_points": 75
            },
            
            # Team B has only away games
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "away", "points": 80, "opponent_points": 75
            },
            {
                "team_id": 2, "team_name": "Team B", "season": 2023, 
                "venue_type": "away", "points": 85, "opponent_points": 80
            },
            
            # Team C has both home and away games, but not enough of each
            {
                "team_id": 3, "team_name": "Team C", "season": 2023, 
                "venue_type": "home", "points": 80, "opponent_points": 70
            },
            {
                "team_id": 3, "team_name": "Team C", "season": 2023, 
                "venue_type": "away", "points": 75, "opponent_points": 80
            },
        ])
        
        feature = HomeCourtAdvantage(min_home_games=2, min_away_games=2)
        result = feature.calculate({"team_box": test_data})
        
        # Teams with insufficient games in either location should not be included
        assert result.filter(pl.col("team_id") == 1).height == 0
        assert result.filter(pl.col("team_id") == 2).height == 0
        assert result.filter(pl.col("team_id") == 3).height == 0 