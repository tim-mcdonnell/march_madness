"""
Tests for data loading and downloading functionality.
"""

import os
from pathlib import Path
from unittest import mock

import pyarrow as pa
import pytest

from src.data.loader import (
    DATA_CATEGORIES,
    create_directory_structure,
    download_all_data,
    download_category_data,
    download_file,
    download_year_data,
    load_category_data,
    load_parquet,
)

# Test constants
TEST_DATA_DIR = Path("tests/data_test")
TEST_YEAR = 2023


class MockResponse:
    """Mock response object for requests.get"""
    
    def __init__(self, content: bytes = b"test data", status_code: int = 200) -> None:
        self.content = content
        self.status_code = status_code
        self.headers = {"content-length": str(len(content))}
        
    def iter_content(self, chunk_size: int = 1024) -> list[bytes]:
        return [self.content]


@pytest.fixture
def setup_test_dir() -> None:
    """Setup and teardown test directory"""
    # Create test directory
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Run the test
    yield
    
    # Cleanup
    import shutil
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


def test_create_directory_structure(setup_test_dir: None) -> None:
    """Test creating directory structure"""
    # Create directory structure
    create_directory_structure()
    
    # Check that directories were created
    for category in DATA_CATEGORIES:
        for year in [TEST_YEAR]:
            path = TEST_DATA_DIR / category["dir_name"] / str(year)
            assert path.exists()  # noqa: S101


@mock.patch("src.data.loader.requests.get")
def test_download_file(mock_get: mock.MagicMock, setup_test_dir: None) -> None:
    """Test downloading a file"""
    # Mock response
    mock_get.return_value = MockResponse()
    
    # Test download
    output_path = TEST_DATA_DIR / "test_file.parquet"
    result = download_file("https://test.url", output_path)
    
    # Verify
    assert result is True  # noqa: S101
    assert output_path.exists()  # noqa: S101
    assert mock_get.called  # noqa: S101
    
    # Test with existing file (no overwrite)
    mock_get.reset_mock()
    result = download_file("https://test.url", output_path, overwrite=False)
    
    # Verify
    assert result is True  # noqa: S101
    assert not mock_get.called  # noqa: S101
    
    # Test with existing file (with overwrite)
    mock_get.reset_mock()
    result = download_file("https://test.url", output_path, overwrite=True)
    
    # Verify
    assert result is True  # noqa: S101
    assert mock_get.called  # noqa: S101


@mock.patch("src.data.loader.download_file")
def test_download_category_data(
    mock_download: mock.MagicMock, 
    setup_test_dir: None
) -> None:
    """Test downloading category data"""
    # Mock download_file
    mock_download.return_value = True
    
    # Test with valid category
    result = download_category_data("play_by_play", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert result is not None  # noqa: S101
    assert mock_download.called  # noqa: S101
    
    # Test with invalid category
    result = download_category_data("invalid_category", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert result is None  # noqa: S101


@mock.patch("src.data.loader.download_category_data")
def test_download_year_data(
    mock_download_category: mock.MagicMock, 
    setup_test_dir: None
) -> None:
    """Test downloading year data"""
    # Mock download_category_data
    expected_path = TEST_DATA_DIR / "test_file.parquet"
    mock_download_category.return_value = expected_path
    
    # Test with default categories
    result = download_year_data(TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert len(result) == len(DATA_CATEGORIES)  # noqa: S101
    assert mock_download_category.call_count == len(DATA_CATEGORIES)  # noqa: S101
    for path in result.values():
        assert path == expected_path  # noqa: S101
    
    # Reset mock
    mock_download_category.reset_mock()
    
    # Test with specific categories
    categories = ["play_by_play", "team_box"]
    result = download_year_data(TEST_YEAR, TEST_DATA_DIR, categories)
    
    # Verify
    assert len(result) == len(categories)  # noqa: S101
    assert mock_download_category.call_count == len(categories)  # noqa: S101
    
    # Test with invalid category
    mock_download_category.reset_mock()
    result = download_year_data(TEST_YEAR, TEST_DATA_DIR, ["invalid_category"])
    
    # Verify
    assert len(result) == 0  # noqa: S101
    assert mock_download_category.call_count == 0  # noqa: S101


@mock.patch("src.data.loader.download_year_data")
def test_download_all_data(
    mock_download_year: mock.MagicMock, 
    setup_test_dir: None
) -> None:
    """Test downloading all data"""
    # Mock download_year_data
    mock_download_year.return_value = {
        "play_by_play": TEST_DATA_DIR / "test_file.parquet"
    }
    
    # Test with default years
    result = download_all_data(2023, 2024, TEST_DATA_DIR)
    
    # Verify
    assert len(result) == 2  # noqa: S101
    assert mock_download_year.call_count == 2  # noqa: S101
    
    # Test with invalid year range
    mock_download_year.reset_mock()
    result = download_all_data(2024, 2023, TEST_DATA_DIR)
    
    # Verify
    assert len(result) == 0  # noqa: S101
    assert mock_download_year.call_count == 0  # noqa: S101


@mock.patch("src.data.loader.pq.read_table")
def test_load_parquet(mock_read_table: mock.MagicMock, setup_test_dir: None) -> None:
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
    assert result == mock_table  # noqa: S101
    assert mock_read_table.called  # noqa: S101
    
    # Test with non-existent file
    result = load_parquet(TEST_DATA_DIR / "non_existent.parquet")
    
    # Verify
    assert result is None  # noqa: S101


@mock.patch("src.data.loader.load_parquet")
@mock.patch("src.data.loader.download_category_data")
def test_load_category_data(
    mock_download_category: mock.MagicMock, 
    mock_load_parquet: mock.MagicMock,
    setup_test_dir: None
) -> None:
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
    assert result == mock_table  # noqa: S101
    assert mock_load_parquet.called  # noqa: S101
    assert not mock_download_category.called  # noqa: S101
    
    # Test when file doesn't exist but download_if_missing=True
    os.remove(expected_file)
    mock_load_parquet.reset_mock()
    mock_download_category.return_value = expected_file
    
    # Load data
    result = load_category_data("play_by_play", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert mock_download_category.called  # noqa: S101
    assert mock_load_parquet.called  # noqa: S101
    
    # Test when file doesn't exist and download_if_missing=False
    os.remove(expected_file)
    mock_load_parquet.reset_mock()
    mock_download_category.reset_mock()
    
    # Load data
    result = load_category_data(
        "play_by_play", 
        TEST_YEAR, 
        TEST_DATA_DIR, 
        download_if_missing=False
    )
    
    # Verify
    assert result is None  # noqa: S101
    assert not mock_download_category.called  # noqa: S101
    assert not mock_load_parquet.called  # noqa: S101
    
    # Test with invalid category
    result = load_category_data("invalid_category", TEST_YEAR, TEST_DATA_DIR)
    
    # Verify
    assert result is None  # noqa: S101 