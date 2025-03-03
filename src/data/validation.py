"""
NCAA March Madness Data Validation Module

This module provides functions to validate the NCAA basketball data
during the data loading and processing stage of the pipeline.
"""

import logging
from pathlib import Path
from typing import Any

import polars as pl

from src.data.schema import (
    SCHEMA_MAP,
    get_schema_summary,
    validate_file,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Exception raised for data validation errors."""
    pass


def _extract_year_from_filename(file_path: Path, category: str) -> int | None:
    """
    Extract year from a file name based on its category.
    
    Args:
        file_path: Path to the file
        category: Data category 
        
    Returns:
        Extracted year as integer, or None if extraction fails
    """
    try:
        if category == 'schedules':
            # Schedule files are named like 'mbb_schedule_YYYY.parquet'
            file_year = int(file_path.stem.split('_')[-1])
        else:
            # Other files are named like 'category_YYYY.parquet'
            file_year = int(file_path.stem.split('_')[-1])
        return file_year
    except (ValueError, IndexError):
        logger.warning(f"Could not extract year from file name: {file_path.name}")
        return None


def _filter_files_by_year(files: list[Path], category: str, years: list[int] | None) -> list[Path]:
    """
    Filter files by year.
    
    Args:
        files: List of file paths
        category: Data category
        years: List of years to include, or None for all years
        
    Returns:
        List of filtered file paths
    """
    filtered_files = []
    
    for file_path in files:
        file_year = _extract_year_from_filename(file_path, category)
        if file_year is not None and (years is None or file_year in years):
            filtered_files.append(file_path)
            
    return filtered_files


def _validate_files_for_category(
    category: str, 
    category_dir: Path, 
    years: list[int] | None, 
    strict_optional: bool,
    validation_failures: list[str]
) -> dict[str, dict[str, Any]]:
    """
    Validate all files for a specific category.
    
    Args:
        category: Data category
        category_dir: Directory containing files for this category
        years: List of years to validate, or None for all years
        strict_optional: Whether to treat optional columns as required
        validation_failures: List to collect validation failure messages
        
    Returns:
        Dictionary with validation results for each file
    """
    results = {}
    
    # Get all parquet files for this category
    all_files = list(category_dir.glob('*.parquet'))
    
    # Filter files by year if specified
    category_files = _filter_files_by_year(all_files, category, years)
    
    if not category_files:
        logger.info(
            f"No files found for category {category}" + 
            (f" and years {years}" if years else "")
        )
        return results
    
    # Validate each file
    for file_path in category_files:
        valid, errors = validate_file(file_path, category, strict_optional=strict_optional)
        
        results[str(file_path)] = {
            'valid': valid,
            'errors': errors,
            'category': category
        }
        
        if valid:
            logger.info(f"Validation passed: {file_path}")
        else:
            err_msg = f"Validation failed for {file_path}: {errors}"
            logger.error(err_msg)
            validation_failures.append(err_msg)
    
    return results


def validate_raw_data(
    data_dir: str | Path, 
    categories: list[str] = None, 
    years: list[int] = None, 
    strict: bool = False, 
    strict_optional: bool = False
) -> dict[str, dict[str, Any]]:
    """
    Validate raw data files for specified categories and years.
    
    Args:
        data_dir: Directory containing raw data files
        categories: List of data categories to validate. If None, all categories will be validated.
        years: List of years to validate. If None, all available years will be validated.
        strict: If True, raises an exception if any validation fails
        strict_optional: If True, treat optional columns as required
    
    Returns:
        Dictionary containing validation results
        
    Raises:
        DataValidationError: If validation fails and strict is True
    """
    data_dir = Path(data_dir)
    
    if not categories:
        categories = list(SCHEMA_MAP.keys())
    
    results = {}
    validation_failures = []
    
    for category in categories:
        category_dir = data_dir / category
        if not category_dir.exists():
            logger.warning(f"Category directory not found: {category_dir}")
            continue
        
        # Validate files for this category
        category_results = _validate_files_for_category(
            category, category_dir, years, strict_optional, validation_failures
        )
        results.update(category_results)
    
    # Check if there were any validation failures
    if validation_failures and strict:
        raise DataValidationError("Data validation failed:\n" + "\n".join(validation_failures))
    
    return results


def validate_dataframe(
    df: pl.DataFrame, 
    category: str, 
    strict: bool = False, 
    strict_optional: bool = False
) -> tuple[bool, list[str]]:
    """
    Validate a dataframe against the schema for a given category.
    
    Args:
        df: The dataframe to validate
        category: The data category
        strict: If True, raises an exception if validation fails
        strict_optional: If True, treat optional columns as required
    
    Returns:
        Tuple containing:
            - Boolean indicating if validation passed
            - List of error messages if validation failed
    
    Raises:
        DataValidationError: If validation fails and strict is True
    """
    from src.data.schema import validate_schema
    
    valid, errors = validate_schema(df, category, strict_optional=strict_optional)
    
    if valid:
        logger.info(f"DataFrame validation passed for category: {category}")
    else:
        error_msg = f"DataFrame validation failed for category {category}: {errors}"
        logger.error(error_msg)
        
        if strict:
            raise DataValidationError(error_msg)
    
    return valid, errors


def _load_schedule_game_ids(data_dir: Path, years: list[int] | None) -> dict[int, set[str]]:
    """
    Load game IDs from schedule files for specified years.
    
    Args:
        data_dir: Directory containing raw data files
        years: List of years to load, or None for all years
        
    Returns:
        Dictionary mapping years to sets of game IDs
    """
    schedule_game_ids = {}
    
    if not years:
        return schedule_game_ids
    
    for year in years:
        schedule_file = data_dir / 'schedules' / f'mbb_schedule_{year}.parquet'
        if schedule_file.exists():
            try:
                df = pl.read_parquet(schedule_file)
                schedule_game_ids[year] = set(df['game_id'].to_list())
            except Exception as e:
                logger.error(f"Error reading schedule file {schedule_file}: {e}")
    
    return schedule_game_ids


def _check_game_id_consistency(
    data_dir: Path,
    category: str,
    year: int,
    schedule_ids: set[str]
) -> tuple[bool, dict[str, Any], str | None]:
    """
    Check if all game IDs in a category file exist in the schedule for that year.
    
    Args:
        data_dir: Directory containing raw data files
        category: Data category to check
        year: Year to check
        schedule_ids: Set of game IDs from the schedule for this year
        
    Returns:
        Tuple containing:
            - Boolean indicating if all game IDs are consistent
            - Dictionary with validation results
            - Error message if validation failed, or None if successful
    """
    file_pattern = f"{category}_{year}.parquet"
    category_file = data_dir / category / file_pattern
    
    if not category_file.exists():
        return True, {}, None
    
    try:
        df = pl.read_parquet(category_file)
        category_game_ids = set(df['game_id'].to_list())
        
        # Check if all game IDs in this category exist in schedules
        missing_ids = category_game_ids - schedule_ids
        
        if missing_ids:
            err_msg = (
                f"Found {len(missing_ids)} game IDs in {category} "
                f"that don't exist in schedules for year {year}"
            )
            result = {
                'valid': False,
                'missing_ids': list(missing_ids)
            }
            return False, result, err_msg
            
        result = {
            'valid': True,
            'total_ids': len(category_game_ids)
        }
        return True, result, None
    
    except Exception as e:
        err_msg = f"Error checking consistency for {category_file}: {e}"
        logger.error(err_msg)
        return False, {}, err_msg


def validate_data_consistency(
    data_dir: str | Path, 
    categories: list[str] = None, 
    years: list[int] = None, 
    strict: bool = False, 
    strict_optional: bool = False
) -> dict[str, dict[str, Any]]:
    """
    Validate consistency across different data categories.
    
    Args:
        data_dir: Directory containing raw data files
        categories: List of categories to validate. If None, all categories will be validated.
        years: List of years to validate. If None, all available years will be validated.
        strict: If True, raises an exception if any consistency check fails
        strict_optional: If True, treat optional columns as required (unused)
    
    Returns:
        Dictionary containing consistency validation results
        
    Raises:
        DataValidationError: If validation fails and strict is True
    """
    data_dir = Path(data_dir)
    
    if not categories:
        categories = list(SCHEMA_MAP.keys())
    
    results = {}
    validation_failures = []
    
    # Load game IDs from schedules
    schedule_game_ids = _load_schedule_game_ids(data_dir, years)
    
    # Validate that all game IDs in other categories exist in schedules
    for category in [c for c in categories if c != 'schedules']:
        for year in years or []:
            if year not in schedule_game_ids:
                continue
                
            consistency_key = f"{category}_{year}_game_ids"
            valid, result, error = _check_game_id_consistency(
                data_dir, category, year, schedule_game_ids[year]
            )
            
            results[consistency_key] = result
            
            if not valid and error:
                validation_failures.append(error)
            elif valid:
                logger.info(f"All game IDs in {category} for year {year} exist in schedules")
    
    # Check if there were any validation failures
    if validation_failures and strict:
        raise DataValidationError(
            "Data consistency validation failed:\n" + "\n".join(validation_failures)
        )
    
    return results


def generate_validation_report(validation_results: dict[str, dict[str, Any]], 
                               output_path: str | Path = None) -> str:
    """
    Generate a human-readable validation report.
    
    Args:
        validation_results: Results from validate_raw_data
        output_path: Path to write the report. If None, report is only returned as a string.
        
    Returns:
        Report as a string
    """
    # Get schema summary for reference
    schema_summary = get_schema_summary()
    
    report_lines = [
        "# NCAA March Madness Data Validation Report",
        "",
        f"Generated at: {logging.Formatter().converter()}",
        "",
        "## Schema Summary",
        ""
    ]
    
    # Add schema summary
    for category, info in schema_summary.items():
        report_lines.extend([
            f"### {category.upper()}",
            f"- Core columns: {info['core_columns']}",
            f"- Optional columns: {info['optional_columns']}",
            f"- Total columns: {info['total_columns']}",
            ""
        ])
    
    # Add validation results
    report_lines.extend([
        "## Validation Results",
        ""
    ])
    
    # Group results by category
    results_by_category = {}
    for file_path, result in validation_results.items():
        category = result.get('category', 'unknown')
        if category not in results_by_category:
            results_by_category[category] = []
        results_by_category[category].append((file_path, result))
    
    # Add results for each category
    for category, results in results_by_category.items():
        report_lines.extend([
            f"### {category.upper()}",
            ""
        ])
        
        valid_count = sum(1 for _, result in results if result.get('valid', False))
        report_lines.append(f"- Files validated: {len(results)}")
        report_lines.append(f"- Valid files: {valid_count}")
        report_lines.append(f"- Invalid files: {len(results) - valid_count}")
        report_lines.append("")
        
        if len(results) - valid_count > 0:
            report_lines.append("#### Validation Errors")
            report_lines.append("")
            
            for file_path, result in results:
                if not result.get('valid', False):
                    report_lines.append(f"**File:** {file_path}")
                    for error in result.get('errors', []):
                        report_lines.append(f"- {error}")
                    report_lines.append("")
    
    report = "\n".join(report_lines)
    
    # Write report to file if output path is provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Validation report written to {output_path}")
    
    return report


def validate_file_schema(
    file_path: str | Path, 
    category: str, 
    strict: bool = False, 
    strict_optional: bool = False
) -> tuple[bool, list[str]]:
    """
    Validate a file against the schema for a given category.
    
    Args:
        file_path: The file path to validate
        category: The data category
        strict: If True, raises an exception if validation fails
        strict_optional: If True, treat optional columns as required
    
    Returns:
        Tuple containing:
            - Boolean indicating if validation passed
            - List of error messages if validation failed
    
    Raises:
        DataValidationError: If validation fails and strict is True
    """
    from src.data.schema import validate_schema
    
    valid, errors = validate_schema(file_path, category, strict_optional=strict_optional)
    
    if valid:
        logger.info(f"File validation passed for category: {category}")
    else:
        error_msg = f"File validation failed for category {category}: {errors}"
        logger.error(error_msg)
        
        if strict:
            raise DataValidationError(error_msg)
    
    return valid, errors


if __name__ == "__main__":
    
    # Example usage
    data_dir = Path("data/raw")
    if data_dir.exists():
        results = validate_raw_data(data_dir)
        report = generate_validation_report(results)
    else:
        pass 