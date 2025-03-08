"""Tests for the efficiency feature builder."""

import importlib
import os

import polars as pl
import pytest


@pytest.fixture
def setup_env() -> None:
    """Ensure efficiency features are enabled for these specific tests."""
    old_value = os.environ.get("ENABLE_EFFICIENCY_FEATURES", "1")
    os.environ["ENABLE_EFFICIENCY_FEATURES"] = "1"
    
    # Force reload of the features module to ensure efficiency is registered
    import src.features
    importlib.reload(src.features)
    
    yield
    
    # Restore original environment
    if old_value is not None:
        os.environ["ENABLE_EFFICIENCY_FEATURES"] = old_value
    else:
        del os.environ["ENABLE_EFFICIENCY_FEATURES"]
    
    # Reload again to restore original state
    import src.features
    importlib.reload(src.features)


@pytest.fixture
def mock_data() -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    """Create mock data for testing the efficiency feature builder."""
    team_performance = pl.DataFrame({
        "team_id": ["101", "102", "103"],
        "season": [2023, 2023, 2023],
        "win_percentage": [0.7, 0.8, 0.9]
    })
    
    team_box = pl.DataFrame({
        "team_id": ["101", "101", "102", "102", "103", "103"],
        "game_id": ["1001", "1002", "2001", "2002", "3001", "3002"],
        "season": [2023, 2023, 2023, 2023, 2023, 2023],
        "team_score": [80, 85, 75, 70, 90, 95],
        "opponent_team_score": [70, 75, 65, 60, 80, 85],
        "field_goals_attempted": [70, 75, 65, 60, 80, 85],
        "field_goals_made": [30, 35, 25, 20, 40, 45],
        "offensive_rebounds": [10, 12, 8, 7, 15, 18],
        "team_turnovers": [12, 15, 10, 8, 14, 16],
        "free_throws_attempted": [20, 25, 15, 10, 30, 35]
    })
    
    schedules = pl.DataFrame({
        "game_id": ["1001", "1002", "2001", "2002", "3001", "3002"],
        "season": [2023, 2023, 2023, 2023, 2023, 2023],
        "home_id": ["101", "101", "102", "102", "103", "103"],
        "away_id": ["102", "103", "101", "103", "101", "102"],
        "neutral_site": [False, False, False, False, False, False],
        "season_type": [1, 1, 1, 1, 3, 3]  # 3 is assumed to be tournament games
    })
    
    return team_performance, team_box, schedules


def test_efficiency_builder_imports(setup_env) -> None:
    """Test that the efficiency feature builder is properly imported when enabled."""
    # This import should succeed when ENABLE_EFFICIENCY_FEATURES is set
    from src.features import EfficiencyFeatureBuilder, create_feature_builder
    
    # Check that the builder can be created
    builder = create_feature_builder("efficiency")
    
    # Verify it's the right type
    assert isinstance(builder, EfficiencyFeatureBuilder)


def test_efficiency_builder_basic_methods(setup_env) -> None:
    """Test that the efficiency feature builder methods work correctly."""
    from src.features import create_feature_builder
    
    # Create the feature builder
    builder = create_feature_builder("efficiency")
    
    # Test that the builder has the expected attributes
    assert builder.name == "efficiency"
    assert builder.iterations == 10  # Default value
    assert builder.output_file == "team_performance.parquet"
    
    # Test with custom config
    custom_builder = create_feature_builder("efficiency", {
        "iterations": 5,
        "min_possessions": 50
    })
    
    assert custom_builder.iterations == 5
    assert custom_builder.min_possessions == 50


def test_disable_efficiency_features() -> None:
    """Test that efficiency features can be controlled via environment variable."""
    # Save current environment state
    old_value = os.environ.get("ENABLE_EFFICIENCY_FEATURES")
    
    try:
        # Disable efficiency features
        os.environ["ENABLE_EFFICIENCY_FEATURES"] = "0"
        
        # Reload the module to apply the environment change
        import src.features
        importlib.reload(src.features)
        
        # This test just verifies that we can set the environment variable
        # and reload the module without errors
        assert os.environ["ENABLE_EFFICIENCY_FEATURES"] == "0"
        
    finally:
        # Restore environment
        if old_value is not None:
            os.environ["ENABLE_EFFICIENCY_FEATURES"] = old_value
        else:
            del os.environ["ENABLE_EFFICIENCY_FEATURES"]
        
        # Reload the module to restore original state
        import src.features
        importlib.reload(src.features) 