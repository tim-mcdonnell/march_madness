"""Test fixtures for feature tests."""


import numpy as np
import polars as pl
import pytest


@pytest.fixture
def mock_team_box_data() -> pl.DataFrame:
    """Generate mock team box score data for testing features."""
    # Create 10 teams, each with 5 games
    n_teams = 10
    n_games_per_team = 5
    n_teams * n_games_per_team
    
    # Generate team IDs and names
    team_ids = list(range(1, n_teams + 1))
    team_names = [f"Team {i}" for i in team_ids]
    
    # Generate game IDs (unique for each game)
    game_ids = list(range(1, (n_teams * n_games_per_team // 2) + 1))
    
    # Create rows for each team's games
    rows = []
    for i, team_id in enumerate(team_ids):
        team_name = team_names[i]
        team_display_name = f"{team_name} University"
        
        # Each team plays 5 games
        for j in range(n_games_per_team):
            game_idx = (i * n_games_per_team + j) // 2
            game_id = game_ids[game_idx]
            
            # Determine opponent
            opponent_id = (team_id % n_teams) + 1
            
            # Add random performance metrics with realistic ranges
            points = np.random.randint(50, 100)
            opponent_points = np.random.randint(50, 100)
            
            fg_attempted = np.random.randint(50, 80)
            fg_made = np.random.randint(20, min(50, fg_attempted))
            
            tpa = np.random.randint(15, 35)
            tpm = np.random.randint(5, min(20, tpa))
            
            fta = np.random.randint(10, 30)
            ftm = np.random.randint(5, min(25, fta))
            
            orb = np.random.randint(5, 15)
            drb = np.random.randint(15, 30)
            
            assists = np.random.randint(10, 25)
            turnovers = np.random.randint(5, 20)
            steals = np.random.randint(3, 10)
            blocks = np.random.randint(1, 8)
            
            # Create a row for this game
            row = {
                "game_id": game_id,
                "team_id": team_id,
                "team_name": team_name,
                "team_display_name": team_display_name,
                "opponent_id": opponent_id,
                "season": 2023,
                "game_date": f"2023-{1+j:02d}-{1+i:02d}",  # Different dates for chronological ordering
                "venue_type": "home" if j % 2 == 0 else "away",
                "points": points,
                "opponent_points": opponent_points,
                "field_goals_attempted": fg_attempted,
                "field_goals_made": fg_made,
                "three_point_field_goals_attempted": tpa,
                "three_point_field_goals_made": tpm,
                "free_throws_attempted": fta,
                "free_throws_made": ftm,
                "offensive_rebounds": orb,
                "defensive_rebounds": drb,
                "total_rebounds": orb + drb,
                "assists": assists,
                "turnovers": turnovers,
                "steals": steals,
                "blocks": blocks
            }
            rows.append(row)
    
    return pl.DataFrame(rows)


@pytest.fixture
def mock_data_dict(mock_team_box_data) -> dict[str, pl.DataFrame]:
    """Generate a dictionary of mock data for testing features."""
    return {"team_box": mock_team_box_data} 