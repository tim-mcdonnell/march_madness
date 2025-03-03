"""
Example script demonstrating how to use the data loader.

This script shows how to download and load NCAA basketball data from the
sportsdataverse/hoopR-mbb-data GitHub repository.
"""

import logging
import os
from pathlib import Path

from src.data.loader import (
    download_category_data,
    download_year_data,
    download_all_data,
    load_category_data,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("data_example")

# Create directory if it doesn't exist
os.makedirs("data/raw", exist_ok=True)


def download_single_category_example():
    """Example showing how to download a single category for a specific year."""
    logger.info("Downloading play-by-play data for 2023")
    file_path = download_category_data("play_by_play", 2023)
    
    if file_path:
        logger.info(f"Downloaded to: {file_path}")
    else:
        logger.error("Download failed")


def download_year_example():
    """Example showing how to download all categories for a specific year."""
    logger.info("Downloading all data for 2023")
    results = download_year_data(2023)
    
    # Check results
    for category, file_path in results.items():
        if file_path:
            logger.info(f"Downloaded {category} data to: {file_path}")
        else:
            logger.error(f"Failed to download {category} data")


def download_specific_categories_example():
    """Example showing how to download specific categories for a year."""
    logger.info("Downloading specific categories for 2023")
    categories = ["team_box", "schedules"]
    results = download_year_data(2023, categories=categories)
    
    # Check results
    for category, file_path in results.items():
        if file_path:
            logger.info(f"Downloaded {category} data to: {file_path}")
        else:
            logger.error(f"Failed to download {category} data")


def download_multiple_years_example():
    """Example showing how to download data for multiple years."""
    logger.info("Downloading data for years 2022-2023")
    results = download_all_data(2022, 2023)
    
    # Check results
    for year, year_results in results.items():
        logger.info(f"Year {year}:")
        for category, file_path in year_results.items():
            if file_path:
                logger.info(f"  - Downloaded {category} data to: {file_path}")
            else:
                logger.error(f"  - Failed to download {category} data")


def load_and_examine_data_example():
    """Example showing how to load and examine downloaded data."""
    logger.info("Loading team box score data for 2023")
    table = load_category_data("team_box", 2023)
    
    if table is not None:
        # Print basic information about the table
        logger.info(f"Loaded table with {len(table)} rows and {len(table.column_names)} columns")
        logger.info(f"Columns: {table.column_names}")
        
        # Display first few rows (head)
        logger.info("First 5 rows:")
        logger.info(table.slice(0, 5).to_pandas())
    else:
        logger.error("Failed to load data")


def download_with_caching_example():
    """Example showing how caching works to avoid re-downloading files."""
    logger.info("Demonstrating caching behavior")
    
    # First download
    logger.info("First download attempt:")
    file_path = download_category_data("schedules", 2023)
    
    if file_path:
        logger.info(f"Downloaded to: {file_path}")
    
    # Second download (should use cached file)
    logger.info("Second download attempt (should use cached file):")
    file_path = download_category_data("schedules", 2023)
    
    if file_path:
        logger.info(f"File already exists at: {file_path}")
    
    # Force re-download with overwrite
    logger.info("Force re-download with overwrite=True:")
    file_path = download_category_data("schedules", 2023, overwrite=True)
    
    if file_path:
        logger.info(f"Re-downloaded to: {file_path}")


if __name__ == "__main__":
    logger.info("NCAA March Madness Data Example")
    logger.info("-" * 40)
    
    # Choose one example to run
    # Uncomment the example you want to run
    
    download_single_category_example()
    # download_year_example()
    # download_specific_categories_example()
    # download_multiple_years_example()
    # load_and_examine_data_example()
    # download_with_caching_example() 