"""Tests for the TeamMasterStage pipeline component."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from src.pipeline.team_master_stage import TeamMasterStage


@pytest.fixture
def mock_config() -> dict:
    """Create a mock pipeline configuration."""
    return {
        "data": {
            "raw_dir": "data/raw",
            "master_dir": "data/master",
            "processed_dir": "data/processed",
            "data_dir": "data"
        }
    }


@pytest.fixture
def test_data_dir(tmp_path) -> Path:
    """Create test directories for the tests."""
    # Create test directories
    raw_dir = tmp_path / "raw" / "team_box"
    raw_dir.mkdir(parents=True)
    
    master_dir = tmp_path / "master"
    master_dir.mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def stage(mock_config, test_data_dir) -> TeamMasterStage:
    """Create a TeamMasterStage instance with test configuration."""
    # Update config to use tmp_path
    config = mock_config.copy()
    config["data"]["raw_dir"] = str(test_data_dir / "raw")
    config["data"]["master_dir"] = str(test_data_dir / "master")
    config["data"]["data_dir"] = str(test_data_dir)
    
    return TeamMasterStage(data_dir=str(test_data_dir), config=config)


@pytest.fixture
def mock_raw_data(test_data_dir) -> Path:
    """Create mock raw data for testing."""
    # Create team box data
    raw_dir = test_data_dir / "raw" / "team_box"
    file_path = raw_dir / "team_box_2023.parquet"
    
    # Create a simple DataFrame with team IDs
    df = pl.DataFrame({
        "team_id": [101, 102, 103],
        "game_id": [1, 1, 2],
        "points": [75, 80, 65]
    })
    
    df.write_parquet(file_path)
    
    # Create another file for a different year
    file_path2 = raw_dir / "team_box_2022.parquet"
    df2 = pl.DataFrame({
        "team_id": [101, 104],
        "game_id": [3, 3],
        "points": [70, 85]
    })
    
    df2.write_parquet(file_path2)
    
    return raw_dir


@pytest.fixture
def mock_espn_response() -> dict:
    """Create a mock ESPN API response."""
    return {
        "team": {
            "id": "101",
            "location": "Test University",
            "name": "Bulldogs",
            "abbreviation": "TEST",
            "displayName": "Test University Bulldogs",
            "shortDisplayName": "Test",
            "color": "123456",
            "alternateColor": "ABCDEF",
            "logos": [
                {"href": "https://example.com/logo.png"}
            ],
            "conference": {
                "id": "1",
                "name": "Test Conference"
            }
        }
    }


def test_process_espn_response(mock_espn_response) -> None:
    """Test processing ESPN API response."""
    # Create stage with direct config
    stage = TeamMasterStage()
    
    # Process response
    result = stage._process_espn_response(101, mock_espn_response)
    
    # Verify basic info extraction
    assert result["team_id"] == 101
    assert result["location"] == "Test University"
    assert result["name"] == "Bulldogs"
    assert result["abbreviation"] == "TEST"
    assert result["display_name"] == "Test University Bulldogs"
    assert result["short_name"] == "Test"
    assert result["color"] == "123456"
    assert result["alternate_color"] == "ABCDEF"
    assert result["logo_url"] == "https://example.com/logo.png"
    assert result["conference_id"] == "1"
    assert result["conference_name"] == "Test Conference"


@patch("src.pipeline.team_master_stage.requests.get")
def test_fetch_team_data_from_espn(mock_get, stage, mock_espn_response) -> None:
    """Test fetching team metadata from ESPN API."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_espn_response
    mock_get.return_value = mock_response
    
    # Call the function
    result = stage._fetch_team_data_from_espn(101)
    
    # Verify the result
    assert "team" in result
    assert result["team"]["location"] == "Test University"
    assert result["team"]["name"] == "Bulldogs"
    
    # Verify the function called requests.get with the right URL
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "101" in call_args[0][0]  # URL contains team ID


@patch.object(TeamMasterStage, "_fetch_team_data_from_espn")
def test_fetch_team_data_from_espn_error(mock_fetch, stage) -> None:
    """Test that error handling in _enrich_team_data works correctly."""
    # Setup mock to return empty dict on error
    mock_fetch.return_value = {}
    
    # Create a test base file
    base_file_path = stage.master_data_dir / "team_master_base.parquet"
    df = pl.DataFrame({
        "team_id": [101, 102],
        "season": [2023, 2023],
        "location": [None, None],
        "name": [None, None]
    })
    df.write_parquet(base_file_path)
    
    # Should still complete without error
    assert stage._enrich_team_data() is True


@patch("src.pipeline.team_master_stage.requests.get")
def test_simple_integration(mock_get, mock_config, test_data_dir, mock_raw_data) -> None:
    """Simple integration test focused on data extraction and team master file creation."""
    # Setup mock response for ESPN API that handles all arguments
    def mock_espn_response(url: str, **kwargs) -> MagicMock:
        team_id = int(url.split("/")[-1])
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "team": {
                "id": str(team_id),
                "location": f"University {team_id}",
                "name": f"Team {team_id}",
                "displayName": f"University {team_id} Team {team_id}",
                "abbreviation": f"T{team_id}",
                "color": "123456",
                "alternateColor": "ABCDEF",
                "logos": [{"href": f"https://example.com/logo-{team_id}.png"}],
                "conference": {"id": "1", "name": "Test Conference"}
            }
        }
        return mock_response
    
    mock_get.side_effect = mock_espn_response
    
    # Run the stage
    config = mock_config.copy()
    config["data"]["raw_dir"] = str(test_data_dir / "raw")
    config["data"]["master_dir"] = str(test_data_dir / "master")
    config["data"]["data_dir"] = str(test_data_dir)
    
    stage = TeamMasterStage(data_dir=str(test_data_dir), config=config)
    result = stage.run(batch_size=10)
    
    assert result is True
    
    # Verify base file was created
    base_file = test_data_dir / "master" / "team_master_base.parquet"
    assert base_file.exists()
    
    # Verify enriched file was created
    enriched_file = test_data_dir / "master" / "team_master.parquet"
    assert enriched_file.exists()
    
    # Verify content
    df = pl.read_parquet(enriched_file)
    
    # Unique team IDs
    unique_teams = df.select("team_id").unique()
    assert unique_teams.height == 4  # We had 4 team IDs: 101, 102, 103, 104 