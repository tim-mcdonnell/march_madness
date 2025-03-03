#!/usr/bin/env python
"""
NCAA March Madness Pipeline Usage Example

This script demonstrates how to use the NCAA March Madness prediction pipeline 
for various common tasks. It provides examples of:
1. Running different pipeline stages
2. Customizing data selection
3. Cleaning data
4. Working with the configuration

Usage:
    python examples/pipeline_usage_example.py
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline.config import create_default_config, load_config
from src.pipeline.data_management import ensure_directories, purge_data
from src.pipeline.data_stage import run as run_data_stage


def setup_logging() -> None:
    """Configure logging for the example script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )


def example_1_basic_usage() -> dict:
    """Basic pipeline usage example."""
    logger = logging.getLogger("example_1")
    logger.info("Example 1: Basic Pipeline Usage")
    
    # Create default config if it doesn't exist
    config_path = "config/pipeline_config.yaml"
    if not Path(config_path).exists():
        logger.info(f"Creating default configuration at {config_path}")
        create_default_config(config_path)
    
    # Load configuration
    config = load_config(config_path)
    logger.info(f"Loaded configuration with {len(config['data']['years'])} years and "
                f"{len(config['data']['categories'])} categories")
    
    # Ensure required directories exist
    ensure_directories(config)
    
    # Run the data stage with default settings
    logger.info("Running data stage with default settings "
               "(limited to 2024-2025 for demo)")
    results = run_data_stage(config, years=[2024, 2025])
    
    # Display results summary
    logger.info(f"Data stage completed for {len(results) - 1} years")
    for year in results:
        if year != "loaded_samples":
            logger.info(f"Year {year}: Downloaded "
                       f"{len(results[year]['downloaded'])} categories")
    
    return results


def example_2_data_selection() -> dict:
    """Example showing how to select specific data."""
    logger = logging.getLogger("example_2")
    logger.info("Example 2: Selecting Specific Data")
    
    # Load config
    config = load_config()
    
    # Select specific years and categories
    selected_years = [2025]
    selected_categories = ["team_box", "schedules"]
    
    logger.info(f"Running data stage for years: {selected_years}")
    logger.info(f"Categories: {selected_categories}")
    
    results = run_data_stage(
        config,
        years=selected_years,
        categories=selected_categories
    )
    
    # Display sample of loaded data
    if "loaded_samples" in results:
        for year, year_data in results["loaded_samples"].items():
            for category, data in year_data.items():
                if "rows" in data:
                    logger.info(f"Loaded {data['rows']} rows for {category} {year}")
                    logger.info(f"Columns: {', '.join(data['column_names'][:5])}...")
    
    return results


def example_3_data_cleaning() -> dict:
    """Example showing how to clean data before processing."""
    logger = logging.getLogger("example_3")
    logger.info("Example 3: Data Cleaning")
    
    # Load config
    config = load_config()
    
    # Demo: clean specific data
    years = [2025]
    categories = ["schedules"]
    
    logger.info(f"Purging raw data for year {years[0]}, category {categories[0]}")
    purge_data("raw", config, categories, years)
    
    # Now download the data again
    logger.info("Re-downloading the purged data")
    results = run_data_stage(config, years=years, categories=categories)
    
    if (years[0] in results and 
        "downloaded" in results[years[0]] and 
        categories[0] in results[years[0]]["downloaded"]):
        path = results[years[0]]["downloaded"][categories[0]]
        logger.info(f"Successfully re-downloaded {categories[0]} data to {path}")
    
    return results


def main() -> int:
    """Run all examples."""
    setup_logging()
    logging.info("NCAA March Madness Pipeline Usage Examples")
    
    try:
        # Run examples sequentially
        example_1_basic_usage()
        example_2_data_selection()
        example_3_data_cleaning()
        
        logging.info("All examples completed successfully")
    except Exception as e:
        logging.exception(f"Error running examples: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 