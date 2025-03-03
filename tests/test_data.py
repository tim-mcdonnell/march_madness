"""
Unit tests for data loading functionality.
"""

import os
from pathlib import Path
from unittest import mock

import pytest
import pyarrow as pa
import pyarrow.parquet as pq

from src.data.loader import (
    create_directory_structure,
    download_file,
    download_category_data,
    download_year_data,
    download_all_data,
    load_parquet,
    load_category_data,
    DATA_CATEGORIES,
)


# Test constants
TEST_DATA_DIR = Path("tests/data_test")
TEST_YEAR = 2023


class MockResponse:
    """Mock response object for requests.get"""
    
    def __init__(self, content=b"test data", status_code=200):
        self.content = content
        self.status_code = status_code
        self.headers = {"content-length": str(len(content))}
        
    def iter_content(self, chunk_size=1024):
        return [self.content]


@pytest.fixture
def setup_test_dir():
    """Setup and teardown test directory"""
    # Create test directory
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Run the test
    yield
    
    # Cleanup
    import shutil
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


def test_create_directory_structure(setup_test_dir):
    """Test creating directory structure"""
    create_directory_structure(TEST_DATA_DIR)
    
    # Check if base directory exists
    assert TEST_DATA_DIR.exists()
    
    # Check if category directories exist
    for category in DATA_CATEGORIES.values():
        category_dir = TEST_DATA_DIR / category["dir_name"]
        assert category_dir.exists()


@mock.patch("src.data.loader.requests.get")
def test_download_file(mock_get, setup_test_dir):
    """Test downloading a file"""
    # Mock response
    mock_get.return_value = MockResponse()
    
    # Test download
    output_path = TEST_DATA_DIR / "test_file.parquet"
    result = download_file("https://test.url", output_path)
    
    # Verify
    assert result is True
    assert output_path.exists()
    assert mock_get.called
    
    # Test with existing file (no overwrite)
    mock_get.reset_mock()
    result = download_file("https://test.url", output_path, overwrite=False)
    
    # Verify
    assert result is True
    assert not mock_get.called
    
    # Test with existing file (with overwrite)
    mock_get.reset_mock()
    result = download_file("https://test.url", output_path, overwrite=True)
    
    # Verify
    assert result is True
    assert mock_get.called


@mock.patch("src.data.loader.download_file")
def test_download_category_data(mock_download, setup_test_dir):
    """Test downloading category data"""
    # Mock download_file
    mock_download.return_value = True
    
    # Test with valid category
    result = download_category_data("play_by_play", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert result is not None
    assert mock_download.called
    
    # Test with invalid category
    result = download_category_data("invalid_category", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert result is None


@mock.patch("src.data.loader.download_category_data")
def test_download_year_data(mock_download_category, setup_test_dir):
    """Test downloading year data"""
    # Mock download_category_data
    expected_path = TEST_DATA_DIR / "test_file.parquet"
    mock_download_category.return_value = expected_path
    
    # Test with default categories
    result = download_year_data(TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert len(result) == len(DATA_CATEGORIES)
    assert mock_download_category.call_count == len(DATA_CATEGORIES)
    for path in result.values():
        assert path == expected_path
    
    # Reset mock
    mock_download_category.reset_mock()
    
    # Test with specific categories
    categories = ["play_by_play", "team_box"]
    result = download_year_data(TEST_YEAR, TEST_DATA_DIR, categories)
    
    # Verify
    assert len(result) == len(categories)
    assert mock_download_category.call_count == len(categories)
    
    # Test with invalid category
    mock_download_category.reset_mock()
    result = download_year_data(TEST_YEAR, TEST_DATA_DIR, ["invalid_category"])
    
    # Verify
    assert len(result) == 0
    assert mock_download_category.call_count == 0


@mock.patch("src.data.loader.download_year_data")
def test_download_all_data(mock_download_year, setup_test_dir):
    """Test downloading all data"""
    # Mock download_year_data
    mock_download_year.return_value = {"play_by_play": TEST_DATA_DIR / "test_file.parquet"}
    
    # Test with default years
    result = download_all_data(2023, 2024, TEST_DATA_DIR)
    
    # Verify
    assert len(result) == 2  # 2 years
    assert mock_download_year.call_count == 2
    
    # Test with invalid year range
    mock_download_year.reset_mock()
    result = download_all_data(2024, 2023, TEST_DATA_DIR)
    
    # Verify
    assert len(result) == 0
    assert mock_download_year.call_count == 0


@mock.patch("src.data.loader.pq.read_table")
def test_load_parquet(mock_read_table, setup_test_dir):
    """Test loading parquet file"""
    # Create a test file
    test_file = TEST_DATA_DIR / "test_file.parquet"
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    with open(test_file, "wb") as f:
        f.write(b"test data")
    
    # Mock read_table
    mock_table = mock.MagicMock(spec=pa.Table)
    mock_read_table.return_value = mock_table
    
    # Test with existing file
    result = load_parquet(test_file)
    
    # Verify
    assert result == mock_table
    assert mock_read_table.called
    
    # Test with non-existent file
    result = load_parquet(TEST_DATA_DIR / "non_existent.parquet")
    
    # Verify
    assert result is None


@mock.patch("src.data.loader.load_parquet")
@mock.patch("src.data.loader.download_category_data")
def test_load_category_data(mock_download_category, mock_load_parquet, setup_test_dir):
    """Test loading category data"""
    # Setup
    expected_file = TEST_DATA_DIR / "play_by_play" / f"play_by_play_{TEST_YEAR}.parquet"
    mock_table = mock.MagicMock(spec=pa.Table)
    
    # Create directory structure
    create_directory_structure(TEST_DATA_DIR)
    
    # Test when file exists
    os.makedirs(expected_file.parent, exist_ok=True)
    with open(expected_file, "wb") as f:
        f.write(b"test data")
    
    mock_load_parquet.return_value = mock_table
    
    # Load data
    result = load_category_data("play_by_play", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert result == mock_table
    assert mock_load_parquet.called
    assert not mock_download_category.called
    
    # Test when file doesn't exist but download_if_missing=True
    os.remove(expected_file)
    mock_load_parquet.reset_mock()
    mock_download_category.return_value = expected_file
    
    # Load data
    result = load_category_data("play_by_play", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert mock_download_category.called
    assert mock_load_parquet.called
    
    # Test when file doesn't exist and download_if_missing=False
    os.remove(expected_file)
    mock_load_parquet.reset_mock()
    mock_download_category.reset_mock()
    
    # Load data
    result = load_category_data("play_by_play", TEST_YEAR, TEST_DATA_DIR, download_if_missing=False)
    
    # Verify
    assert result is None
    assert not mock_download_category.called
    assert not mock_load_parquet.called
    
    # Test with invalid category
    result = load_category_data("invalid_category", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert result is None 