"""Data quality validation for feature generation.

This module provides data quality checking functions that can be used
during feature generation to ensure the generated features meet
quality standards.
"""

import logging
from typing import Any

import polars as pl

# Configure logging
logger = logging.getLogger(__name__)


class FeatureQualityChecker:
    """Quality checker for feature data.
    
    This class provides methods to check the quality of generated features,
    including null value percentage, variability, and range validation.
    """
    
    def __init__(self, 
                feature_metadata: dict[str, dict[str, Any]],
                raise_errors: bool = False) -> None:
        """Initialize the feature quality checker.
        
        Args:
            feature_metadata: Dictionary mapping feature names to their metadata,
                including expected ranges, types, and maximum null percentages.
            raise_errors: If True, raise exceptions for quality issues. If False,
                log warnings instead.
        """
        self.feature_metadata = feature_metadata
        self.raise_errors = raise_errors
        
    def check_all(self, df: pl.DataFrame) -> tuple[bool, list[str]]:
        """Run all quality checks on the feature DataFrame.
        
        Args:
            df: DataFrame containing the features to check
            
        Returns:
            Tuple of (passed_all, error_messages)
        """
        all_passed = True
        error_messages = []
        
        # Check for missing columns
        missing_columns = self._check_columns_exist(df)
        if missing_columns:
            msg = f"Missing expected feature columns: {missing_columns}"
            error_messages.append(msg)
            all_passed = False
            
        # Check null percentages
        null_issues = self._check_null_percentages(df)
        if null_issues:
            error_messages.extend(null_issues)
            all_passed = False
            
        # Check variability
        variability_issues = self._check_variability(df)
        if variability_issues:
            error_messages.extend(variability_issues)
            all_passed = False
            
        # Check value ranges
        range_issues = self._check_value_ranges(df)
        if range_issues:
            error_messages.extend(range_issues)
            all_passed = False
            
        # Log or raise issues
        if not all_passed:
            if self.raise_errors:
                raise ValueError("\n".join(error_messages))
            for msg in error_messages:
                logger.warning(msg)
        
        return all_passed, error_messages
    
    def _check_columns_exist(self, df: pl.DataFrame) -> list[str]:
        """Check that all expected feature columns exist.
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of missing column names
        """
        return [f for f in self.feature_metadata if f not in df.columns]
    
    def _check_null_percentages(self, df: pl.DataFrame) -> list[str]:
        """Check that null percentages are below thresholds.
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of error messages for features with too many nulls
        """
        total_rows = df.height
        errors = []
        
        for feature, metadata in self.feature_metadata.items():
            if feature not in df.columns:
                continue
                
            max_null_pct = metadata.get('max_null_pct', 0.1)  # Default to 10% if not specified
            null_count = df.select(pl.col(feature).is_null().sum()).item()
            null_pct = null_count / total_rows
            
            if null_pct > max_null_pct:
                errors.append(
                    f"Feature '{feature}' has {null_pct:.2%} null values, "
                    f"which exceeds the threshold of {max_null_pct:.2%}"
                )
                
        return errors
    
    def _check_variability(self, df: pl.DataFrame) -> list[str]:
        """Check that features have variability (not all the same value).
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of error messages for features with no variability
        """
        errors = []
        
        for feature, _metadata in self.feature_metadata.items():
            if feature not in df.columns:
                continue
                
            # Skip if there are no non-null values
            non_null_values = df.filter(~pl.col(feature).is_null())
            if non_null_values.height == 0:
                continue
                
            # Check uniqueness
            unique_values = non_null_values.select(pl.col(feature).n_unique()).item()
            if unique_values <= 1:
                errors.append(
                    f"Feature '{feature}' has no variability (all values are the same)"
                )
                
        return errors
    
    def _check_value_ranges(self, df: pl.DataFrame) -> list[str]:
        """Check that feature values are within expected ranges.
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of error messages for features with out-of-range values
        """
        errors = []
        
        for feature, metadata in self.feature_metadata.items():
            if feature not in df.columns:
                continue
                
            # Skip if no range specified
            if 'range' not in metadata or (metadata['range'][0] is None and metadata['range'][1] is None):
                continue
                
            # Filter out nulls and infinities for valid checking
            valid_values = df.filter(
                ~pl.col(feature).is_null() & 
                ~pl.col(feature).is_infinite()
            )
            
            # Skip if no valid values
            if valid_values.height == 0:
                continue
                
            # Get actual min and max from valid values
            min_val, max_val = metadata['range']
            actual_min = valid_values.select(pl.col(feature).min()).item()
            actual_max = valid_values.select(pl.col(feature).max()).item()
            
            # Check minimum value if specified
            if min_val is not None and actual_min < min_val - 1e-6:
                errors.append(
                    f"Feature '{feature}' has minimum value {actual_min}, "
                    f"which is below the expected minimum {min_val}"
                )
            
            # Check maximum value if specified
            if max_val is not None and actual_max > max_val + 1e-6:
                errors.append(
                    f"Feature '{feature}' has maximum value {actual_max}, "
                    f"which is above the expected maximum {max_val}"
                )
            
            # Check for infinities if ranges are specified
            if min_val is not None or max_val is not None:
                # Count infinities
                inf_count = df.select(pl.col(feature).is_infinite().sum()).item()
                
                if inf_count > 0:
                    # Only add a warning, don't fail validation
                    infinity_pct = inf_count / df.height
                    logger.warning(
                        f"Feature '{feature}' has {inf_count} infinity values ({infinity_pct:.2%})"
                    )
                
        return errors


# Base feature metadata - default settings that can be overridden by configuration
BASE_FEATURE_METADATA = {
    # Shooting metrics
    'efg_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'ts_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'three_point_rate': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'ft_rate': {'type': 'ratio', 'range': (0.0, 2.0), 'max_null_pct': 0.1},
    
    # Possession metrics
    'orb_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'drb_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'trb_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'ast_rate': {'type': 'ratio', 'range': (0.0, None), 'max_null_pct': 0.1},
    'tov_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'ast_to_tov_ratio': {'type': 'ratio', 'range': (0.0, None), 'max_null_pct': 0.1},
    
    # Win percentage breakdowns - updated thresholds based on actual data
    'home_win_pct_detailed': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.5},
    'away_win_pct_detailed': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    'neutral_win_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.6},
    'home_games_played': {'type': 'count', 'range': (0, None), 'max_null_pct': 0.1},
    'away_games_played': {'type': 'count', 'range': (0, None), 'max_null_pct': 0.1},
    'neutral_games_played': {'type': 'count', 'range': (0, None), 'max_null_pct': 0.1},
    
    # Form metrics
    'point_diff_stddev': {'type': 'stddev', 'range': (0.0, None), 'max_null_pct': 0.4},
    'scoring_stddev': {'type': 'stddev', 'range': (0.0, None), 'max_null_pct': 0.4},
    'recent_point_diff': {'type': 'score', 'range': (None, None), 'max_null_pct': 0.1},
    'recent_win_pct': {'type': 'percentage', 'range': (0.0, 1.0), 'max_null_pct': 0.1},
    
    # Home court advantage
    'home_court_advantage': {'type': 'score', 'range': (None, None), 'max_null_pct': 0.5},
    'home_win_boost': {'type': 'offset_percentage', 'range': (-1.0, 1.0), 'max_null_pct': 0.5},
}


def get_feature_metadata(config: dict[str, Any] | None = None,
                     columns: list[str] | None = None) -> dict[str, dict[str, Any]]:
    """Get feature metadata with thresholds from configuration.
    
    Args:
        config: Configuration dictionary with possible thresholds
        columns: Optional list of column names to include (if None, includes all)
        
    Returns:
        Feature metadata dictionary with appropriate thresholds
    """
    # Start with base metadata
    metadata = dict(BASE_FEATURE_METADATA)
    
    # Filter to only include specified columns if provided
    if columns is not None:
        metadata = {k: v for k, v in metadata.items() if k in columns}
    
    # Apply configuration thresholds if provided
    if config:
        # Look for thresholds in config
        validation_config = config.get('validation', {})
        thresholds = validation_config.get('thresholds', {})
        
        # Apply thresholds to metadata
        for feature, threshold in thresholds.items():
            if feature in metadata:
                metadata[feature]['max_null_pct'] = threshold
                logger.info(f"Using custom threshold for {feature}: {threshold}")
    
    return metadata


def validate_features(df: pl.DataFrame, 
                     feature_metadata: dict[str, dict[str, Any]] | None = None,
                     config: dict[str, Any] | None = None,
                     raise_errors: bool = False) -> bool:
    """Validate features against quality standards.
    
    Args:
        df: DataFrame containing features to validate
        feature_metadata: Optional metadata for features (if None, uses metadata from config or defaults)
        config: Configuration from which to extract thresholds
        raise_errors: If True, raise exceptions for quality issues
        
    Returns:
        True if all checks pass, False otherwise
    """
    # Get feature metadata from config if not provided directly
    if feature_metadata is None:
        # Only include columns that exist in the DataFrame
        feature_metadata = get_feature_metadata(config, columns=df.columns)
        
    checker = FeatureQualityChecker(feature_metadata, raise_errors)
    passed, _ = checker.check_all(df)
    
    return passed 