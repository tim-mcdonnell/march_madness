"""
Configuration management for the NCAA March Madness prediction pipeline.

This module handles loading, validating, and accessing pipeline configuration.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config/pipeline_config.yaml")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load pipeline configuration from YAML file.
    
    Args:
        config_path: Path to configuration file, or None to use default
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        ValueError: If configuration is invalid
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    else:
        config_path = Path(config_path)
    
    logger.info(f"Loading configuration from {config_path}")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}")
    
    # Validate configuration
    validate_config(config)
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
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


def get_default_config() -> Dict[str, Any]:
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
            "output_dir": "data/features"
        },
        "models": {
            "model_dir": "models",
            "tournament_years": [2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024]
        },
        "evaluation": {
            "output_dir": "visualizations"
        }
    }


def create_default_config(output_path: Optional[str] = None) -> str:
    """
    Create default configuration file.
    
    Args:
        output_path: Path to write configuration file, or None to use default
        
    Returns:
        str: Path to created configuration file
    """
    if output_path is None:
        output_path = DEFAULT_CONFIG_PATH
    else:
        output_path = Path(output_path)
    
    logger.info(f"Creating default configuration at {output_path}")
    
    # Create parent directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get default configuration
    config = get_default_config()
    
    # Write configuration to file
    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return str(output_path) 