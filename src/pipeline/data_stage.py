"""
Data collection and cleaning stage for the NCAA March Madness prediction pipeline.

This module handles data ingestion from the sportsdataverse/hoopR-mbb-data repository
using the functionality in src/data/loader.py.
"""

import logging
from pathlib import Path
from typing import Any

from src.data.loader import (
    download_all_data,
    download_year_data,
    load_category_data,
)
from src.pipeline.data_management import ensure_directories

logger = logging.getLogger(__name__)


def run(
    config: dict[str, Any],
    years: list[int] | None = None,
    categories: list[str] | None = None,
) -> dict[str, Any]:
    """
    Run the data collection stage.
    
    Args:
        config: Pipeline configuration
        years: Years to process (None for all years in config)
        categories: Data categories to process (None for all)
        
    Returns:
        dict: Results dictionary with stage outputs
    """
    # Create necessary directories
    ensure_directories(config)
    
    # Get raw data directory from config
    raw_dir = Path(config["data"]["raw_dir"])
    
    # Use all years and categories from config if not specified
    if years is None:
        years = config["data"]["years"]
    
    if categories is None:
        categories = config["data"]["categories"]
    
    logger.info(f"Running data collection for years: {years}")
    logger.info(f"Categories: {categories}")
    
    # Download data
    results = {}
    
    # If multiple years, use download_all_data
    if len(years) > 1:
        start_year = min(years)
        end_year = max(years)
        
        # Check if this is a continuous range
        if set(years) == set(range(start_year, end_year + 1)):
            logger.info(f"Downloading data for years {start_year}-{end_year}")
            downloads = download_all_data(
                start_year=start_year,
                end_year=end_year,
                base_dir=raw_dir,
                categories=categories,
            )
            
            # Add to results
            for year, year_downloads in downloads.items():
                results[year] = {"downloaded": year_downloads}
        else:
            # Non-continuous range, download each year separately
            for year in years:
                logger.info(f"Downloading data for year {year}")
                year_downloads = download_year_data(
                    year=year,
                    base_dir=raw_dir,
                    categories=categories,
                )
                results[year] = {"downloaded": year_downloads}
    
    # Single year
    elif len(years) == 1:
        year = years[0]
        logger.info(f"Downloading data for year {year}")
        year_downloads = download_year_data(
            year=year,
            base_dir=raw_dir,
            categories=categories,
        )
        results[year] = {"downloaded": year_downloads}
    
    # No years specified, use default behavior
    else:
        logger.warning("No years specified for data collection")
        return {"error": "No years specified"}
    
    # Load some data to check it worked
    loaded_samples = {}
    for year in years:
        year_samples = {}
        for category in categories:
            try:
                # Load the data but don't store the whole table in results
                table = load_category_data(
                    category=category,
                    year=year,
                    base_dir=raw_dir,
                )
                
                if table is not None:
                    # Store metadata about the loaded table
                    year_samples[category] = {
                        "rows": len(table),
                        "columns": len(table.column_names),
                        "column_names": table.column_names,
                    }
                else:
                    year_samples[category] = {"error": "Failed to load data"}
            except Exception as e:
                logger.error(f"Error loading {category} data for year {year}: {e}")
                year_samples[category] = {"error": str(e)}
        
        loaded_samples[year] = year_samples
    
    # Add loaded samples to results
    results["loaded_samples"] = loaded_samples
    
    logger.info("Data collection stage completed")
    return results 