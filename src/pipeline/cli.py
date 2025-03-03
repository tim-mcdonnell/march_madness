"""
Command-line interface for the NCAA March Madness prediction pipeline.

This module provides the CLI parser and argument handling for the pipeline.
"""

import argparse
import logging
from typing import Any

from src.pipeline.data_management import purge_data

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for the pipeline CLI.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="NCAA March Madness Prediction Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Pipeline stage selection
    parser.add_argument(
        "--stages", 
        nargs="+", 
        choices=["data", "eda", "features", "model", "evaluate", "all"],
        default=["all"], 
        help="Pipeline stages to run"
    )
    
    # Data range options
    parser.add_argument(
        "--years", 
        nargs="+", 
        type=int,
        help="Years to process (default: all years in config)"
    )
    
    parser.add_argument(
        "--categories", 
        nargs="+",
        choices=["play_by_play", "player_box", "schedules", "team_box"],
        help="Data categories to process (default: all)"
    )
    
    # Clean/purge options
    parser.add_argument(
        "--clean-raw", 
        action="store_true",
        help="Purge raw data before running"
    )
    
    parser.add_argument(
        "--clean-processed", 
        action="store_true",
        help="Purge processed data before running"
    )
    
    parser.add_argument(
        "--clean-features", 
        action="store_true",
        help="Purge feature data before running"
    )
    
    parser.add_argument(
        "--clean-models", 
        action="store_true",
        help="Purge trained models before running"
    )
    
    parser.add_argument(
        "--clean-all", 
        action="store_true",
        help="Purge all data before running"
    )
    
    # Configuration options
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/pipeline_config.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--create-config", 
        action="store_true",
        help="Create default configuration file if it doesn't exist"
    )
    
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO", 
        help="Logging level"
    )
    
    return parser


def process_args(args: argparse.Namespace, config: dict[str, Any]) -> dict[str, Any]:
    """
    Process pipeline arguments and execute operations.
    
    Args:
        args: Command-line arguments
        config: Pipeline configuration
        
    Returns:
        dict: Results of pipeline execution
    """
    # Handle data purging
    if args.clean_all:
        purge_data("all", config, args.categories, args.years)
    else:
        if args.clean_raw:
            purge_data("raw", config, args.categories, args.years)
        if args.clean_processed:
            purge_data("processed", config, args.categories, args.years)
        if args.clean_features:
            purge_data("features", config)
        if args.clean_models:
            purge_data("models", config)
    
    # Determine which stages to run
    stages_to_run = args.stages
    if "all" in stages_to_run:
        stages_to_run = ["data", "eda", "features", "model", "evaluate"]
    
    # Run the pipeline stages
    results = {}
    
    # Import here to avoid circular imports
    from src.pipeline.data_stage import run as run_data_stage
    
    # Data stage
    if "data" in stages_to_run:
        logger.info("Running data collection and cleaning stage")
        results["data"] = run_data_stage(
            config, 
            years=args.years,
            categories=args.categories
        )
    
    # Placeholder for other stages
    # These would be implemented as we develop the pipeline further
    if "eda" in stages_to_run:
        logger.info("Exploratory data analysis stage not yet implemented")
        # from src.pipeline.eda_stage import run as run_eda_stage
        # results["eda"] = run_eda_stage(config)
    
    if "features" in stages_to_run:
        logger.info("Feature engineering stage not yet implemented")
        # from src.pipeline.feature_stage import run as run_feature_stage
        # results["features"] = run_feature_stage(config)
    
    if "model" in stages_to_run:
        logger.info("Model development stage not yet implemented")
        # from src.pipeline.model_stage import run as run_model_stage
        # results["model"] = run_model_stage(config)
    
    if "evaluate" in stages_to_run:
        logger.info("Evaluation stage not yet implemented")
        # from src.pipeline.eval_stage import run as run_eval_stage
        # results["evaluate"] = run_eval_stage(config)
    
    return results


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the pipeline.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("pipeline.log"),
            logging.StreamHandler()
        ]
    ) 