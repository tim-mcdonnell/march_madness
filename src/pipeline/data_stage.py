"""
NCAA March Madness - Data Collection and Cleaning Stage

This module handles the data collection and cleaning stage for the NCAA March Madness
prediction pipeline. It downloads the required data and performs initial cleaning
and preprocessing.
"""

import logging
from pathlib import Path
from typing import Any

# Import data loading functions
from src.data.loader import download_all_data, download_year_data

# Import validation functions
from src.data.validation import (
    DataValidationError,
    generate_validation_report,
    validate_data_consistency,
    validate_raw_data,
)

# Import pipeline configuration functions
from src.pipeline.config import (
    get_enabled_categories,
    get_enabled_years,
    get_raw_data_dir,
    get_validation_config,
    get_validation_report_path,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run(
    config: dict[str, Any], 
    years: list[int] | None = None, 
    categories: list[str] | None = None
) -> dict[str, Any]:
    """
    Run the data collection and cleaning stage.
    
    Args:
        config: Pipeline configuration dictionary
        years: List of years to process. If None, uses all years from config.
        categories: List of data categories to process. If None, uses all categories from config.
        
    Returns:
        Dictionary containing the results of the data collection stage
    """
    logger.info("Starting data collection and cleaning stage")
    
    # Ensure necessary directories exist
    raw_dir = Path(config["data"]["raw_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Use years and categories from config if not specified
    if years is None:
        years = config["data"]["years"]
    if categories is None:
        categories = config["data"]["categories"]
    
    logger.info(f"Processing years: {years}")
    logger.info(f"Processing categories: {categories}")
    
    results = {
        "years": years,
        "categories": categories,
        "data": {}
    }
    
    # Check if we're downloading all years or specific years
    is_continuous_range = years == list(range(min(years), max(years) + 1))
    
    if is_continuous_range:
        # Download all data at once for a continuous range of years
        logger.info(f"Downloading data for years {min(years)}-{max(years)}")
        data = download_all_data(
            base_dir=raw_dir,
            categories=categories,
            start_year=min(years),
            end_year=max(years)
        )
        
        for year in years:
            results["data"][year] = {
                "downloaded": True,
                "categories": {}
            }
            for category in categories:
                results["data"][year]["categories"][category] = {
                    "downloaded": category in data[year],
                    "file_path": (
                        str(raw_dir / category / f"{category}_{year}.parquet") 
                        if category in data[year] else None
                    )
                }
    else:
        # Download data for each year individually
        for year in years:
            logger.info(f"Downloading data for year {year}")
            data = download_year_data(
                base_dir=raw_dir,
                categories=categories,
                year=year
            )
            
            results["data"][year] = {
                "downloaded": True,
                "categories": {}
            }
            for category in categories:
                results["data"][year]["categories"][category] = {
                    "downloaded": category in data,
                    "file_path": (
                        str(raw_dir / category / f"{category}_{year}.parquet") 
                        if category in data else None
                    )
                }
    
    logger.info("Data collection and cleaning stage completed")
    return results


def validate_downloaded_data(config: dict[str, Any]) -> bool:
    """
    Validate the downloaded data files against schema and consistency checks.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        True if validation passes, False otherwise
    """
    validation_config = get_validation_config(config)
    
    if not validation_config.get('enabled', True):
        logger.info("Data validation is disabled in configuration")
        return True
    
    raw_data_dir = get_raw_data_dir(config)
    categories = get_enabled_categories(config)
    years = get_enabled_years(config)
    strict = validation_config.get('strict', False)
    strict_optional = validation_config.get('strict_optional', False)
    check_consistency = validation_config.get('check_consistency', True)
    report_path = get_validation_report_path(config)
    
    logger.info(f"Validating data in {raw_data_dir}")
    logger.info(
        f"Validating raw data: categories={categories}, years={years}, "
        f"strict={strict}, strict_optional={strict_optional}"
    )
    
    try:
        # Validate raw data files against schema
        validation_results = validate_raw_data(
            data_dir=raw_data_dir, 
            categories=categories, 
            years=years, 
            strict=strict,
            strict_optional=strict_optional
        )
        
        # Check cross-category data consistency if enabled
        if check_consistency:
            logger.info("Checking data consistency across categories")
            consistency_results = validate_data_consistency(
                data_dir=raw_data_dir, 
                categories=categories, 
                years=years, 
                strict=strict
            )
            
            # Merge consistency results with validation results
            for key, result in consistency_results.items():
                validation_results[f"consistency_{key}"] = result
        
        # Generate validation report if report path is specified
        if report_path:
            generate_validation_report(validation_results, report_path)
            logger.info(f"Validation report written to {report_path}")
        
        # Check if validation passed
        validation_passed = all(
            result.get('valid', False) 
            for result in validation_results.values() 
            if isinstance(result, dict) and 'valid' in result
        )
        
        if validation_passed:
            logger.info("Data validation passed")
        else:
            logger.error("Data validation failed")
            
        return validation_passed
        
    except DataValidationError as e:
        logger.error(f"Data validation error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during data validation: {e}", exc_info=True)
        return False


def process_transformations(config: dict[str, Any]) -> bool:
    """Process data transformations.
    
    This function runs all the data transformation steps:
    1. Team season statistics
    2. Game results
    3. Tournament data
    4. Conference metrics
    5. Bracket history
    6. Merged datasets
    
    Args:
        config: Pipeline configuration
        
    Returns:
        True if processing succeeds, False otherwise
    """
    from src.data.transformer import process_all_transformations
    
    try:
        # Get raw and processed directories from config
        raw_dir = config["data"]["raw_dir"]
        processed_dir = config["data"]["processed_dir"]
        
        # Get years from config
        years = config["data"]["years"]
        
        # Get categories from config
        categories = config["data"]["categories"]
        
        logger.info(f"Processing data transformations for years {years}")
        logger.info(f"Using raw data from {raw_dir}")
        logger.info(f"Saving processed data to {processed_dir}")
        
        # Create the processed directory if it doesn't exist
        Path(processed_dir).mkdir(parents=True, exist_ok=True)
        
        # Run transformations
        results = process_all_transformations(
            years=years,
            categories=categories,
            data_dir=raw_dir,
            processed_dir=processed_dir
        )
        
        # Log the number of rows in each result and group by type
        if results:
            # First log the normalized data files
            normalized_categories = ['team_box', 'schedules', 'player_box', 'play_by_play']
            logger.info("=== Normalized consolidated data files ===")
            for category in normalized_categories:
                if category in results and results[category] is not None:
                    row_count = len(results[category])
                    logger.info(f"Generated normalized {category}.parquet with {row_count} rows")
                    
            # Check if files exist in the processed directory
            for category in normalized_categories:
                file_path = Path(processed_dir) / f"{category}.parquet"
                if file_path.exists():
                    logger.info(f"Verified file exists: {file_path}")
            
            # Then log other derived datasets
            logger.info("=== Derived datasets ===")
            for name, df in results.items():
                if df is not None and name not in normalized_categories:
                    logger.info(f"Generated {name} with {len(df)} rows")
                    
            # Check if team_season_statistics.parquet exists
            team_stats_path = Path(processed_dir) / "team_season_statistics.parquet"
            if team_stats_path.exists():
                logger.info(f"Verified file exists: {team_stats_path}")
        else:
            logger.warning("No datasets were generated during transformation")
        
        logger.info("Data processing completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during data processing: {e}", exc_info=True)
        return False


def run_data_stage(config: dict[str, Any]) -> bool:
    """
    Run the data collection and cleaning stage.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        True if the stage completed successfully, False otherwise
    """
    logger.info("Starting data collection and cleaning stage")
    
    # Download the data
    years = config.get("data", {}).get("years", [])
    categories = config.get("data", {}).get("categories", [])
    
    # Call the run function to download data
    download_results = run(config, years, categories)
    
    if not download_results:
        logger.error("Data download failed, stopping pipeline")
        return False
    
    # Validate downloaded data
    if not validate_downloaded_data(config):
        logger.error("Data validation failed, stopping pipeline")
        return False
    
    # Process data for analysis
    if not process_transformations(config):
        logger.error("Data processing failed, stopping pipeline")
        return False
    
    logger.info("Data stage completed successfully")
    return True


if __name__ == "__main__":
    pass 