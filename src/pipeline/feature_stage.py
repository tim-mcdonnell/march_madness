"""Feature calculation pipeline stage.

This module provides a pipeline stage for calculating features
and generating feature datasets.
"""

import logging
from pathlib import Path
from typing import Any

from src.features import calculate_features, initialize_features
from src.features.core.data_manager import FeatureDataManager
from src.pipeline.data_stage import BaseDataStage

logger = logging.getLogger(__name__)


class FeatureCalculationStage(BaseDataStage):
    """Pipeline stage for calculating features.
    
    This stage calculates features based on processed data and
    saves the results to the features directory.
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the feature calculation stage.
        
        Args:
            data_dir: Base data directory.
            config: Configuration for the stage.
        """
        super().__init__(data_dir, config)
        self.processed_dir = Path(data_dir) / "processed"
        self.features_dir = Path(data_dir) / "features"
        
        # Create the features directory if it doesn't exist
        self.features_dir.mkdir(parents=True, exist_ok=True)
        (self.features_dir / "combined").mkdir(exist_ok=True)
        
        # Initialize feature system
        self.features_loaded = False
    
    def run(
        self,
        categories: list[str] | None = None,
        feature_ids: list[str] | None = None,
        overwrite: bool = False,
    ) -> bool:
        """Run the feature calculation stage.
        
        Args:
            categories: List of feature categories to calculate.
                       If None, calculate features for all categories.
            feature_ids: List of specific feature IDs to calculate.
                        If None, calculate all features in the selected categories.
            overwrite: Whether to overwrite existing feature files.
            
        Returns:
            True if the stage ran successfully, False otherwise.
        """
        logger.info("Running feature calculation stage")
        
        # Make sure features are loaded
        if not self.features_loaded:
            count = initialize_features()
            logger.info(f"Loaded {count} features")
            self.features_loaded = True
        
        # Create data manager
        data_manager = FeatureDataManager(
            data_dir=str(self.data_dir),
            raw_dir=str(self.data_dir / "raw"),
            processed_dir=str(self.processed_dir),
            features_dir=str(self.features_dir),
        )
        
        # Calculate features
        if categories:
            # Calculate features for specific categories
            results = {}
            for category in categories:
                logger.info(f"Calculating features for category: {category}")
                category_results = calculate_features(
                    category=category,
                    feature_ids=feature_ids,
                    data_manager=data_manager,
                    save_results=True,
                    overwrite=overwrite,
                )
                results.update(category_results)
        
        elif feature_ids:
            # Calculate specific features
            logger.info(f"Calculating features by ID: {feature_ids}")
            results = calculate_features(
                feature_ids=feature_ids,
                data_manager=data_manager,
                save_results=True,
                overwrite=overwrite,
            )
        
        else:
            # Calculate all features
            logger.info("Calculating all features")
            results = calculate_features(
                data_manager=data_manager,
                save_results=True,
                overwrite=overwrite,
            )
        
        # Clean up feature files to remove duplicate columns
        logger.info("Cleaning feature files to remove duplicate columns")
        data_manager.clean_feature_files()
        
        # Combine all feature files
        combined_path = data_manager.combine_feature_files()
        
        if not combined_path:
            logger.warning("No features were calculated or combined")
            return False
        
        logger.info(f"Feature calculation complete. Combined results at: {combined_path}")
        return True 