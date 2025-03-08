"""Feature generation script for March Madness predictor."""

import argparse
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
    
    # Load the required data
    logger.info("Loading team season statistics")
    team_season_stats = pl.read_parquet("data/processed/team_season_statistics.parquet")
    
    logger.info("Loading team box scores")
    team_box = pl.read_parquet("data/processed/team_box.parquet")
    
    # Build the features
    logger.info("Building features")
    features = feature_builder.build_features(team_season_stats, team_box)
    
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
        default="team_performance.parquet",
        help="Filename to use (without extension)"
    )
    parser.add_argument(
        "--recent-form-games",
        type=int,
        default=10,
        help="Number of games to consider for recent form calculation"
    )
    
    args = parser.parse_args()
    
    # Create config dict from arguments
    config = {
        "recent_form_games": args.recent_form_games,
        "output_file": args.output_filename,
    }
    
    # Generate the features
    output_path = generate_features(
        args.feature_set,
        args.output_dir,
        args.output_filename,
        config
    )
    
    logger.info(f"Features saved to {output_path}")


if __name__ == "__main__":
    main() 