"""Tests for the foundation feature builder."""

from datetime import date
from pathlib import Path

import polars as pl
import pytest

from src.features.builders.foundation import FoundationFeatureBuilder


@pytest.fixture
def sample_team_season_stats() -> pl.DataFrame:
    """Create a sample team season stats DataFrame for testing."""
    return pl.DataFrame({
        "team_id": [1, 2, 3, 4],
        "team_name": ["Team A", "Team B", "Team C", "Team D"],
        "team_display_name": ["Team A", "Team B", "Team C", "Team D"],
        "season": [2023, 2023, 2023, 2023],
        "games_played": [30, 28, 32, 29],
        "total_points": [2400, 2100, 2600, 2300],
        "points_per_game": [80.0, 75.0, 81.25, 79.31],
        "opponent_points": [2100, 2000, 2400, 2200],
        "opponent_points_per_game": [70.0, 71.43, 75.0, 75.86],
        "home_games": [15, 14, 16, 15],
        "away_games": [15, 14, 16, 14],
        "wins": [22, 18, 24, 20],
        "losses": [8, 10, 8, 9],
        "home_wins": [13, 12, 15, 13],
        "away_wins": [9, 6, 9, 7],
        "avg_point_differential": [10.0, 3.57, 6.25, 3.45],
        "win_percentage": [0.733, 0.643, 0.750, 0.690],
        "home_win_pct": [0.867, 0.857, 0.938, 0.867],
        "away_win_pct": [0.600, 0.429, 0.563, 0.500]
    })


@pytest.fixture
def sample_team_box() -> pl.DataFrame:
    """Create a sample team box score DataFrame for testing."""
    # Create a consistent set of data for 4 teams and multiple games
    team_ids = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]
    opponent_ids = [2, 3, 4, 1, 3, 4, 1, 2, 4, 1, 2, 3]
    game_ids = [101, 102, 103, 101, 104, 105, 102, 104, 106, 103, 105, 106]
    seasons = [2023] * 12
    
    # Game dates spread across a season
    game_dates = [
        date(2022, 11, 15), date(2022, 12, 5), date(2023, 1, 10),  # Team 1
        date(2022, 11, 15), date(2022, 12, 20), date(2023, 1, 25), # Team 2
        date(2022, 12, 5), date(2022, 12, 20), date(2023, 2, 10),  # Team 3
        date(2023, 1, 10), date(2023, 1, 25), date(2023, 2, 10)    # Team 4
    ]
    
    # Home vs away
    home_away = ["home", "away", "home", "away", "home", "away", 
                "home", "away", "home", "away", "home", "away"]
    
    # Team scores and opponent scores
    team_scores = [85, 78, 92, 70, 82, 65, 72, 75, 88, 85, 70, 80]
    opponent_scores = [70, 72, 85, 85, 75, 70, 78, 82, 80, 92, 65, 88]
    
    # Win/loss
    team_winners = [score_team > score_opp for score_team, score_opp 
                   in zip(team_scores, opponent_scores, strict=True)]
    
    # Field goal stats
    fga = [70, 65, 75, 65, 70, 60, 60, 65, 70, 75, 60, 65]
    fgm = [32, 30, 35, 28, 30, 25, 28, 32, 34, 35, 28, 32]
    
    # Three-point stats
    tpa = [25, 22, 28, 20, 25, 18, 18, 22, 25, 30, 20, 22]
    tpm = [10, 8, 12, 6, 9, 5, 7, 8, 10, 12, 8, 9]
    
    # Free throw stats
    fta = [22, 20, 25, 18, 22, 15, 16, 20, 22, 25, 15, 18]
    ftm = [18, 16, 20, 14, 18, 12, 12, 16, 18, 20, 12, 14]
    
    # Rebounding stats
    orb = [12, 10, 14, 8, 11, 7, 9, 12, 13, 13, 8, 11]
    drb = [28, 25, 30, 22, 26, 20, 24, 25, 28, 29, 22, 26]
    trb = [40, 35, 44, 30, 37, 27, 33, 37, 41, 42, 30, 37]
    
    # Assist/turnover stats
    ast = [20, 18, 24, 15, 19, 13, 16, 17, 21, 22, 15, 19]
    tov = [10, 12, 8, 14, 11, 9, 10, 10, 9, 8, 9, 10]
    
    # Defensive stats
    stl = [7, 6, 9, 5, 8, 4, 5, 6, 8, 8, 5, 7]
    blk = [5, 4, 6, 3, 5, 2, 3, 4, 5, 6, 3, 4]
    
    # Create DataFrame
    return pl.DataFrame({
        "game_id": game_ids,
        "team_id": team_ids,
        "opponent_team_id": opponent_ids,
        "season": seasons,
        "game_date": game_dates,
        "team_home_away": home_away,
        "team_score": team_scores,
        "opponent_team_score": opponent_scores,
        "team_winner": team_winners,
        "field_goals_attempted": fga,
        "field_goals_made": fgm,
        "three_point_field_goals_attempted": tpa,
        "three_point_field_goals_made": tpm,
        "free_throws_attempted": fta,
        "free_throws_made": ftm,
        "offensive_rebounds": orb,
        "defensive_rebounds": drb,
        "total_rebounds": trb,
        "assists": ast,
        "turnovers": tov,
        "steals": stl,
        "blocks": blk,
        # Add necessary fields for field goal percentages
        "field_goal_pct": [m/a for m, a in zip(fgm, fga, strict=True)],
        "three_point_field_goal_pct": [m/a for m, a in zip(tpm, tpa, strict=True)],
        "free_throw_pct": [m/a for m, a in zip(ftm, fta, strict=True)]
    })


@pytest.fixture
def sample_schedules() -> pl.DataFrame:
    """Create a sample schedules DataFrame with neutral site information."""
    game_ids = [101, 102, 103, 104, 105, 106]
    neutral_sites = [False, True, False, False, True, True]
    
    return pl.DataFrame({
        "game_id": game_ids,
        "neutral_site": neutral_sites
    })


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Create a temporary directory for test outputs."""
    return tmp_path / "features"


def test_foundation_feature_builder_init() -> None:
    """Test the initialization of the FoundationFeatureBuilder."""
    # Test with default config
    builder = FoundationFeatureBuilder()
    assert builder.name == "foundation"
    assert builder.recent_form_games == 10
    assert builder.output_file == "team_performance.parquet"
    
    # Test with custom config
    custom_config = {
        "recent_form_games": 5,
        "output_file": "custom_output.parquet"
    }
    builder = FoundationFeatureBuilder(custom_config)
    assert builder.recent_form_games == 5
    assert builder.output_file == "custom_output.parquet"


def test_calculate_shooting_metrics(sample_team_box) -> None:
    """Test the calculation of shooting metrics."""
    builder = FoundationFeatureBuilder()
    result = builder._calculate_shooting_metrics(sample_team_box)
    
    # Check the shape of the result
    assert result.shape[0] == 4  # 4 teams
    
    # Check that all expected columns are present
    expected_cols = ["team_id", "season", "efg_pct", "ts_pct", "three_point_rate", "ft_rate"]
    assert all(col in result.columns for col in expected_cols)
    
    # Check that metrics are calculated correctly for a sample team
    team_1_metrics = result.filter(pl.col("team_id") == 1)
    
    # Verify some metrics are in expected ranges
    assert 0.4 <= team_1_metrics["efg_pct"][0] <= 0.6  # Typical eFG% range
    assert 0.5 <= team_1_metrics["ts_pct"][0] <= 0.7   # Typical TS% range
    assert 0.2 <= team_1_metrics["three_point_rate"][0] <= 0.5  # Typical 3PT rate
    assert 0.2 <= team_1_metrics["ft_rate"][0] <= 0.5  # Typical FT rate


def test_calculate_possession_metrics(sample_team_box) -> None:
    """Test the calculation of possession metrics."""
    builder = FoundationFeatureBuilder()
    result = builder._calculate_possession_metrics(sample_team_box)
    
    # Check the shape of the result
    assert result.shape[0] == 4  # 4 teams
    
    # Check that all expected columns are present
    expected_cols = ["team_id", "season", "orb_pct", "drb_pct", "trb_pct", 
                     "ast_rate", "tov_pct", "ast_to_tov_ratio"]
    assert all(col in result.columns for col in expected_cols)
    
    # Check that metrics are calculated correctly for a sample team
    team_1_metrics = result.filter(pl.col("team_id") == 1)
    
    # Verify some metrics are in expected ranges
    assert 0.2 <= team_1_metrics["orb_pct"][0] <= 0.5  # Typical ORB% range
    assert 0.5 <= team_1_metrics["drb_pct"][0] <= 0.9  # Typical DRB% range
    assert 0.4 <= team_1_metrics["trb_pct"][0] <= 0.7  # Typical TRB% range
    assert 0.4 <= team_1_metrics["ast_rate"][0] <= 0.8  # Typical AST% range
    assert 0.1 <= team_1_metrics["tov_pct"][0] <= 0.3  # Typical TOV% range
    assert 1.0 <= team_1_metrics["ast_to_tov_ratio"][0] <= 3.0  # Typical A/TO ratio


def test_calculate_win_percentage_breakdowns(sample_team_box) -> None:
    """Test the calculation of win percentage breakdowns."""
    builder = FoundationFeatureBuilder()
    result = builder._calculate_win_percentage_breakdowns(sample_team_box)
    
    # Check the shape of the result
    assert result.shape[0] == 4  # 4 teams
    
    # Check that all expected columns are present
    expected_cols = ["team_id", "season", "home_win_pct_detailed", "away_win_pct_detailed",
                     "neutral_win_pct", "home_games_played", "away_games_played", 
                     "neutral_games_played"]
    assert all(col in result.columns for col in expected_cols)
    
    # Check for a specific team
    team_1 = result.filter(pl.col("team_id") == 1)
    
    # Calculate expected values from sample data
    home_games = sample_team_box.filter((pl.col("team_id") == 1) & (pl.col("team_home_away") == "home"))
    away_games = sample_team_box.filter((pl.col("team_id") == 1) & (pl.col("team_home_away") == "away"))
    
    # Calculate expected values
    home_wins = sum(home_games["team_winner"].to_list())
    home_games_count = len(home_games)
    away_wins = sum(away_games["team_winner"].to_list())
    away_games_count = len(away_games)
    
    expected_home_win_pct = home_wins / home_games_count if home_games_count > 0 else None
    expected_away_win_pct = away_wins / away_games_count if away_games_count > 0 else None
    
    # Assert matches with calculated values
    assert team_1["home_win_pct_detailed"][0] == expected_home_win_pct 
    assert team_1["away_win_pct_detailed"][0] == expected_away_win_pct
    assert team_1["home_games_played"][0] == home_games_count
    assert team_1["away_games_played"][0] == away_games_count


def test_calculate_form_metrics(sample_team_box) -> None:
    """Test the calculation of form metrics."""
    builder = FoundationFeatureBuilder({"recent_form_games": 2})
    result = builder._calculate_form_metrics(sample_team_box)
    
    # Check the shape of the result
    assert result.shape[0] == 4  # 4 teams
    
    # Check that all expected columns are present
    expected_cols = ["team_id", "season", "point_diff_stddev", "scoring_stddev",
                     "last_game_date", "total_games", "recent_point_diff", "recent_win_pct"]
    assert all(col in result.columns for col in expected_cols)
    
    # Check for a specific team
    team_1 = result.filter(pl.col("team_id") == 1)
    
    # Verify metrics are in reasonable ranges
    assert team_1["point_diff_stddev"][0] > 0  # Should have some variation
    assert team_1["total_games"][0] == 3  # Team 1 played 3 games
    
    # Recent form should be based on the most recent games
    # For team 1, the last two games were a loss and a win
    recent_games = sample_team_box.filter(pl.col("team_id") == 1).sort("game_date").tail(2)
    recent_point_diffs = [score - opp for score, opp in zip(recent_games["team_score"].to_list(), 
                                                           recent_games["opponent_team_score"].to_list(), strict=True)]
    recent_wins = recent_games["team_winner"].to_list()
    
    # The weighted average should be somewhere between the values but closer to the most recent
    assert min(recent_point_diffs) <= team_1["recent_point_diff"][0] <= max(recent_point_diffs)
    assert min(recent_wins) <= team_1["recent_win_pct"][0] <= max(recent_wins)


def test_calculate_home_court_advantage(sample_team_box) -> None:
    """Test the calculation of home court advantage metrics."""
    builder = FoundationFeatureBuilder()
    result = builder._calculate_home_court_advantage(sample_team_box)
    
    # Check the shape of the result
    assert result.shape[0] == 4  # 4 teams
    
    # Check that all expected columns are present
    expected_cols = ["team_id", "season", "home_court_advantage", "home_win_boost"]
    assert all(col in result.columns for col in expected_cols)
    
    # Check for a specific team
    team_1 = result.filter(pl.col("team_id") == 1)
    
    # Team 1 performs better at home, so advantage should be positive
    home_games = sample_team_box.filter((pl.col("team_id") == 1) & (pl.col("team_home_away") == "home"))
    away_games = sample_team_box.filter((pl.col("team_id") == 1) & (pl.col("team_home_away") == "away"))
    
    home_margins = [(score - opp) for score, opp in zip(home_games["team_score"].to_list(), 
                                                      home_games["opponent_team_score"].to_list(), strict=True)]
    away_margins = [(score - opp) for score, opp in zip(away_games["team_score"].to_list(), 
                                                      away_games["opponent_team_score"].to_list(), strict=True)]
    
    avg_home_margin = sum(home_margins) / len(home_margins) if home_margins else 0
    avg_away_margin = sum(away_margins) / len(away_margins) if away_margins else 0
    expected_advantage = avg_home_margin - avg_away_margin
    
    # Allow for small floating point differences
    assert abs(team_1["home_court_advantage"][0] - expected_advantage) < 0.01


def test_build_features(sample_team_season_stats, sample_team_box) -> None:
    """Test the complete feature building process."""
    builder = FoundationFeatureBuilder({"recent_form_games": 2})
    result = builder.build_features(sample_team_season_stats, sample_team_box)
    
    # Check the shape - should have all the original columns plus our new features
    assert result.shape[0] == 4  # 4 teams
    assert result.shape[1] > sample_team_season_stats.shape[1]  # More columns than original
    
    # Check that we have all the original columns
    original_cols = sample_team_season_stats.columns
    assert all(col in result.columns for col in original_cols)
    
    # Check that we have the new feature columns
    new_feature_cols = ["efg_pct", "ts_pct", "three_point_rate", "ft_rate",
                        "orb_pct", "drb_pct", "trb_pct", "ast_rate", "tov_pct",
                        "home_win_pct_detailed", "away_win_pct_detailed", "neutral_win_pct",
                        "point_diff_stddev", "recent_point_diff", "recent_win_pct",
                        "home_court_advantage", "home_win_boost"]
    assert all(col in result.columns for col in new_feature_cols)
    
    # Verify some key values for a specific team
    team_1 = result.filter(pl.col("team_id") == 1)
    assert team_1["team_name"][0] == "Team A"
    assert 0 <= team_1["efg_pct"][0] <= 1  # eFG% should be between 0 and 1
    assert team_1["games_played"][0] == 30  # From original data
    assert team_1["home_games_played"][0] == 2  # From new data


def test_save_features(sample_team_season_stats, sample_team_box, temp_output_dir) -> None:
    """Test saving features to a parquet file."""
    # Create the output directory
    temp_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate features
    builder = FoundationFeatureBuilder()
    features = builder.build_features(sample_team_season_stats, sample_team_box)
    
    # Save features
    output_path = builder.save_features(features, temp_output_dir, "test_features.parquet")
    
    # Verify the file exists
    assert output_path.exists()
    
    # Verify the file is a valid parquet file
    loaded_df = pl.read_parquet(output_path)
    
    # Verify it has the same shape and columns
    assert loaded_df.shape == features.shape
    assert set(loaded_df.columns) == set(features.columns) 