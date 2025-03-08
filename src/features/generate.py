"""Feature generation script for March Madness predictor."""

import argparse
import inspect
import logging
from pathlib import Path

import polars as pl

from src.features import create_feature_builder, get_available_feature_builders
from src.features.data_quality import validate_features

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_features(
    feature_set: str, 
    output_dir: str = "data/features",
    output_filename: str | None = None,
    config: dict[str, object] | None = None,
    validate_quality: bool = True
) -> Path:
    """Generate features using the specified feature builder.
    
    Args:
        feature_set: Name of the feature set to generate
        output_dir: Directory to save the features to
        output_filename: Filename to use (without extension)
        config: Configuration parameters
        validate_quality: Whether to validate feature quality before saving
        
    Returns:
        Path to the saved feature file
    """
    logger.info(f"Generating {feature_set} features")
    
    # Create the feature builder
    feature_builder = create_feature_builder(feature_set, config)
    
    # Determine required data based on build_features signature
    build_features_sig = inspect.signature(feature_builder.build_features)
    param_names = list(build_features_sig.parameters.keys())
    
    # Common data files for all feature builders
    data_files = {
        "team_season_stats": "data/processed/team_season_statistics.parquet",
        "team_box": "data/processed/team_box.parquet",
    }
    
    # Additional files for specific feature sets
    if feature_set == "efficiency" or "schedules" in param_names:
        data_files["schedules"] = "data/processed/schedules.parquet"
    
    # For phase 2 efficiency metrics, we need team_performance from phase 1
    if feature_set == "efficiency":
        data_files["team_performance"] = "data/features/team_performance.parquet"
    
    # Load required data
    loaded_data = {}
    for param_name, file_path in data_files.items():
        logger.info(f"Loading {param_name} from {file_path}")
        loaded_data[param_name] = pl.read_parquet(file_path)
    
    # Match parameters to build_features signature
    build_args = {}
    for param in param_names:
        if param in loaded_data:
            build_args[param] = loaded_data[param]
        else:
            logger.warning(f"Required parameter {param} not found in loaded data")
    
    # Build the features
    logger.info(f"Building features using {feature_set} builder")
    features = feature_builder.build_features(**build_args)
    
    # Validate feature quality if requested
    if validate_quality:
        logger.info("Validating feature quality")
        
        # Get validation configuration
        validation_config = config.get("validation", {}) if config else {}
        raise_errors = validation_config.get("raise_errors", False)
        
        # Validate features using configuration
        quality_ok = validate_features(
            features,
            config=config,
            raise_errors=raise_errors
        )
        
        if quality_ok:
            logger.info("Feature quality validation passed")
        else:
            logger.warning("Feature quality validation found issues (see warnings above)")
            
            # If configured to stop on validation failure
            if validation_config.get("abort_on_failure", False):
                raise ValueError("Feature quality validation failed")
    
    # Save the features
    logger.info(f"Saving features to {output_dir}")
    output_path = feature_builder.save_features(
        features, output_dir, output_filename
    )
    
    logger.info(f"Features saved to {output_path}")
    return output_path


def main() -> None:
    """Main entry point for feature generation."""
    parser = argparse.ArgumentParser(description="Generate features for March Madness predictor")
    parser.add_argument(
        "--feature-set", 
        type=str, 
        default="foundation",
        choices=get_available_feature_builders(),
        help="Name of the feature set to generate"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="data/features",
        help="Directory to save the features to"
    )
    parser.add_argument(
        "--output-filename", 
        type=str, 
        default=None,
        help="Filename to use (without extension, defaults to feature set name)"
    )
    
    # Foundation-specific parameters
    parser.add_argument(
        "--recent-form-games",
        type=int,
        default=10,
        help="Number of games to consider for recent form calculation"
    )
    
    # Efficiency-specific parameters
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations for efficiency rating adjustments"
    )
    parser.add_argument(
        "--min-possessions",
        type=int,
        default=100,
        help="Minimum possessions for efficiency rating reliability"
    )
    
    args = parser.parse_args()
    
    # Create config dict from arguments
    config = {
        "recent_form_games": args.recent_form_games,
        "iterations": args.iterations,
        "min_possessions": args.min_possessions,
    }
    
    # Set default output filename based on feature set if not provided
    output_filename = args.output_filename
    if output_filename is None:
        # Always use team_performance.parquet as the default output file
        # to maintain a single consolidated features file
        output_filename = "team_performance.parquet"
    
    config["output_file"] = output_filename
    
    # Generate the features
    output_path = generate_features(
        args.feature_set,
        args.output_dir,
        output_filename,
        config
    )
    
    logger.info(f"Features saved to {output_path}")


if __name__ == "__main__":
    main() 