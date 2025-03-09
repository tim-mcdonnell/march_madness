"""Feature data management.

This module provides utilities for loading input data and storing
feature calculation results.
"""

import logging
from pathlib import Path

import polars as pl

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class FeatureDataManager:
    """Manages feature data loading and storage.
    
    This class handles loading input data required for feature calculations
    and storing the resulting feature values.
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        raw_dir: str = "data/raw",
        processed_dir: str = "data/processed",
        features_dir: str = "data/features",
    ) -> None:
        """Initialize the data manager.
        
        Args:
            data_dir: Base data directory.
            raw_dir: Directory containing raw data files.
            processed_dir: Directory containing processed data files.
            features_dir: Directory for storing feature data files.
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.features_dir = Path(features_dir)
        
        # Create the features directory structure if it doesn't exist
        self.features_dir.mkdir(parents=True, exist_ok=True)
        (self.features_dir / "combined").mkdir(exist_ok=True)
        
        # Standard column mapping to normalize column names across features
        self.column_mapping = {
            # Map processed data column names to feature-expected names
            "team_score": "points",
            "opponent_team_score": "opponent_points",
            "team_home_away": "venue_type",
        }
        
        logger.debug(f"Data manager initialized with features_dir: {self.features_dir}")
    
    def standardize_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """Standardize column names to match feature expectations.
        
        This method renames columns according to the column_mapping dictionary
        to ensure consistent column names across all features.
        
        Args:
            df: Input DataFrame with original column names
            
        Returns:
            DataFrame with standardized column names
        """
        # Create a mapping of columns that actually exist in the dataframe
        rename_dict = {
            old: new for old, new in self.column_mapping.items() 
            if old in df.columns and new not in df.columns
        }
        
        if rename_dict:
            logger.debug(f"Standardizing columns: {rename_dict}")
            return df.rename(rename_dict)
        
        return df
    
    def load_processed_data(self, data_type: str) -> pl.DataFrame | None:
        """Load processed data of a specific type.
        
        Args:
            data_type: Type of data to load (e.g., "team_box", "player_box").
            
        Returns:
            DataFrame containing the loaded data, or None if the file is not found.
        """
        file_path = self.processed_dir / f"{data_type}.parquet"
        if not file_path.exists():
            logger.warning(f"Processed data file not found: {file_path}")
            return None
        
        try:
            logger.info(f"Loading processed data: {file_path}")
            df = pl.read_parquet(file_path)
            
            # Standardize column names
            df = self.standardize_columns(df)
            
            # Standardize team_display_name to team_location for consistency
            if "team_display_name" in df.columns and "team_location" not in df.columns:
                df = df.rename({"team_display_name": "team_location"})
            
            return df
        
        except Exception as e:
            logger.error(f"Error loading processed data {data_type}: {e}")
            return None
    
    def load_data_for_feature(self, feature: BaseFeature) -> dict[str, pl.DataFrame]:
        """Load all data required by a feature.
        
        Args:
            feature: The feature for which to load data.
            
        Returns:
            Dictionary mapping data types to DataFrames.
        """
        required_data = feature.get_required_data()
        data = {}
        
        for data_type in required_data:
            df = self.load_processed_data(data_type)
            if df is None:
                logger.error(f"Could not load required data '{data_type}' for feature {feature.id}")
                continue
            
            data[data_type] = df
        
        return data
    
    def save_feature_results(
        self, category: str, results: pl.DataFrame, overwrite: bool = False
    ) -> str:
        """Save feature calculation results for a category.
        
        Args:
            category: Feature category.
            results: DataFrame containing feature values.
            overwrite: Whether to overwrite existing data.
            
        Returns:
            Path to the saved file.
        """
        file_name = f"{category}_metrics.parquet"
        file_path = self.features_dir / file_name
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if the file already exists
        if file_path.exists() and not overwrite:
            # Load existing data and merge with new results
            try:
                existing_df = pl.read_parquet(file_path)
                
                # Determine common columns to use as join keys
                common_cols = ["team_id", "team_location", "team_name", "season"]
                
                # Find valid join columns that exist in both DataFrames
                join_cols = [col for col in common_cols if col in existing_df.columns and col in results.columns]
                
                if not join_cols:
                    logger.warning("No common join columns found. Saving new results only.")
                    results.write_parquet(file_path)
                    return str(file_path)
                
                # Extract only feature columns from results, excluding join columns
                feature_cols = [col for col in results.columns if col not in join_cols]
                
                # Create a clean DataFrame with only the necessary columns
                result_df = results.select(join_cols + feature_cols)
                
                # Use join to combine the data without creating duplicate columns
                merged_df = existing_df.join(
                    result_df,
                    on=join_cols,
                    how="outer",
                    suffix="_right"  # Add suffix for duplicate columns
                )
                
                logger.info(f"Merged {len(feature_cols)} new columns with existing data")
                merged_df.write_parquet(file_path)
                
            except Exception as e:
                logger.error(f"Error merging with existing data: {e}")
                logger.info("Saving new results only")
                results.write_parquet(file_path)
        else:
            # Save new results
            results.write_parquet(file_path)
        
        logger.info(f"Saved feature results to: {file_path}")
        return str(file_path)
    
    def clean_feature_files(self) -> None:
        """Clean all feature files to remove duplicate column suffixes.
        
        This method removes duplicate '_right' suffixes from all category feature files.
        These can be created during joins when column names conflict.
        """
        # Find all category feature files
        feature_files = list(self.features_dir.glob("*_metrics.parquet"))
        if not feature_files:
            logger.warning("No feature files found to clean")
            return
        
        for file_path in feature_files:
            category_name = file_path.stem.replace("_metrics", "")
            logger.info(f"Cleaning feature file: {file_path}")
            
            try:
                # Read the current DataFrame
                df = pl.read_parquet(file_path)
                
                # Define the standard join columns we want to keep without _right suffix
                standard_cols = ["team_id", "team_location", "team_name", "season"]
                
                # Identify all columns that end with _right
                right_suffix_cols = [col for col in df.columns if col.endswith("_right")]
                
                if not right_suffix_cols:
                    logger.info(f"No columns with _right suffix found in {category_name}")
                    continue
                
                # Create a column mapping to rename _right columns
                rename_dict = {}
                drop_cols = []
                
                for col in right_suffix_cols:
                    base_col = col.replace("_right", "")
                    
                    # For standard join columns, always prefer the non-suffixed version
                    if base_col in standard_cols:
                        drop_cols.append(col)  # Drop the _right version 
                    else:
                        # For feature columns, if both exist, keep the _right version (newer)
                        # and drop the old one
                        if base_col in df.columns:
                            drop_cols.append(base_col)  # Drop the old version
                            rename_dict[col] = base_col  # Rename _right to replace it
                
                # First drop any columns we want to eliminate
                if drop_cols:
                    df = df.drop(drop_cols)
                    logger.info(f"Removed {len(drop_cols)} duplicate/outdated columns in {category_name}")
                
                # Then rename the _right columns to their base names
                if rename_dict:
                    df = df.rename(rename_dict)
                    logger.info(f"Renamed {len(rename_dict)} _right columns in {category_name}")
                
                # Save cleaned DataFrame
                df.write_parquet(file_path)
                logger.info(f"Saved cleaned {category_name} feature file")
            
            except Exception as e:
                logger.error(f"Error cleaning {category_name} feature file: {e}")
        
        logger.info(f"Finished cleaning {len(feature_files)} feature files")
    
    def combine_feature_files(self) -> str | None:
        """
        Combine all feature files into a single feature set.
        
        This method reads individual feature category files and combines them
        into a single comprehensive feature set. It handles join column deduplication
        and ensures proper prefixing of feature columns with their category names.
        
        Returns:
            Path to the combined feature file, or None if no files were combined.
        """
        logger.info("Combining feature files...")
        
        # Standard join columns that should be unique
        std_join_cols = ["team_id", "team_location", "team_name", "season"]
        
        # Find all feature files
        feature_paths = list(self.features_dir.glob("*.parquet"))
        if not feature_paths:
            logger.warning("No feature files found to combine.")
            return None
        
        # Load the first feature file as our base
        if not feature_paths:
            logger.warning("No feature files found to combine.")
            return None
        
        # Start with an empty DataFrame with just the join columns
        base_df = None
        feature_dfs = []

        # First, collect all the feature DataFrames
        for path in feature_paths:
            category = path.stem.replace("_metrics", "")
            try:
                df = pl.read_parquet(path)
                logger.info(f"Loaded feature file: {path}")
                
                # Store the category and dataframe
                feature_dfs.append((category, df))
            except Exception as e:
                logger.error(f"Error loading feature file {path}: {e}")
        
        if not feature_dfs:
            logger.warning("No feature files could be loaded.")
            return None

        # Initialize the base DataFrame with just the join columns from the first feature file
        base_df = feature_dfs[0][1].select(std_join_cols)
        
        # Now add features from each category with proper prefixing
        for category, df in feature_dfs:
            # Get feature columns (non-join columns)
            feature_cols = [col for col in df.columns if col not in std_join_cols]
            
            if not feature_cols:
                logger.warning(f"No feature columns found in {category} category.")
                continue
            
            # Prefix feature columns with category name if not already prefixed
            prefixed_features = {}
            for col in feature_cols:
                if not col.startswith(f"{category}_"):
                    prefixed_features[col] = f"{category}_{col}"
            
            # If there are columns to rename, create a new dataframe with renamed columns
            if prefixed_features:
                feature_df = df.select(
                    std_join_cols + [
                        pl.col(col).alias(prefixed_features.get(col, col)) 
                        for col in feature_cols
                    ]
                )
            else:
                feature_df = df.select(std_join_cols + feature_cols)
            
            # For the first category, we already have the join columns, so just add the features
            if base_df.width == len(std_join_cols):  # Only join columns
                # Add feature columns directly
                for col in feature_df.columns:
                    if col not in std_join_cols:  # Skip join columns
                        base_df = base_df.with_columns(feature_df.select(col))
            else:
                # For subsequent categories, join on std_join_cols
                try:
                    # Join only feature columns to avoid duplication
                    feature_only_df = feature_df.select([col for col in feature_df.columns if col not in std_join_cols])
                    join_df = feature_df.select(std_join_cols)
                    
                    # First join the join columns
                    base_df = base_df.join(join_df, on=std_join_cols, how="left", suffix="_right")
                    
                    # Then add each feature column separately
                    for col in feature_only_df.columns:
                        temp_df = join_df.with_columns(feature_only_df.select(col))
                        base_df = base_df.join(
                            temp_df.select(std_join_cols + [col]), 
                            on=std_join_cols, 
                            how="left",
                            suffix="_right"
                        )
                except Exception as e:
                    logger.error(f"Error joining {category} features: {e}")
                
        # Save the combined results
        output_path = self.features_dir / "combined" / "full_feature_set.parquet"
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        if base_df is not None and base_df.height > 0:
            base_df.write_parquet(output_path)
            logger.info(f"Combined {len(feature_paths)} feature files into: {output_path}")
            return output_path
        logger.warning("Failed to create combined feature file - no data available.")
        return None 