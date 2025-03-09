"""Feature engineering package.

This package contains feature engineering modules for extracting and
calculating basketball statistics and metrics from raw data.
"""

import logging

import polars as pl

from src.features.core.base import BaseFeature
from src.features.core.data_manager import FeatureDataManager
from src.features.core.loader import FeatureLoader
from src.features.core.registry import registry

logger = logging.getLogger(__name__)


def initialize_features() -> int:
    """Initialize the feature system.
    
    Discovers and loads all available features.
    
    Returns:
        Number of features loaded.
    """
    loader = FeatureLoader()
    return loader.load_all_features()


def get_all_features() -> dict[str, type[BaseFeature]]:
    """Get all registered features.
    
    Returns:
        Dictionary mapping feature IDs to feature classes.
    """
    return registry.get_all_features()


def get_features_by_category(category: str) -> dict[str, type[BaseFeature]]:
    """Get all features in a category.
    
    Args:
        category: The category to retrieve features for.
        
    Returns:
        Dictionary mapping feature IDs to feature classes.
    """
    return registry.get_features_by_category(category)


def calculate_features(
    category: str | None = None,
    feature_ids: list[str] | None = None,
    data_manager: FeatureDataManager | None = None,
    save_results: bool = True,
    overwrite: bool = False,
) -> dict[str, pl.DataFrame]:
    """Calculate features and optionally save results.
    
    Args:
        category: Calculate features for this category only.
                 If None, calculate all features.
        feature_ids: Calculate these specific features only.
                    If None, calculate all features in the category.
        data_manager: Data manager to use. If None, create a new one.
        save_results: Whether to save results to files.
        overwrite: Whether to overwrite existing feature files.
        
    Returns:
        Dictionary mapping categories to DataFrames with calculated features.
    """
    # Ensure features are loaded
    if not registry.get_all_features():
        initialize_features()
    
    # Create a data manager if none was provided
    if data_manager is None:
        data_manager = FeatureDataManager()
    
    results = {}
    
    # Determine which features to calculate
    if feature_ids:
        # Calculate specific features
        features_to_calc = {}
        for feature_id in feature_ids:
            try:
                feature_class = registry.get_feature(feature_id)
                feature = feature_class()
                if feature.category not in features_to_calc:
                    features_to_calc[feature.category] = []
                features_to_calc[feature.category].append(feature)
            except KeyError:
                logger.warning(f"Feature not found: {feature_id}")
        
        # Calculate features for each category
        for category, features in features_to_calc.items():
            category_results = calculate_category_features(
                category, features, data_manager
            )
            if category_results is not None:
                results[category] = category_results
                
                if save_results:
                    data_manager.save_feature_results(
                        category, category_results, overwrite=overwrite
                    )
    
    elif category:
        # Calculate all features in a specific category
        feature_classes = registry.get_features_by_category(category)
        if not feature_classes:
            logger.warning(f"No features found for category: {category}")
            return results
        
        features = [cls() for cls in feature_classes.values()]
        category_results = calculate_category_features(
            category, features, data_manager
        )
        
        if category_results is not None:
            results[category] = category_results
            
            if save_results:
                data_manager.save_feature_results(
                    category, category_results, overwrite=overwrite
                )
    
    else:
        # Calculate all features in all categories
        for category in registry.get_categories():
            feature_classes = registry.get_features_by_category(category)
            features = [cls() for cls in feature_classes.values()]
            
            category_results = calculate_category_features(
                category, features, data_manager
            )
            
            if category_results is not None:
                results[category] = category_results
                
                if save_results:
                    data_manager.save_feature_results(
                        category, category_results, overwrite=overwrite
                    )
    
    # Combine all feature files if results were saved
    if save_results and results:
        data_manager.combine_feature_files()
    
    return results


def calculate_category_features(
    category: str,
    features: list[BaseFeature],
    data_manager: FeatureDataManager,
) -> pl.DataFrame | None:
    """Calculate features for a specific category.
    
    Args:
        category: Feature category.
        features: List of features to calculate.
        data_manager: Data manager to use.
        
    Returns:
        DataFrame with calculated features or None if no features were calculated.
    """
    logger.info(f"Calculating {len(features)} features for category: {category}")
    
    # Calculate each feature
    all_results = []
    for feature in features:
        try:
            # Load data required by the feature
            data = data_manager.load_data_for_feature(feature)
            
            # Skip if any required data is missing
            if len(data) < len(feature.get_required_data()):
                missing = set(feature.get_required_data()) - set(data.keys())
                logger.warning(f"Skipping feature {feature.id}: Missing required data {missing}")
                continue
            
            # Calculate the feature
            logger.info(f"Calculating feature: {feature.id} - {feature.name}")
            result = feature.calculate(data)
            
            if result is not None:
                logger.info(f"Successfully calculated feature: {feature.id}")
                # Store the feature ID and result
                all_results.append((feature, result))
            else:
                logger.warning(f"Feature {feature.id} returned no results")
                
        except Exception as e:
            logger.error(f"Error calculating feature {feature.id}: {e}")
    
    if not all_results:
        logger.warning(f"No features were successfully calculated for category: {category}")
        return None
    
    # Completely revised approach to combine results
    # Instead of joining incrementally, we'll combine all at once in a cleaner way
    
    # First, extract the join keys from the first result
    join_cols = ["team_id", "team_location", "team_name", "season"]
    first_feature, first_df = all_results[0]
    
    # Identify valid join columns that exist in the first result
    valid_join_cols = [col for col in join_cols if col in first_df.columns]
    if not valid_join_cols:
        logger.error(f"No valid join columns found in results for {category}")
        return None
    
    # Create a base DataFrame with just the join columns to start with
    base_df = first_df.select(valid_join_cols).clone()
    logger.debug(f"Base DataFrame has {base_df.shape[0]} rows and columns: {base_df.columns}")
    
    # For each feature result, join only its unique feature columns
    for feature, df in all_results:
        feature_id = feature.id
        
        # Verify these join columns exist in current feature's DataFrame
        df_join_cols = [col for col in valid_join_cols if col in df.columns]
        if not df_join_cols:
            logger.warning(f"Skipping feature {feature_id} - no matching join columns")
            continue
        
        # Extract feature-specific columns, excluding join columns
        feature_cols = [col for col in df.columns if col not in df_join_cols]
        if not feature_cols:
            logger.warning(f"Skipping feature {feature_id} - no feature-specific columns")
            continue
        
        # Prefix feature columns with feature ID to ensure uniqueness
        renamed_cols = {}
        for col in feature_cols:
            # If the column is already feature-specific, keep it as is
            if col.startswith(f"{feature_id}_"):
                continue
            # Otherwise, prefix it with the feature ID
            renamed_cols[col] = f"{feature_id}_{col}"
        
        if renamed_cols:
            feature_df = df.select(df_join_cols + feature_cols).rename(renamed_cols)
        else:
            feature_df = df.select(df_join_cols + feature_cols)
        
        logger.debug(f"Feature {feature_id} DataFrame has columns: {feature_df.columns}")
        
        try:
            # Join the feature DataFrame with the base DataFrame
            join_cols = [col for col in df_join_cols if col in base_df.columns]
            if not join_cols:
                logger.warning(f"Cannot join feature {feature_id} - no common join columns")
                continue
            
            # Use safe join to avoid column name conflicts
            new_cols = [col for col in feature_df.columns if col not in base_df.columns]
            if not new_cols:
                logger.warning(f"Feature {feature_id} has no new columns to add")
                continue
            
            # Only select new columns from feature_df to avoid duplicates
            feature_df_new = feature_df.select(join_cols + new_cols)
            base_df = base_df.join(
                feature_df_new,
                on=join_cols,
                how="left",
                suffix="_right"  # Add suffix for duplicate columns
            )
        except Exception as e:
            logger.error(f"Error joining feature {feature_id}: {e}")
    
    logger.info(f"Successfully calculated {len(all_results)} features for category: {category}")
    return base_df
