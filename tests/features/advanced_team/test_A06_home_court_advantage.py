"""Tests for the Home Court Advantage feature."""

import polars as pl
import pytest

from src.features.advanced_team.A06_home_court_advantage import HomeCourtAdvantage


def create_test_data():
    """Create test data for Home Court Advantage calculation."""
    # Create team_box test data
    team_box_data = []
    
    # Team 1 - performs better at home
    for i in range(10):
        # Home games - winning by average of 10 points
        team_box_data.append({
            "game_id": 1000 + i,
            "team_id": 1,
            "team_name": "Team One",
            "team_display_name": "Team One University",
            "points": 80,
            "opponent_points": 70,
            "team_home_away": "home",
            "season": 2023
        })
        
        # Away games - losing by average of 5 points
        team_box_data.append({
            "game_id": 2000 + i,
            "team_id": 1,
            "team_name": "Team One",
            "team_display_name": "Team One University",
            "points": 70,
            "opponent_points": 75,
            "team_home_away": "away",
            "season": 2023
        })
    
    # Team 2 - performs better away
    for i in range(10):
        # Home games - winning by average of 5 points
        team_box_data.append({
            "game_id": 3000 + i,
            "team_id": 2,
            "team_name": "Team Two",
            "team_display_name": "Team Two University",
            "points": 75,
            "opponent_points": 70,
            "team_home_away": "home",
            "season": 2023
        })
        
        # Away games - winning by average of 10 points
        team_box_data.append({
            "game_id": 4000 + i,
            "team_id": 2,
            "team_name": "Team Two",
            "team_display_name": "Team Two University",
            "points": 85,
            "opponent_points": 75,
            "team_home_away": "away",
            "season": 2023
        })
    
    # Team 3 - not enough games
    for i in range(3):  # Only 3 home and away games
        # Home games
        team_box_data.append({
            "game_id": 5000 + i,
            "team_id": 3,
            "team_name": "Team Three",
            "team_display_name": "Team Three University",
            "points": 70,
            "opponent_points": 65,
            "team_home_away": "home",
            "season": 2023
        })
        
        # Away games
        team_box_data.append({
            "game_id": 6000 + i,
            "team_id": 3,
            "team_name": "Team Three",
            "team_display_name": "Team Three University",
            "points": 65,
            "opponent_points": 75,
            "team_home_away": "away",
            "season": 2023
        })
    
    # Create schedules test data with neutral site information
    schedules_data = []
    
    # Add some neutral site games for Team 1
    for i in range(5):
        schedules_data.append({
            "game_id": 7000 + i,
            "neutral_site": True,
            "home_id": 1,
            "away_id": 4,
            "season": 2023
        })
        
        # Add corresponding team_box entries
        team_box_data.append({
            "game_id": 7000 + i,
            "team_id": 1,
            "team_name": "Team One",
            "team_display_name": "Team One University",
            "points": 75,
            "opponent_points": 72,
            "team_home_away": "home",  # This would be incorrectly marked as home
            "season": 2023
        })
    
    return {
        "team_box": pl.DataFrame(team_box_data),
        "schedules": pl.DataFrame(schedules_data)
    }


def test_home_court_advantage_calculation():
    """Test the Home Court Advantage calculation."""
    # Create feature instance
    feature = HomeCourtAdvantage(min_home_games=5, min_away_games=5)
    
    # Get test data
    data = create_test_data()
    
    # Add venue_type column to test data to match implementation
    data["team_box"] = data["team_box"].with_columns([
        pl.col("team_home_away").alias("venue_type")
    ])
    
    # Calculate feature
    result = feature.calculate(data)
    
    # Verify shape - should have 2 teams since Team 3 doesn't have enough games
    assert result.height == 2
    
    # Get results for each team
    team_1_hca = result.filter(pl.col("team_id") == 1)["home_court_advantage"].item()
    team_2_hca = result.filter(pl.col("team_id") == 2)["home_court_advantage"].item()
    
    # Team 1 should have positive HCA (performs better at home)
    # HCA = (80-70) - (70-75) = 10 - (-5) = 15
    assert team_1_hca == 15.0
    
    # Team 2 should have negative HCA (performs better away)
    # HCA = (75-70) - (85-75) = 5 - 10 = -5
    assert team_2_hca == -5.0
    
    # Verify Team 3 is not in results
    assert result.filter(pl.col("team_id") == 3).height == 0


def test_home_court_advantage_with_schedules():
    """Test that the feature correctly uses schedules data for neutral sites."""
    # Create feature instance
    feature = HomeCourtAdvantage(min_home_games=5, min_away_games=5)
    
    # Get test data
    data = create_test_data()
    
    # Add venue_type column to test data to match implementation
    data["team_box"] = data["team_box"].with_columns([
        pl.col("team_home_away").alias("venue_type")
    ])
    
    # Calculate feature without schedules data first
    team_box_only = data["team_box"].clone()
    result_no_schedules = feature.calculate({"team_box": team_box_only})
    
    # Now calculate with schedules
    result_with_schedules = feature.calculate(data)
    
    # Get HCA for Team 1 from both results
    hca_no_schedules = result_no_schedules.filter(pl.col("team_id") == 1)["home_court_advantage"].item()
    hca_with_schedules = result_with_schedules.filter(pl.col("team_id") == 1)["home_court_advantage"].item()
    
    # HCA should be different when including schedules because some "home" games
    # will be correctly identified as neutral
    assert hca_no_schedules != hca_with_schedules


def test_missing_venue_type_column():
    """Test handling of column name differences."""
    # Create feature instance
    feature = HomeCourtAdvantage()
    
    # Get test data
    data = create_test_data()
    
    # Create a dataframe missing the venue_type column
    team_box = data["team_box"]
    
    # Should raise ValueError due to missing venue_type column
    with pytest.raises(ValueError, match="Missing required columns"):
        feature.calculate({"team_box": team_box}) 