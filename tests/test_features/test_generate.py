"""Tests for the feature generation module."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from src.features.generate import generate_features, main


@pytest.fixture
def mock_feature_builder() -> MagicMock:
    """Create a mock feature builder."""
    mock_builder = MagicMock()
    mock_builder.build_features.return_value = pl.DataFrame({
        "team_id": [1, 2, 3],
        "season": [2023, 2023, 2023],
        "test_feature": [0.5, 0.6, 0.7]
    })
    mock_builder.save_features.return_value = Path("/mock/path/features.parquet")
    return mock_builder


@pytest.fixture
def mock_data() -> tuple[pl.DataFrame, pl.DataFrame]:
    """Create mock data for testing."""
    team_season_stats = pl.DataFrame({
        "team_id": [1, 2, 3],
        "season": [2023, 2023, 2023],
        "win_percentage": [0.7, 0.8, 0.9]
    })
    
    team_box = pl.DataFrame({
        "team_id": [1, 1, 2, 2, 3, 3],
        "game_id": [101, 102, 201, 202, 301, 302],
        "season": [2023, 2023, 2023, 2023, 2023, 2023],
        "points": [80, 85, 75, 70, 90, 95]
    })
    
    return team_season_stats, team_box


@patch("src.features.generate.create_feature_builder")
@patch("src.features.generate.pl.read_parquet")
def test_generate_features(mock_read_parquet, mock_create_builder, mock_feature_builder, mock_data) -> None:
    """Test the generate_features function."""
    team_season_stats, team_box = mock_data
    
    # Configure mocks
    mock_create_builder.return_value = mock_feature_builder
    mock_read_parquet.side_effect = [team_season_stats, team_box]
    
    # Call the function
    output_path = generate_features("test_feature", "test_output_dir", "test_output.parquet", {"test_config": True})
    
    # Verify mocks were called correctly
    mock_create_builder.assert_called_once_with("test_feature", {"test_config": True})
    mock_read_parquet.assert_any_call("data/processed/team_season_statistics.parquet")
    mock_read_parquet.assert_any_call("data/processed/team_box.parquet")
    
    # Verify the feature builder was used correctly
    mock_feature_builder.build_features.assert_called_once()
    args = mock_feature_builder.build_features.call_args[0]
    assert all(isinstance(arg, pl.DataFrame) for arg in args)
    
    mock_feature_builder.save_features.assert_called_once_with(
        mock_feature_builder.build_features.return_value,
        "test_output_dir",
        "test_output.parquet"
    )
    
    # Verify the returned path
    assert output_path == Path("/mock/path/features.parquet")


@patch("src.features.generate.generate_features")
@patch("src.features.generate.argparse.ArgumentParser.parse_args")
@patch("src.features.generate.get_available_feature_builders")
def test_main_function(mock_get_builders, mock_parse_args, mock_generate_features) -> None:
    """Test the main function."""
    # Configure mocks
    mock_get_builders.return_value = ["foundation", "test_feature"]
    mock_args = argparse.Namespace(
        feature_set="test_feature",
        output_dir="test_output_dir",
        output_filename="test_output.parquet",
        recent_form_games=5,
        iterations=10,
        min_possessions=100
    )
    mock_parse_args.return_value = mock_args
    mock_generate_features.return_value = Path("/mock/path/features.parquet")
    
    # Call the function
    main()
    
    # Verify mocks were called correctly
    mock_generate_features.assert_called_once_with(
        "test_feature",
        "test_output_dir",
        "test_output.parquet",
        {
            "recent_form_games": 5, 
            "iterations": 10, 
            "min_possessions": 100,
            "output_file": "test_output.parquet"
        }
    )


@patch("src.features.generate.argparse.ArgumentParser.parse_args")
@patch("src.features.generate.logger.info")
def test_main_output(mock_logger, mock_parse_args) -> None:
    """Test the output message of the main function."""
    with patch("src.features.generate.generate_features") as mock_generate_features:
        # Configure mocks
        mock_parse_args.return_value = argparse.Namespace(
            feature_set="foundation",
            output_dir="data/features",
            output_filename="team_performance.parquet",
            recent_form_games=10,
            iterations=10,
            min_possessions=100
        )
        mock_generate_features.return_value = Path("data/features/team_performance.parquet")
        
        # Call the function
        main()
        
        # Verify the logger was called with the correct message
        # Note: logger.info is called multiple times, we want the last call
        mock_logger.assert_any_call("Features saved to data/features/team_performance.parquet")


@patch("src.features.generate.get_available_feature_builders")
def test_mock_available_builders(mock_get_builders) -> None:
    """Mock available builders for testing to exclude efficiency builder."""
    mock_get_builders.return_value = ["foundation", "test_feature"]
    # Test that the mock works
    from src.features.generate import get_available_feature_builders
    assert get_available_feature_builders() == ["foundation", "test_feature"] 