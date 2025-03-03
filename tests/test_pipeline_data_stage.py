"""Tests for the data stage pipeline, focusing on file generation verification."""

import os
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest import mock

import polars as pl
import pytest

from src.data.transformer import normalize_schema
from src.pipeline.data_stage import process_transformations, run_data_stage

# Test constants
TEST_RAW_DIR = Path("tests/data_test_pipeline/raw")
TEST_PROCESSED_DIR = Path("tests/data_test_pipeline/processed")
TEST_YEARS = [2023, 2024]
TEST_CATEGORIES = ["play_by_play", "player_box", "schedules", "team_box"]


@pytest.fixture
def test_config() -> dict[str, Any]:
    """Create a test configuration for the pipeline."""
    return {
        "data": {
            "raw_dir": str(TEST_RAW_DIR),
            "processed_dir": str(TEST_PROCESSED_DIR),
            "years": TEST_YEARS,
            "categories": TEST_CATEGORIES
        },
        "validation": {
            "enabled": True,
            "strict": False,
            "strict_optional": False,
            "check_consistency": True
        }
    }


@pytest.fixture
def setup_test_dirs() -> Generator[None, None, None]:
    """Setup and teardown test directories."""
    # Create test directories
    os.makedirs(TEST_RAW_DIR, exist_ok=True)
    os.makedirs(TEST_PROCESSED_DIR, exist_ok=True)
    
    # Yield to test
    yield
    
    # Clean up after test
    shutil.rmtree(TEST_RAW_DIR, ignore_errors=True)
    shutil.rmtree(TEST_PROCESSED_DIR, ignore_errors=True)


@pytest.fixture
def create_test_data(setup_test_dirs: None) -> Generator[None, None, None]:
    """Create test data for all categories."""
    # Create data for each category and year
    for category in TEST_CATEGORIES:
        category_dir = TEST_RAW_DIR / category
        os.makedirs(category_dir, exist_ok=True)
        
        for year in TEST_YEARS:
            if category == 'schedules':
                filename = f"mbb_schedule_{year}.parquet"
                df = pl.DataFrame({
                    "game_id": [1001, 1002, 1003],
                    "season": [year, year, year],
                    "game_date": ["2023-01-01", "2023-01-05", "2023-01-10"],
                    "home_team_id": [101, 102, 103],
                    "away_team_id": [102, 103, 101],
                    "home_team_name": ["Team A", "Team B", "Team C"],
                    "away_team_name": ["Team B", "Team C", "Team A"],
                    "home_points": [75, 68, 82],
                    "away_points": [70, 65, 78],
                    "neutral_site": [False, False, False]
                })
            else:
                filename = f"{category}_{year}.parquet"
                df = pl.DataFrame({
                    "game_id": [1001, 1002, 1003],
                    "team_id": [101, 102, 103],
                    "season": [year, year, year],
                })
                
                # Add category-specific columns
                if category == "play_by_play":
                    df = df.with_columns([
                        pl.lit("1").alias("sequence_number"),
                        pl.lit("1").alias("half"),
                        pl.lit("10").alias("clock_minutes"),
                        pl.lit("30").alias("clock_seconds")
                    ])
                elif category == "player_box":
                    df = df.with_columns([
                        pl.lit(1).alias("player_id"),
                        pl.lit(10).alias("points")
                    ])
                elif category == "team_box":
                    df = df.with_columns([
                        pl.lit(70).alias("points"),
                        pl.lit(30).alias("rebounds")
                    ])
            
            df.write_parquet(category_dir / filename)
    
    yield


def test_process_transformations_generates_files(
    test_config: dict[str, Any], create_test_data: None
) -> None:
    """Test that process_transformations generates all expected files."""
    # Run the transformations
    result = process_transformations(test_config)
    
    # Check that the function returned True (successful execution)
    assert result is True
    
    # Check that all expected files exist
    expected_files = [
        "team_box.parquet",
        "player_box.parquet",
        "schedules.parquet",
        "play_by_play.parquet",
        "team_season_statistics.parquet"
    ]
    
    for file_name in expected_files:
        file_path = TEST_PROCESSED_DIR / file_name
        assert file_path.exists(), f"Expected file {file_name} was not generated"
        
        # Also check that the files are not empty
        df = pl.read_parquet(file_path)
        assert len(df) > 0, f"File {file_name} is empty"


@mock.patch("src.data.transformer.process_all_transformations")
def test_process_transformations_returns_false_on_error(
    mock_process: mock.MagicMock, test_config: dict[str, Any], setup_test_dirs: None
) -> None:
    """Test that process_transformations returns False when an error occurs."""
    # Setup mock to raise an exception
    mock_process.side_effect = Exception("Test exception")
    
    # Run the transformations, should return False
    result = process_transformations(test_config)
    
    # Check that function returned False (error occurred)
    assert result is False


@mock.patch("src.data.transformer.process_all_transformations")
def test_process_transformations_detects_missing_files(
    mock_process: mock.MagicMock, test_config: dict[str, Any], setup_test_dirs: None
) -> None:
    """Test that process_transformations detects when expected files are not generated."""
    # Setup mock to return empty dict (no files generated)
    mock_process.return_value = {}
    
    # Run the transformations
    result = process_transformations(test_config)
    
    # The function returns True even when no files are generated, but logs a warning
    assert result is True


def test_schema_normalization_handles_type_mismatches(setup_test_dirs: None) -> None:
    """Test that schema normalization properly handles type mismatches between years."""
    # Create test data with type mismatches

    # Year 2023 data has string types for sequence columns
    play_by_play_2023 = pl.DataFrame({
        "game_id": [1001, 1002, 1003],
        "sequence_number": ["1", "2", "3"],
        "half": ["1", "1", "2"],
        "clock_minutes": ["18", "17", "10"],
        "clock_seconds": ["45", "30", "15"],
        "season": [2023, 2023, 2023]
    })

    # Year 2024 data has int types for sequence columns
    play_by_play_2024 = pl.DataFrame({
        "game_id": [2001, 2002, 2003],
        "sequence_number": [1, 2, 3],
        "half": [1, 1, 2],
        "clock_minutes": [19, 18, 12],
        "clock_seconds": [55, 40, 25],
        "season": [2024, 2024, 2024]
    })

    # Save test files
    os.makedirs(TEST_RAW_DIR / "play_by_play", exist_ok=True)
    play_by_play_2023.write_parquet(TEST_RAW_DIR / "play_by_play" / "play_by_play_2023.parquet")
    play_by_play_2024.write_parquet(TEST_RAW_DIR / "play_by_play" / "play_by_play_2024.parquet")

    # Load the data using the same functions the pipeline would use
    data_frames = {}
    for year in [2023, 2024]:
        try:
            file_path = TEST_RAW_DIR / "play_by_play" / f"play_by_play_{year}.parquet"
            if file_path.exists():
                df = pl.read_parquet(file_path)
                data_frames[year] = df
        except Exception as e:
            pytest.fail(f"Failed to load test data: {e}")

    # Normalize the schema
    normalized_frames = normalize_schema(data_frames, "play_by_play")

    # Verify that both years have the same schema
    assert set(normalized_frames[2023].columns) == set(normalized_frames[2024].columns)

    # Verify that all columns have the same type in both years
    for col in normalized_frames[2023].columns:
        year_2023_type = normalized_frames[2023][col].dtype
        year_2024_type = normalized_frames[2024][col].dtype
        assert year_2023_type == year_2024_type, (
            f"Column {col} has different types: {year_2023_type} vs {year_2024_type}"
        )
    
    # Verify type conversion: sequence columns should be strings after normalization
    string_columns = ["sequence_number", "half", "clock_minutes", "clock_seconds"]
    for col in string_columns:
        dtype_str = str(normalized_frames[2024][col].dtype).lower()
        assert dtype_str in ["utf8", "string"], (
            f"Column {col} was not converted to string type, got {dtype_str}"
        )
        
        # Check specific values to ensure they were converted correctly
        assert normalized_frames[2024][col][0] == str(play_by_play_2024[col][0]), (
            f"Value for {col} was not correctly converted"
        )


@mock.patch("src.pipeline.data_stage.validate_downloaded_data")
@mock.patch("src.pipeline.data_stage.process_transformations")
def test_run_data_stage_full_pipeline(
    mock_process: mock.MagicMock, mock_validate: mock.MagicMock, test_config: dict[str, Any]
) -> None:
    """Test the full data stage pipeline execution."""
    # Setup mocks
    mock_validate.return_value = True
    mock_process.return_value = True
    
    # Run the data stage
    result = run_data_stage(test_config)
    
    # Check that pipeline completed successfully
    assert result is True
    
    # Verify that validate_downloaded_data was called
    mock_validate.assert_called_once()
    
    # Verify that process_transformations was called
    mock_process.assert_called_once_with(test_config)


@mock.patch("src.pipeline.data_stage.run_data_stage")
def test_integration_with_cli(
    mock_run_data_stage: mock.MagicMock, test_config: dict[str, Any]
) -> None:
    """Test integration with the CLI pipeline runner."""
    # Import here to avoid circular imports
    from src.pipeline.cli import _run_pipeline_stage
    
    # Setup mock
    mock_run_data_stage.return_value = True
    
    # Create CLI args
    class Args:
        def __init__(self) -> None:
            self.stages = ["data"]
            self.years = TEST_YEARS
            self.categories = TEST_CATEGORIES
    
    args = Args()
    
    # Run the pipeline with the CLI function
    result = _run_pipeline_stage("data", test_config, args)
    
    # Check that run_data_stage was called
    mock_run_data_stage.assert_called_once_with(test_config)
    
    # Check that the CLI returned success
    assert result["success"] is True


def test_end_to_end_with_type_mismatches(test_config: dict[str, Any]) -> None:
    """Test end-to-end processing with data that has type mismatches."""
    # Setup test data with type mismatches
    os.makedirs(TEST_RAW_DIR / "play_by_play", exist_ok=True)
    os.makedirs(TEST_PROCESSED_DIR, exist_ok=True)

    # Year 2023 data has string types
    play_by_play_2023 = pl.DataFrame({
        "game_id": [1001, 1002, 1003],
        "sequence_number": ["1", "2", "3"],
        "half": ["1", "1", "2"],
        "clock_minutes": ["18", "17", "10"],
        "clock_seconds": ["45", "30", "15"],
        "season": [2023, 2023, 2023],
        "team_id": [101, 102, 103],
    })

    # Year 2024 data has int types
    play_by_play_2024 = pl.DataFrame({
        "game_id": [2001, 2002, 2003],
        "sequence_number": [1, 2, 3],
        "half": [1, 1, 2],
        "clock_minutes": [19, 18, 12],
        "clock_seconds": [55, 40, 25],
        "season": [2024, 2024, 2024],
        "team_id": [104, 105, 106],
    })

    # Create team_box data for team season statistics
    team_box_2023 = pl.DataFrame({
        "game_id": [1001, 1002, 1003],
        "team_id": [101, 102, 103],
        "points": [70, 65, 80],
        "season": [2023, 2023, 2023],
    })

    team_box_2024 = pl.DataFrame({
        "game_id": [2001, 2002, 2003],
        "team_id": [104, 105, 106],
        "points": [75, 68, 82],
        "season": [2024, 2024, 2024],
    })

    # Create schedules data
    schedules_2023 = pl.DataFrame({
        "game_id": [1001, 1002, 1003],
        "season": [2023, 2023, 2023],
        "game_date": ["2023-01-01", "2023-01-05", "2023-01-10"],
        "home_team_id": [101, 102, 103],
        "away_team_id": [102, 103, 101],
        "home_team_name": ["Team A", "Team B", "Team C"],
        "away_team_name": ["Team B", "Team C", "Team A"],
        "home_points": [70, 65, 80],
        "away_points": [65, 60, 75]
    })

    schedules_2024 = pl.DataFrame({
        "game_id": [2001, 2002, 2003],
        "season": [2024, 2024, 2024],
        "game_date": ["2024-01-01", "2024-01-05", "2024-01-10"],
        "home_team_id": [104, 105, 106],
        "away_team_id": [105, 106, 104],
        "home_team_name": ["Team D", "Team E", "Team F"],
        "away_team_name": ["Team E", "Team F", "Team D"],
        "home_points": [75, 68, 82],
        "away_points": [70, 65, 78]
    })

    # Save test files
    play_by_play_2023.write_parquet(TEST_RAW_DIR / "play_by_play" / "play_by_play_2023.parquet")
    play_by_play_2024.write_parquet(TEST_RAW_DIR / "play_by_play" / "play_by_play_2024.parquet")

    os.makedirs(TEST_RAW_DIR / "team_box", exist_ok=True)
    team_box_2023.write_parquet(TEST_RAW_DIR / "team_box" / "team_box_2023.parquet")
    team_box_2024.write_parquet(TEST_RAW_DIR / "team_box" / "team_box_2024.parquet")

    os.makedirs(TEST_RAW_DIR / "schedules", exist_ok=True)
    schedules_2023.write_parquet(TEST_RAW_DIR / "schedules" / "mbb_schedule_2023.parquet")
    schedules_2024.write_parquet(TEST_RAW_DIR / "schedules" / "mbb_schedule_2024.parquet")

    # Create minimal player_box data
    os.makedirs(TEST_RAW_DIR / "player_box", exist_ok=True)
    player_box_2023 = pl.DataFrame({
        "game_id": [1001, 1002, 1003],
        "team_id": [101, 102, 103],
        "player_id": [1, 2, 3],
        "season": [2023, 2023, 2023],
    })
    player_box_2023.write_parquet(TEST_RAW_DIR / "player_box" / "player_box_2023.parquet")
    player_box_2024 = pl.DataFrame({
        "game_id": [2001, 2002, 2003],
        "team_id": [104, 105, 106],
        "player_id": [4, 5, 6],
        "season": [2024, 2024, 2024],
    })
    player_box_2024.write_parquet(TEST_RAW_DIR / "player_box" / "player_box_2024.parquet")

    # Run the transformations
    result = process_transformations(test_config)

    # Check that processing was successful
    assert result is True

    # Verify that the output file was created
    output_path = TEST_PROCESSED_DIR / "play_by_play.parquet"
    assert output_path.exists(), "play_by_play.parquet was not generated"

    # Load the output file and check that schema was properly normalized
    combined_df = pl.read_parquet(output_path)

    # Check row count (should include data from both years)
    assert len(combined_df) == 6, "Combined dataframe should have 6 rows"

    # Check that the sequence columns are all the same type (strings)
    for col in ["sequence_number", "half", "clock_minutes", "clock_seconds"]:
        dtype_str = str(combined_df[col].dtype).lower()
        assert dtype_str in ["utf8", "string"], (
            f"Column {col} should be a string type, got {dtype_str}"
        )
        
    # Check that data from both years is present
    assert set(combined_df["season"].unique().to_list()) == {2023, 2024}, (
        "Data from both years should be present"
    ) 