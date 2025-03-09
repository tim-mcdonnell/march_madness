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
        """Clean feature files to remove duplicate columns with _right suffix."""
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
    
    def _derive_s01_from_team_box(self, missing_team_seasons: pl.DataFrame) -> pl.DataFrame:
        """
        Derive S01 (Effective Field Goal Percentage) directly from team_box data.
        
        This is a fallback method when teams exist in team_box but their S01 values
        weren't calculated properly in the feature stage.
        
        Args:
            missing_team_seasons: DataFrame with team_id and season for teams missing S01
            
        Returns:
            DataFrame with team_id, season, and derived S01 values
        """
        try:
            # Load team_box data
            team_box = pl.read_parquet(self.processed_dir / "team_box.parquet")
            
            # Filter to relevant team-seasons
            team_box_filtered = team_box.join(
                missing_team_seasons,
                on=["team_id", "season"],
                how="inner"
            )
            
            if len(team_box_filtered) == 0:
                logger.warning("No matching team_box data found for missing S01 values")
                return pl.DataFrame()
            
            # Verify required columns are present
            required_cols = [
                "team_id", "field_goals_made", "three_point_field_goals_made", 
                "field_goals_attempted", "season"
            ]
            
            missing_cols = [col for col in required_cols if col not in team_box_filtered.columns]
            if missing_cols:
                logger.warning(f"Missing required columns for S01 calculation: {missing_cols}")
                return pl.DataFrame()
            
            # Calculate eFG% by team and season using same formula as the feature
            result = (
                team_box_filtered
                .group_by(["team_id", "season"])
                .agg([
                    pl.col("field_goals_made").sum().alias("total_field_goals_made"),
                    pl.col("three_point_field_goals_made").sum().alias("total_three_point_field_goals_made"),
                    pl.col("field_goals_attempted").sum().alias("total_field_goals_attempted"),
                ])
            )
            
            # Add the eFG% column using the formula
            result = result.with_columns([
                (
                    (pl.col("total_field_goals_made") + 0.5 * pl.col("total_three_point_field_goals_made")) / 
                    pl.when(pl.col("total_field_goals_attempted") > 0)
                    .then(pl.col("total_field_goals_attempted"))
                    .otherwise(1.0)  # Avoid division by zero
                ).alias("derived_effective_field_goal_percentage")  # Use a different name to avoid conflicts
            ])
            
            # Drop the intermediate columns
            result = result.drop([
                "total_field_goals_made", 
                "total_three_point_field_goals_made", 
                "total_field_goals_attempted"
            ])
            
            logger.info(f"Derived S01 values for {len(result)} team-seasons directly from team_box")
            return result
            
        except Exception as e:
            logger.error(f"Error deriving S01 values from team_box: {e}")
            return pl.DataFrame()
            
    def apply_derived_s01_values(self, base_df: pl.DataFrame, derived_s01: pl.DataFrame) -> pl.DataFrame:
        """
        Apply derived S01 values to the base DataFrame, handling column name conflicts.
        
        Args:
            base_df: Base DataFrame to update
            derived_s01: DataFrame with derived S01 values
            
        Returns:
            Updated DataFrame with derived S01 values applied
        """
        s01_col = "shooting_S01_effective_field_goal_percentage"
        
        try:
            # Create a DataFrame with null S01 values replaced by derived values
            if derived_s01.height > 0:
                # First, extract the rows with null S01 values
                null_s01_rows = base_df.filter(pl.col(s01_col).is_null())
                
                # Join with derived values
                updated_rows = null_s01_rows.join(
                    derived_s01.select(
                        "team_id", 
                        "season", 
                        pl.col("derived_effective_field_goal_percentage")
                    ),
                    on=["team_id", "season"],
                    how="left"
                )
                
                # Create new column with values from derived values
                updated_rows = updated_rows.with_columns([
                    pl.col("derived_effective_field_goal_percentage").alias(s01_col)
                ]).drop("derived_effective_field_goal_percentage")
                
                # Find rows that have non-null values
                non_null_s01_rows = base_df.filter(pl.col(s01_col).is_not_null())
                
                # Combine original non-null rows with updated rows
                return pl.concat([non_null_s01_rows, updated_rows]).sort(["team_id", "season"])
                
            return base_df
            
        except Exception as e:
            logger.error(f"Error applying derived S01 values: {e}")
            return base_df

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
        
        # Dictionary to store each feature DataFrame by category
        feature_dfs = {}
        
        # First, collect all the feature DataFrames
        for path in feature_paths:
            category = path.stem.replace("_metrics", "")
            try:
                df = pl.read_parquet(path)
                logger.info(f"Loaded feature file: {path} with {len(df)} rows")
                feature_dfs[category] = df
            except Exception as e:
                logger.error(f"Error loading feature file {path}: {e}")
        
        if not feature_dfs:
            logger.warning("No feature files could be loaded.")
            return None
        
        # To solve the team-seasons discrepancy, we need to load the original data sources
        # to help with joining and filling in missing values
        
        # Load team_box and schedules data to help with team-season matching
        try:
            team_box = pl.read_parquet(self.processed_dir / "team_box.parquet")
            schedules = pl.read_parquet(self.processed_dir / "schedules.parquet")
            
            # Extract team_id and season combinations from both sources
            team_seasons_teambox = team_box.select(['team_id', 'season']).unique()
            
            # Create a comprehensive team mapping from schedules with both home and away teams
            team_mapping = pl.concat([
                # Home teams
                schedules.select([
                    pl.col('home_id').alias('team_id'), 
                    pl.col('home_location').alias('team_location'), 
                    pl.col('home_name').alias('team_name'),
                    pl.col('season')
                ]),
                # Away teams
                schedules.select([
                    pl.col('away_id').alias('team_id'), 
                    pl.col('away_location').alias('team_location'), 
                    pl.col('away_name').alias('team_name'),
                    pl.col('season')
                ])
            ]).unique()
            
            logger.info(f"Created comprehensive team mapping with {len(team_mapping)} team-seasons")
            
        except Exception as e:
            logger.warning(f"Could not load additional data for enhanced joins: {e}")
            team_mapping = None
            team_seasons_teambox = None
        
        # Create a base DataFrame with all unique combinations of join columns
        union_dfs = []
        
        # Start with the team mapping if available
        if team_mapping is not None:
            union_dfs.append(team_mapping)
        
        # Add team-seasons from each feature file
        for category, df in feature_dfs.items():
            # Get valid join columns that exist in this DataFrame
            valid_join_cols = [col for col in std_join_cols if col in df.columns]
            if len(valid_join_cols) >= 2 and "team_id" in valid_join_cols and "season" in valid_join_cols:
                union_dfs.append(df.select(valid_join_cols))
            else:
                logger.warning(f"Skipping {category}: missing required join columns")
        
        if not union_dfs:
            logger.error("No valid DataFrames with required join columns found")
            return None
        
        # Union all DataFrames to get all unique combinations of join columns
        base_df = union_dfs[0]
        for df in union_dfs[1:]:
            base_df = pl.concat([base_df, df]).unique()
        
        logger.info(f"Created base DataFrame with {len(base_df)} unique rows")
        
        # Now add features from each category with proper prefixing
        for category, df in feature_dfs.items():
            # Get valid join columns that exist in both DataFrames
            valid_join_cols = [col for col in std_join_cols if col in df.columns and col in base_df.columns]
            
            # Get feature columns (non-join columns)
            feature_cols = [col for col in df.columns if col not in std_join_cols]
            
            if not feature_cols:
                logger.warning(f"No feature columns found in {category} category.")
                continue
            
            if not valid_join_cols:
                logger.warning(f"No valid join columns for {category}, skipping.")
                continue
            
            # Prefix feature columns with category name if not already prefixed
            feature_df = df.select(
                valid_join_cols + 
                [
                    pl.col(col).alias(f"{category}_{col}" if not col.startswith(f"{category}_") else col)
                    for col in feature_cols
                ]
            )
            
            # Join with the base DataFrame
            try:
                # Use a left join to keep all rows in base_df
                base_df = base_df.join(
                    feature_df,
                    on=valid_join_cols,
                    how="left"
                )
                logger.info(f"Joined {len(feature_cols)} columns from {category}")
            except Exception as e:
                logger.error(f"Error joining {category} features: {e}")
        
        # For features that depend directly on team_box (like S01), add special handling
        # to check if we can derive values for missing data
        s01_col = "shooting_S01_effective_field_goal_percentage"
        if "shooting" in feature_dfs and team_seasons_teambox is not None:
            try:
                # Identify team-seasons missing S01 values but present in team_box
                if s01_col in base_df.columns:
                    missing_s01 = (
                        base_df
                        .filter(pl.col(s01_col).is_null())
                        .select(["team_id", "season"])
                    )
                    
                    # Find those that should have data from team_box
                    fixable_seasons = missing_s01.join(
                        team_seasons_teambox, 
                        on=["team_id", "season"],
                        how="inner"
                    )
                    
                    if len(fixable_seasons) > 0:
                        logger.info(f"Found {len(fixable_seasons)} team-seasons that should have S01 values")
                        
                        # First try to join with the shooting metrics data
                        shooting = feature_dfs["shooting"]
                        
                        # Join to get the missing values
                        enhanced_s01 = fixable_seasons.join(
                            shooting,
                            on=["team_id", "season"],
                            how="left"
                        )
                        
                        if len(enhanced_s01) > 0 and "S01_effective_field_goal_percentage" in enhanced_s01.columns:
                            # Update the base DataFrame with these values
                            for row in enhanced_s01.iter_rows(named=True):
                                if row["S01_effective_field_goal_percentage"] is not None:
                                    # Update the base DataFrame for this team-season
                                    base_df = base_df.with_columns([
                                        pl.when(
                                            (pl.col("team_id") == row["team_id"]) & 
                                            (pl.col("season") == row["season"]) &
                                            pl.col(s01_col).is_null()
                                        )
                                        .then(pl.lit(row["S01_effective_field_goal_percentage"]))
                                        .otherwise(pl.col(s01_col))
                                        .alias(s01_col)
                                    ])
                            logger.info("Enhanced S01 data from shooting metrics for team-seasons")
                
                        # For any remaining missing values, try to derive directly from team_box
                        still_missing_s01 = (
                            base_df
                            .filter(pl.col(s01_col).is_null())
                            .select(["team_id", "season"])
                            .join(team_seasons_teambox, on=["team_id", "season"], how="inner")
                        )
                        
                        if len(still_missing_s01) > 0:
                            logger.info(f"Still missing {len(still_missing_s01)} S01 values that should be calculable")
                            
                            # Derive S01 values directly from team_box
                            derived_s01 = self._derive_s01_from_team_box(still_missing_s01)
                            
                            if len(derived_s01) > 0:
                                # Apply the derived values to the base DataFrame
                                base_df = self.apply_derived_s01_values(base_df, derived_s01)
                                logger.info(f"Added {len(derived_s01)} derived S01 values")
                
                null_count = base_df[s01_col].null_count() if s01_col in base_df.columns else "unknown"
                logger.info(f"After enhancement: S01 null count: {null_count} out of {len(base_df)}")
                
            except Exception as e:
                logger.error(f"Error enhancing S01 values: {e}")
        
        # Save the combined results
        output_path = self.features_dir / "combined" / "full_feature_set.parquet"
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        if base_df is not None and base_df.height > 0:
            # Backup the existing file if it exists
            if output_path.exists():
                backup_path = output_path.with_name(f"{output_path.stem}_backup.parquet")
                try:
                    import shutil
                    shutil.copy2(output_path, backup_path)
                    logger.info(f"Backed up existing file to {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to backup existing file: {e}")
            
            base_df.write_parquet(output_path)
            logger.info(f"Combined {len(feature_paths)} feature files into: {output_path}")
            
            # Verify the combine worked correctly
            try:
                result_df = pl.read_parquet(output_path)
                for category in feature_dfs:
                    category_cols = [col for col in result_df.columns if col.startswith(f"{category}_")]
                    if category_cols:
                        # Calculate fill rates for the first 3 columns
                        filled_pct = {
                            col: (1 - result_df[col].null_count() / len(result_df)) * 100 
                            for col in category_cols[:3]
                        }
                        logger.info(
                            f"Verification - {category} columns: {len(category_cols)}, "
                            f"fill rates: {filled_pct}"
                        )
            except Exception as e:
                logger.error(f"Error verifying combined file: {e}")
            
            return str(output_path)
        
        logger.warning("Failed to create combined feature file - no data available.")
        return None 