"""
NCAA March Madness - Feature Engineering Stage

This module handles the feature engineering stage for the NCAA March Madness
prediction pipeline. It builds and transforms features using the feature builders
defined in the src/features module.
"""

import logging
from pathlib import Path
from typing import Any

# Import feature generation functions
from src.features import get_available_feature_builders
from src.features.generate import generate_features

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run(
    config: dict[str, Any],
    feature_sets: list[str] | None = None
) -> dict[str, Any]:
    """
    Run the feature engineering stage.
    
    Args:
        config: Pipeline configuration dictionary
        feature_sets: List of feature sets to generate (default: all enabled in config)
        
    Returns:
        Dictionary with feature generation results
    """
    logger.info("Starting feature engineering stage")
    
    # Get configuration
    feature_config = config.get("features", {})
    output_dir = feature_config.get("output_dir", "data/features")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Determine which feature sets to generate
    enabled_feature_sets = feature_config.get("enabled_feature_sets", ["foundation"])
    if feature_sets is None:
        feature_sets = enabled_feature_sets
    else:
        # Only generate feature sets that are both specified and enabled
        feature_sets = [fs for fs in feature_sets if fs in enabled_feature_sets]
    
    if not feature_sets:
        logger.warning("No feature sets selected for generation")
        return {"success": False, "message": "No feature sets selected"}
    
    available_builders = get_available_feature_builders()
    logger.info(f"Available feature builders: {', '.join(available_builders)}")
    
    # Generate each feature set
    results = {}
    for feature_set in feature_sets:
        if feature_set not in available_builders:
            logger.warning(f"Feature set '{feature_set}' not available. Skipping.")
            results[feature_set] = {"success": False, "message": "Feature set not available"}
            continue
        
        logger.info(f"Generating features for '{feature_set}'")
        try:
            # Get feature-specific configuration
            feature_specific_config = feature_config.get(feature_set, {})
            
            # Get the output filename (default to team_performance.parquet for backward compatibility)
            output_filename = feature_specific_config.get("output_file", "team_performance.parquet")
            
            # Generate features
            output_path = generate_features(
                feature_set=feature_set,
                output_dir=output_dir,
                output_filename=output_filename,  # Pass the configured filename
                config=feature_specific_config
            )
            
            logger.info(f"Successfully generated features for '{feature_set}' at {output_path}")
            results[feature_set] = {
                "success": True,
                "output_path": str(output_path)
            }
        except Exception as e:
            logger.error(f"Error generating features for '{feature_set}': {e}")
            results[feature_set] = {
                "success": False,
                "message": str(e)
            }
    
    # Overall success is true if all feature sets were processed successfully
    success = all(result.get("success", False) for result in results.values())
    
    return {
        "success": success,
        "feature_sets": results
    }


def run_feature_stage(config: dict[str, Any]) -> bool:
    """
    Run the feature engineering stage of the pipeline.
    
    Args:
        config: Pipeline configuration dictionary
        
    Returns:
        Boolean indicating success
    """
    try:
        results = run(config)
        return results.get("success", False)
    except Exception as e:
        logger.exception(f"Error in feature stage: {e}")
        return False 