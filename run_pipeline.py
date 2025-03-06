#!/usr/bin/env python
"""
NCAA March Madness Prediction Pipeline

Main entry point for running the prediction pipeline. 
This script provides a CLI for selecting pipeline stages, configuring data range,
and setting clean/purge options.

Example usage:
    # Run the full pipeline (creates default config automatically if needed)
    python run_pipeline.py
    
    # Run only the data collection stage
    python run_pipeline.py --stages data
    
    # Run data and feature engineering with specific years
    python run_pipeline.py --stages data features --years 2023 2024
    
    # Clean raw data before running
    python run_pipeline.py --clean-raw
    
    # Clean all data and run the full pipeline
    python run_pipeline.py --clean-all
    
    # Create a custom config without running the pipeline
    python run_pipeline.py --create-config --no-run
"""

import logging
import sys

from src.pipeline.cli import create_parser, process_args, setup_logging
from src.pipeline.config import create_default_config, load_config


def main() -> int:
    """
    Main entry point for the pipeline.
    
    Returns:
        int: Exit code
    """
    # Parse command-line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("NCAA March Madness Prediction Pipeline")
    
    try:
        # Create default config if requested or if it doesn't exist
        config_path = args.config
        config_created = False
        
        if args.create_config:
            logger.info(f"Creating default configuration at {config_path}")
            create_default_config(config_path)
            logger.info(f"Default configuration created at {config_path}")
            config_created = True
            
            # Exit if user just wants to create config without running
            if args.no_run:
                logger.info("Configuration created. Exiting without running pipeline.")
                return 0
        
        # Load configuration
        try:
            config = load_config(config_path)
            logger.info(f"Loaded configuration from {config_path}")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            logger.info("Creating a default configuration file...")
            create_default_config(config_path)
            config = load_config(config_path)
            logger.info(f"Created and loaded default configuration at {config_path}")
            config_created = True
        
        # Process arguments and run pipeline
        results = process_args(args, config)
        
        if not results:
            logger.warning("No pipeline stages were executed")
            return 1
        
        # Log completion
        logger.info("Pipeline completed successfully")
        return 0
    
    except Exception as e:
        logger.exception(f"Error running pipeline: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 