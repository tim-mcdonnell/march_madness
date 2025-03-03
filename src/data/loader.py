"""
Data loader module for NCAA March Madness prediction project.

This module provides functions to download and load parquet files from the 
sportsdataverse/hoopR-mbb-data GitHub repository.

Data Categories:
1. Play-by-Play Data
2. Player Box Scores
3. Game Schedules
4. Team Box Scores

Years Range: 2003-2025
"""

import logging
import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data/download.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("data_loader")

# Base URL and file patterns
BASE_URL = "https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb"
DATA_CATEGORIES = {
    "play_by_play": {
        "url_pattern": f"{BASE_URL}/pbp/parquet/play_by_play_{{year}}.parquet",
        "dir_name": "play_by_play",
    },
    "player_box": {
        "url_pattern": f"{BASE_URL}/player_box/parquet/player_box_{{year}}.parquet",
        "dir_name": "player_box",
    },
    "schedules": {
        "url_pattern": f"{BASE_URL}/schedules/parquet/mbb_schedule_{{year}}.parquet",
        "dir_name": "schedules",
    },
    "team_box": {
        "url_pattern": f"{BASE_URL}/team_box/parquet/team_box_{{year}}.parquet",
        "dir_name": "team_box",
    },
}

# Default data directory
DEFAULT_DATA_DIR = Path("data/raw")


def create_directory_structure(base_dir: str | Path = DEFAULT_DATA_DIR) -> None:
    """
    Create the directory structure for storing downloaded data.
    
    Args:
        base_dir: Base directory for storing data
        
    Returns:
        None
    """
    base_path = Path(base_dir)
    
    # Create base directory if it doesn't exist
    if not base_path.exists():
        logger.info(f"Creating base directory: {base_path}")
        base_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each data category
    for category in DATA_CATEGORIES.values():
        category_dir = base_path / category["dir_name"]
        if not category_dir.exists():
            logger.info(f"Creating directory: {category_dir}")
            category_dir.mkdir(parents=True, exist_ok=True)


def download_file(
    url: str, 
    output_path: str | Path, 
    overwrite: bool = False,
) -> bool:
    """
    Download a file from a URL and save it to the specified path.
    
    Args:
        url: URL to download the file from
        output_path: Path to save the downloaded file
        overwrite: Whether to overwrite existing files
        
    Returns:
        bool: True if download successful, False otherwise
    """
    output_path = Path(output_path)
    
    # Check if file already exists
    if output_path.exists() and not overwrite:
        logger.info(f"File already exists: {output_path}")
        return True
    
    try:
        logger.info(f"Downloading file from {url} to {output_path}")
        response = requests.get(url, stream=True, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Get file size for progress bar
            total_size = int(response.headers.get("content-length", 0))
            
            # Create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file with progress bar
            with open(output_path, "wb") as file, tqdm(
                desc=os.path.basename(output_path),
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)
            
            logger.info(f"Download successful: {output_path}")
            return True
        logger.warning(
            f"Failed to download file: {url}, Status code: {response.status_code}"
        )
        return False
    except Exception as e:
        logger.error(f"Error downloading file {url}: {e}")
        return False


def download_category_data(
    category: str, 
    year: int, 
    base_dir: str | Path = DEFAULT_DATA_DIR,
    overwrite: bool = False,
) -> Path | None:
    """
    Download data for a specific category and year.
    
    Args:
        category: Data category (play_by_play, player_box, schedules, team_box)
        year: Year to download data for
        base_dir: Base directory for storing data
        overwrite: Whether to overwrite existing files
        
    Returns:
        Path: Path to the downloaded file, or None if download failed
    """
    if category not in DATA_CATEGORIES:
        logger.error(f"Invalid category: {category}")
        return None
    
    base_path = Path(base_dir)
    category_info = DATA_CATEGORIES[category]
    url = category_info["url_pattern"].format(year=year)
    
    # Create output path
    output_dir = base_path / category_info["dir_name"]
    output_file = output_dir / f"{os.path.basename(url)}"
    
    # Download the file
    success = download_file(url, output_file, overwrite)
    
    if success:
        return output_file
    return None


def download_year_data(
    year: int, 
    base_dir: str | Path = DEFAULT_DATA_DIR,
    categories: list[str] | None = None,
    overwrite: bool = False,
) -> dict[str, Path | None]:
    """
    Download data for all categories for a specific year.
    
    Args:
        year: Year to download data for
        base_dir: Base directory for storing data
        categories: List of categories to download (default: all)
        overwrite: Whether to overwrite existing files
        
    Returns:
        Dict: Mapping of category to downloaded file path
    """
    # Use all categories if none specified
    if categories is None:
        categories = list(DATA_CATEGORIES.keys())
    else:
        # Validate categories
        for category in categories:
            if category not in DATA_CATEGORIES:
                logger.error(f"Invalid category: {category}")
                categories.remove(category)
    
    # Create the directory structure
    create_directory_structure(base_dir)
    
    # Download data for each category
    results = {}
    for category in categories:
        logger.info(f"Downloading {category} data for year {year}")
        file_path = download_category_data(category, year, base_dir, overwrite)
        results[category] = file_path
    
    return results


def download_all_data(
    start_year: int = 2003,
    end_year: int = 2025,
    base_dir: str | Path = DEFAULT_DATA_DIR,
    categories: list[str] | None = None,
    overwrite: bool = False,
) -> dict[int, dict[str, Path | None]]:
    """
    Download data for all years and categories.
    
    Args:
        start_year: Start year (inclusive)
        end_year: End year (inclusive)
        base_dir: Base directory for storing data
        categories: List of categories to download (default: all)
        overwrite: Whether to overwrite existing files
        
    Returns:
        Dict: Mapping of year to category to downloaded file path
    """
    # Validate year range
    if start_year > end_year:
        logger.error(f"Invalid year range: {start_year}-{end_year}")
        return {}
    
    # Create the directory structure
    create_directory_structure(base_dir)
    
    # Download data for each year
    results = {}
    for year in range(start_year, end_year + 1):
        logger.info(f"Downloading data for year {year}")
        year_results = download_year_data(year, base_dir, categories, overwrite)
        results[year] = year_results
    
    return results


def load_parquet(file_path: str | Path) -> pa.Table | None:
    """
    Load a parquet file into a PyArrow table.
    
    Args:
        file_path: Path to the parquet file
        
    Returns:
        pa.Table: PyArrow table, or None if loading failed
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File does not exist: {file_path}")
        return None
    
    try:
        logger.info(f"Loading parquet file: {file_path}")
        return pq.read_table(file_path)
    except Exception as e:
        logger.error(f"Error loading parquet file {file_path}: {e}")
        return None


def load_category_data(
    category: str,
    year: int,
    base_dir: str | Path = DEFAULT_DATA_DIR,
    download_if_missing: bool = True,
) -> pa.Table | None:
    """
    Load data for a specific category and year.
    
    Args:
        category: Data category (play_by_play, player_box, schedules, team_box)
        year: Year to load data for
        base_dir: Base directory for storing data
        download_if_missing: Whether to download the file if it's missing
        
    Returns:
        pa.Table: PyArrow table, or None if loading failed
    """
    if category not in DATA_CATEGORIES:
        logger.error(f"Invalid category: {category}")
        return None
    
    base_path = Path(base_dir)
    category_info = DATA_CATEGORIES[category]
    
    # Construct file path
    url = category_info["url_pattern"].format(year=year)
    file_name = os.path.basename(url)
    file_path = base_path / category_info["dir_name"] / file_name
    
    # Check if file exists
    if not file_path.exists():
        if download_if_missing:
            logger.info(f"File not found, downloading: {file_path}")
            file_path = download_category_data(category, year, base_dir)
            if file_path is None:
                return None
        else:
            logger.error(f"File not found: {file_path}")
            return None
    
    # Load the parquet file
    return load_parquet(file_path) 