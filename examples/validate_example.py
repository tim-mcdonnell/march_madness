#!/usr/bin/env python
"""
Example of using the NCAA March Madness Data Validation Framework.

This script demonstrates how to use the validation framework to:
1. Validate a single data file
2. Validate all data files in a directory
3. Check data consistency across categories
4. Generate a validation report
"""

import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data.schema import get_schema_summary, validate_file
from src.data.validation import (
    generate_validation_report,
    validate_data_consistency,
    validate_raw_data,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Example data directories
RAW_DATA_DIR = Path("data/raw")
REPORT_DIR = Path("validation_reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def example_validate_single_file() -> None:
    """Example of validating a single data file."""
    logger.info("Example 1: Validating a single data file")
    
    # Specify the file to validate
    category = "team_box"
    year = 2023
    file_path = RAW_DATA_DIR / category / f"{category}_{year}.parquet"
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        logger.info("Please download the data first by running the pipeline")
        return
    
    # Validate the file
    valid, errors = validate_file(file_path, category)
    
    # Print results
    if valid:
        logger.info(f"Validation PASSED for {file_path}")
    else:
        logger.error(f"Validation FAILED for {file_path}")
        for error in errors:
            logger.error(f"  - {error}")


def example_validate_all_files() -> None:
    """Example of validating all data files for a specific year."""
    logger.info("\nExample 2: Validating all data files for a specific year")
    
    # Specify year and categories
    year = 2023
    categories = ["play_by_play", "player_box", "schedules", "team_box"]
    
    # Validate all files
    validation_results = validate_raw_data(
        data_dir=RAW_DATA_DIR,
        years=[year],
        categories=categories,
        strict=False
    )
    
    # Count valid and invalid files
    valid_count = sum(1 for result in validation_results.values() if result.get("valid", False))
    invalid_count = len(validation_results) - valid_count
    
    # Print summary
    logger.info(f"Validated {len(validation_results)} files:")
    logger.info(f"  - Valid: {valid_count}")
    logger.info(f"  - Invalid: {invalid_count}")
    
    # Generate a report
    report_path = REPORT_DIR / f"validation_report_{year}.md"
    generate_validation_report(validation_results, report_path)
    logger.info(f"Report generated: {report_path}")


def example_check_consistency() -> None:
    """Example of checking data consistency across categories."""
    logger.info("\nExample 3: Checking data consistency across categories")
    
    # Specify year
    year = 2023
    
    # Check consistency
    consistency_results = validate_data_consistency(
        data_dir=RAW_DATA_DIR,
        years=[year],
        strict=False
    )
    
    # Print summary
    if not consistency_results.get("errors"):
        logger.info("No consistency errors found")
    else:
        logger.error(f"Found {len(consistency_results['errors'])} consistency errors:")
        for error in consistency_results["errors"]:
            logger.error(f"  - {error}")
    
    # Check for missing game IDs
    for key, value in consistency_results.get("game_id_consistency", {}).items():
        if value:
            logger.warning(f"{key}: {len(value)} missing IDs")


def example_schema_summary() -> None:
    """Example of getting a schema summary."""
    logger.info("\nExample 4: Getting schema information")
    
    # Get schema summary
    summary = get_schema_summary()
    
    # Print summary
    for category, info in summary.items():
        logger.info(f"{category.upper()} Schema:")
        logger.info(f"  - Total columns: {info['total_columns']}")
        logger.info("  - Column types:")
        for type_name, count in info['type_counts'].items():
            logger.info(f"    - {type_name}: {count}")


if __name__ == "__main__":
    logger.info("NCAA March Madness Data Validation Examples")
    
    # Check if data directory exists
    if not RAW_DATA_DIR.exists():
        logger.error(f"Data directory not found: {RAW_DATA_DIR}")
        logger.info("Please download the data first by running the pipeline")
        sys.exit(1)
    
    # Run examples
    example_schema_summary()
    example_validate_single_file()
    example_validate_all_files()
    example_check_consistency()
    
    logger.info("\nAll examples completed") 