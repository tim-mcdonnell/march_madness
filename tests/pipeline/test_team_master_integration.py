"""End-to-end test for the team master data stage."""
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from src.pipeline.team_master_stage import TeamMasterStage


@pytest.fixture
def test_environment() -> dict:
    """Set up a test environment with test data."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    try:
        # Set up directory structure
        data_dir = temp_path / "data"
        raw_dir = data_dir / "raw"
        team_box_dir = raw_dir / "team_box"
        team_box_dir.mkdir(parents=True, exist_ok=True)
        
        master_dir = data_dir / "master"
        master_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test data files
        # Team box data for 2022
        team_box_2022 = pl.DataFrame({
            "team_id": [101, 102, 103, 104],
            "team_name": ["Team A", "Team B", "Team C", "Team D"],
            "points": [70, 80, 65, 75]
        })
        team_box_2022.write_parquet(team_box_dir / "team_box_2022.parquet")
        
        # Team box data for 2023
        team_box_2023 = pl.DataFrame({
            "team_id": [101, 102, 105, 106],
            "team_name": ["Team A", "Team B", "Team E", "Team F"],
            "points": [75, 85, 70, 80]
        })
        team_box_2023.write_parquet(team_box_dir / "team_box_2023.parquet")
        
        yield {
            "temp_dir": temp_dir,
            "data_dir": str(data_dir),
            "master_dir": str(master_dir),
            "raw_dir": str(raw_dir)
        }
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

@patch("requests.get")
def test_full_team_master_stage(mock_get, test_environment) -> None:
    """End-to-end test of the TeamMasterStage."""
    # Mock ESPN API responses
    def mock_espn_api(url: str, **kwargs) -> MagicMock:
        """Mock the ESPN API response."""
        # Extract team_id from URL
        team_id = int(url.split("/")[-1])
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "team": {
                "id": str(team_id),
                "location": f"University {team_id}",
                "name": f"Team {team_id}",
                # Simplified response with only necessary fields
            }
        }
        return mock_response
    
    mock_get.side_effect = mock_espn_api
    
    # Create configuration
    config = {
        "data": {
            "data_dir": test_environment["data_dir"],
            "raw_dir": test_environment["raw_dir"],
            "master_dir": test_environment["master_dir"]
        }
    }
    
    # Create and run stage
    stage = TeamMasterStage(data_dir=test_environment["data_dir"], config=config)
    result = stage.run(batch_size=2)  # Use small batch size for testing
    
    assert result is True
    
    # Verify file was created (only using one file now)
    master_file = Path(test_environment["master_dir"]) / "team_master.parquet"
    assert master_file.exists()
    
    # Verify content of master file
    df = pl.read_parquet(master_file)
    
    # Check structure - only 4 columns now
    assert set(df.columns) == {"team_id", "season", "location", "name"}
    
    # Check team IDs (should have 6 unique teams)
    unique_team_ids = df.select("team_id").unique()
    assert unique_team_ids.height == 6
    
    # Check team names were populated (no nulls, only possibly empty strings)
    empty_names = df.filter(pl.col("name") == "")
    assert empty_names.height == 0

@patch("requests.get")
def test_incremental_updates(mock_get, test_environment) -> None:
    """Test that the stage can handle incremental updates to team data."""
    # Here we'll set up a scenario to test how the enrichment process works
    # when new teams are added to existing master data
    
    # Mock ESPN API responses
    def mock_espn_api(url: str, **kwargs) -> MagicMock:
        """Mock the ESPN API response."""
        # Extract team_id from URL
        team_id = int(url.split("/")[-1])
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "team": {
                "id": str(team_id),
                "location": f"University {team_id}",
                "name": f"Team {team_id}",
                # Simplified response with only necessary fields
            }
        }
        return mock_response
    
    mock_get.side_effect = mock_espn_api
    
    # Create configuration
    config = {
        "data": {
            "data_dir": test_environment["data_dir"],
            "raw_dir": test_environment["raw_dir"],
            "master_dir": test_environment["master_dir"]
        }
    }
    
    # Create test data directly
    master_path = Path(test_environment["master_dir"]) / "team_master.parquet"
    
    # Create test team data
    team_box_dir = Path(test_environment["raw_dir"]) / "team_box"
    team_box_2022 = pl.DataFrame({
        "team_id": [101, 102, 103, 104],
        "game_id": [1, 1, 2, 2],
        "points": [70, 80, 65, 75]
    })
    team_box_2022.write_parquet(team_box_dir / "team_box_2022.parquet")
    
    team_box_2023 = pl.DataFrame({
        "team_id": [101, 102, 105, 106],
        "game_id": [3, 3, 4, 4],
        "points": [75, 85, 70, 80]
    })
    team_box_2023.write_parquet(team_box_dir / "team_box_2023.parquet")
    
    # Create a half-populated master file that only has team 101 filled in
    # Others will have empty data to test incremental update
    stage = TeamMasterStage(
        data_dir=test_environment["data_dir"],
        config=config
    )
    
    # Run to create the initial master file
    stage.run(batch_size=1)
    
    # Verify the file was created
    assert master_path.exists()
    
    # Now modify the master file to simulate partially completed data
    # We'll leave only team 101's data and empty out the rest
    master_df = pl.read_parquet(master_path)
    
    # Create a new DataFrame with team 101 data intact and others emptied out
    team_101 = master_df.filter(pl.col("team_id") == 101)
    others = master_df.filter(pl.col("team_id") != 101).with_columns([
        pl.lit("").alias("location"),
        pl.lit("").alias("name"),
    ])
    
    # Combine and save back
    modified_df = pl.concat([team_101, others])
    modified_df.write_parquet(master_path)
    
    # Now run the enrichment to test incremental updates
    stage2 = TeamMasterStage(
        data_dir=test_environment["data_dir"],
        config=config
    )
    
    result = stage2.run(batch_size=2)
    assert result is True
    
    # Verify the results
    updated_df = pl.read_parquet(master_path)
    
    # Should have enriched all teams
    for team_id in [101, 102, 103, 104, 105, 106]:
        # Filter for this team ID
        team_rows = updated_df.filter(pl.col("team_id") == team_id)
        
        # Should have data for this team
        assert team_rows.height > 0
        
        # All rows should have non-empty location and name
        assert team_rows.filter(pl.col("location") == "").height == 0
        assert team_rows.filter(pl.col("name") == "").height == 0 