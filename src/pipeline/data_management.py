"""
Data management utilities for the NCAA March Madness prediction pipeline.

This module provides functions for managing data files, including purging data
for clean runs of the pipeline.
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def purge_data(
    data_type: str,
    config: dict[str, Any],
    categories: list[str] | None = None,
    years: list[int] | None = None
) -> None:
    """
    Purge data of a specific type.
    
    Args:
        data_type: Type of data to purge (raw, processed, features, models, all)
        config: Pipeline configuration
        categories: Specific data categories to purge, or None for all
        years: Specific years to purge, or None for all
        
    Raises:
        ValueError: If data_type is invalid
    """
    valid_types = ["raw", "processed", "features", "models", "all"]
    if data_type not in valid_types:
        raise ValueError(
            f"Invalid data type: {data_type}. Must be one of {valid_types}"
        )
    
    if data_type == "all":
        # Purge all data types
        for dtype in ["raw", "processed", "features", "models"]:
            purge_data(dtype, config, categories, years)
        return
    
    logger.info(f"Purging {data_type} data")
    
    if data_type == "raw":
        purge_raw_data(config, categories, years)
    elif data_type == "processed":
        purge_processed_data(config, categories, years)
    elif data_type == "features":
        purge_feature_data(config)
    elif data_type == "models":
        purge_model_data(config)


def purge_raw_data(
    config: dict[str, Any],
    categories: list[str] | None = None,
    years: list[int] | None = None
) -> None:
    """
    Purge raw data files.
    
    Args:
        config: Pipeline configuration
        categories: Specific data categories to purge, or None for all
        years: Specific years to purge, or None for all
    """
    raw_dir = Path(config["data"]["raw_dir"])
    
    if not raw_dir.exists():
        logger.warning(f"Raw data directory does not exist: {raw_dir}")
        return
    
    # Use all categories if none specified
    if categories is None:
        categories = config["data"]["categories"]
    
    # Process each category
    for category in categories:
        category_dir = raw_dir / category
        
        if not category_dir.exists():
            logger.warning(f"Category directory does not exist: {category_dir}")
            continue
        
        # If years specified, delete specific files, otherwise delete all files 
        # in category
        if years is not None:
            for year in years:
                # The file pattern depends on the category
                if category == "schedules":
                    file_pattern = f"mbb_schedule_{year}.parquet"
                else:
                    file_pattern = f"{category}_{year}.parquet"
                
                file_path = category_dir / file_pattern
                
                if file_path.exists():
                    logger.info(f"Deleting file: {file_path}")
                    file_path.unlink()
        else:
            # Delete all files in category directory
            for file_path in category_dir.glob("*.parquet"):
                logger.info(f"Deleting file: {file_path}")
                file_path.unlink()


def purge_processed_data(
    config: dict[str, Any],
    categories: list[str] | None = None,
    years: list[int] | None = None
) -> None:
    """
    Purge processed data files.
    
    Args:
        config: Pipeline configuration
        categories: Specific data categories to purge, or None for all
        years: Specific years to purge, or None for all
    """
    processed_dir = Path(config["data"]["processed_dir"])
    
    if not processed_dir.exists():
        logger.warning(f"Processed data directory does not exist: {processed_dir}")
        return
    
    # Use all categories if none specified
    if categories is None:
        categories = config["data"]["categories"]
    
    # Process each category and year
    for file_path in processed_dir.glob("*.parquet"):
        filename = file_path.name
        
        # Check if file matches category and year filters
        should_delete = False
        
        # Extract category and year from filename 
        # (e.g., "play_by_play_2023_cleaned.parquet")
        file_parts = filename.split('_')
        
        if len(file_parts) >= 3:
            # Reconstruct the category (might be multiple parts)
            category_parts = []
            year_found = False
            
            for part in file_parts:
                # Check if this part could be a year
                if not year_found and part.isdigit() and len(part) == 4:
                    file_year = int(part)
                    year_found = True
                elif not year_found:
                    category_parts.append(part)
            
            file_category = '_'.join(category_parts)
            
            # Determine if file should be deleted based on categories and years filters
            if categories is not None and file_category not in categories:
                should_delete = False
            elif years is not None and (not year_found or file_year not in years):
                should_delete = False
            else:
                should_delete = True
        else:
            # If filename doesn't match expected pattern, include it by default
            should_delete = True
        
        # Delete file if it matches filters
        if should_delete:
            logger.info(f"Deleting file: {file_path}")
            file_path.unlink()


def purge_feature_data(config: dict[str, Any]) -> None:
    """
    Purge feature data files.
    
    Args:
        config: Pipeline configuration
    """
    if "features" not in config or "output_dir" not in config["features"]:
        logger.warning("Feature configuration not found in config")
        return
    
    feature_dir = Path(config["features"]["output_dir"])
    
    if not feature_dir.exists():
        logger.warning(f"Feature directory does not exist: {feature_dir}")
        return
    
    # Delete all files in feature directory
    for file_path in feature_dir.glob("*.parquet"):
        logger.info(f"Deleting file: {file_path}")
        file_path.unlink()


def purge_model_data(config: dict[str, Any]) -> None:
    """
    Purge model data files.
    
    Args:
        config: Pipeline configuration
    """
    if "models" not in config or "model_dir" not in config["models"]:
        logger.warning("Model configuration not found in config")
        return
    
    model_dir = Path(config["models"]["model_dir"])
    
    if not model_dir.exists():
        logger.warning(f"Model directory does not exist: {model_dir}")
        return
    
    # Delete all model files
    for file_path in model_dir.glob("*.pkl"):
        logger.info(f"Deleting file: {file_path}")
        file_path.unlink()
    
    for file_path in model_dir.glob("*.pt"):
        logger.info(f"Deleting file: {file_path}")
        file_path.unlink()


def ensure_directories(config: dict[str, Any]) -> None:
    """
    Ensure all required directories exist.
    
    Args:
        config: Pipeline configuration
    """
    # Data directories
    Path(config["data"]["raw_dir"]).mkdir(parents=True, exist_ok=True)
    Path(config["data"]["processed_dir"]).mkdir(parents=True, exist_ok=True)
    
    # Features directory
    if "features" in config and "output_dir" in config["features"]:
        Path(config["features"]["output_dir"]).mkdir(parents=True, exist_ok=True)
    
    # Model directory
    if "models" in config and "model_dir" in config["models"]:
        Path(config["models"]["model_dir"]).mkdir(parents=True, exist_ok=True)
    
    # Evaluation directory
    if "evaluation" in config and "output_dir" in config["evaluation"]:
        Path(config["evaluation"]["output_dir"]).mkdir(parents=True, exist_ok=True) 