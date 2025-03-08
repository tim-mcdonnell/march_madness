"""
Configuration management for the NCAA March Madness prediction pipeline.

This module handles loading, validating, and accessing pipeline configuration.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config/pipeline_config.yaml")


class PipelineConfigurationError(Exception):
    """Exception raised for pipeline configuration errors."""
    pass


def load_config(config_path: str | Path) -> dict[str, Any]:
    """
    Load the pipeline configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        dict: The configuration as a dictionary
        
    Raises:
        PipelineConfigurationError: If the configuration file doesn't exist or isn't valid
    """
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            
        # Validate required configuration sections
        required_sections = ['data', 'pipeline']
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            raise PipelineConfigurationError(
                f"Missing required configuration sections: {missing_sections}"
            )
            
        return config
        
    except FileNotFoundError as e:
        raise PipelineConfigurationError(f"Configuration file not found: {config_path}") from e
    except yaml.YAMLError as e:
        raise PipelineConfigurationError(f"Error parsing configuration file: {e}") from e


def get_data_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Extract data-related configuration parameters.
    
    Args:
        config: Pipeline configuration dict
        
    Returns:
        Data configuration dict
    """
    return config.get('data', {})


def get_validation_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Extract validation-related configuration parameters.
    
    Args:
        config: Pipeline configuration dict
        
    Returns:
        Validation configuration dict with defaults applied
    """
    validation_config = config.get('data', {}).get('validation', {})
    
    # Set defaults for validation configuration
    validation_config.setdefault('enabled', True)
    validation_config.setdefault('strict', False)
    validation_config.setdefault('strict_optional', False)
    validation_config.setdefault('categories', None)  # None means all categories
    validation_config.setdefault('years', None)  # None means all years
    validation_config.setdefault('check_consistency', True)
    
    return validation_config


def get_pipeline_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Extract pipeline execution configuration parameters.
    
    Args:
        config: Pipeline configuration dict
        
    Returns:
        Pipeline execution configuration dict
    """
    return config.get('pipeline', {})


def get_raw_data_dir(config: dict[str, Any]) -> Path:
    """
    Get the raw data directory from the configuration.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        Path to the raw data directory
        
    Raises:
        PipelineConfigurationError: If raw data directory is not specified
    """
    data_config = get_data_config(config)
    raw_data_dir = data_config.get('raw_dir')
    
    if not raw_data_dir:
        raise PipelineConfigurationError("Raw data directory not specified in configuration")
        
    return Path(raw_data_dir)


def get_processed_data_dir(config: dict[str, Any]) -> Path:
    """
    Get the processed data directory path from configuration.
    
    Args:
        config: Pipeline configuration dict
        
    Returns:
        Path to processed data directory
        
    Raises:
        PipelineConfigurationError: If processed data directory is not specified
    """
    data_config = get_data_config(config)
    processed_data_dir = data_config.get('processed_dir')
    
    if not processed_data_dir:
        raise PipelineConfigurationError("Processed data directory not specified in configuration")
        
    return Path(processed_data_dir)


def get_validation_report_path(config: dict[str, Any]) -> Path | None:
    """
    Get the validation report output path from configuration.
    
    Args:
        config: Pipeline configuration dict
        
    Returns:
        Path to validation report or None if not specified
    """
    validation_config = get_validation_config(config)
    report_path = validation_config.get('report_path')
    
    if report_path:
        return Path(report_path)
    return None


def get_enabled_categories(config: dict[str, Any]) -> list[str] | None:
    """
    Get the list of enabled data categories from configuration.
    
    Args:
        config: Pipeline configuration dict
        
    Returns:
        List of enabled categories or None if all categories are enabled
    """
    validation_config = get_validation_config(config)
    return validation_config.get('categories')


def get_enabled_years(config: dict[str, Any]) -> list[int] | None:
    """
    Get the list of enabled years from configuration.
    
    Args:
        config: Pipeline configuration dict
        
    Returns:
        List of enabled years or None if all years are enabled
    """
    validation_config = get_validation_config(config)
    return validation_config.get('years')


def validate_config(config: dict[str, Any]) -> None:
    """
    Validate pipeline configuration.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Check for required sections
    required_sections = ["data"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate data section
    data_section = config["data"]
    required_data_fields = ["raw_dir", "processed_dir"]
    for field in required_data_fields:
        if field not in data_section:
            raise ValueError(f"Missing required field in data configuration: {field}")
    
    # Set default values if not present
    if "years" not in data_section:
        data_section["years"] = list(range(2003, 2026))  # Default: 2003-2025
        
    if "categories" not in data_section:
        data_section["categories"] = [
            "play_by_play", "player_box", "schedules", "team_box"
        ]


def get_default_config() -> dict[str, Any]:
    """
    Get default pipeline configuration.
    
    Returns:
        dict: Default configuration dictionary
    """
    return {
        "data": {
            "raw_dir": "data/raw",
            "processed_dir": "data/processed",
            "years": list(range(2003, 2026)),  # 2003-2025
            "categories": [
                "play_by_play", 
                "player_box", 
                "schedules", 
                "team_box"
            ]
        },
        "features": {
            "output_dir": "data/features",
            "enabled_feature_sets": ["foundation"],
            "foundation": {
                "recent_form_games": 10
            }
        },
        "models": {
            "model_dir": "models",
            "tournament_years": [2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024]
        },
        "evaluation": {
            "output_dir": "visualizations"
        }
    }


def create_default_config(output_path: str | None = None) -> str:
    """
    Create default configuration file.
    
    Args:
        output_path: Path to write configuration file, or None to use default
        
    Returns:
        str: Path to created configuration file
    """
    output_path = DEFAULT_CONFIG_PATH if output_path is None else Path(output_path)
    
    logger.info(f"Creating default configuration at {output_path}")
    
    # Create parent directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get default configuration
    config = get_default_config()
    
    # Write configuration to file
    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return str(output_path) 