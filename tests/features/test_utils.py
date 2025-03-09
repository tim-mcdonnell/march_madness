"""Utilities for testing features."""


import polars as pl


def assert_has_variance(series: pl.Series, min_std: float = 0.001) -> None:
    """
    Assert that a series has sufficient variance (not all identical values).
    
    Args:
        series: Polars series to check
        min_std: Minimum standard deviation required
    
    Raises:
        AssertionError: If the standard deviation is too low
    """
    std = series.std()
    assert std > min_std, f"Feature has insufficient variance: std={std}"


def assert_minimal_missing(series: pl.Series, max_missing_pct: float = 0.1) -> None:
    """
    Assert that a series has no more than max_missing_pct missing values.
    
    Args:
        series: Polars series to check
        max_missing_pct: Maximum allowed percentage of missing values (0.0-1.0)
    
    Raises:
        AssertionError: If too many values are missing
    """
    missing_pct = series.null_count() / len(series)
    assert missing_pct <= max_missing_pct, f"Too many missing values: {missing_pct:.2%}"


def assert_in_range(series: pl.Series, min_val: float, max_val: float) -> None:
    """
    Assert that all values in a series are within the specified range.
    
    Args:
        series: Polars series to check
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Raises:
        AssertionError: If any values are outside the specified range
    """
    # Check min
    min_actual = series.min()
    assert min_actual >= min_val, f"Minimum value {min_actual} is below allowed minimum {min_val}"
    
    # Check max
    max_actual = series.max()
    assert max_actual <= max_val, f"Maximum value {max_actual} is above allowed maximum {max_val}"


def validate_feature_output(
    df: pl.DataFrame, 
    feature_column: str,
    min_val: float = None,
    max_val: float = None,
    max_missing_pct: float = 0.1,
    min_std: float = 0.001
) -> None:
    """
    Validate the output of a feature calculation.
    
    Args:
        df: Feature result DataFrame
        feature_column: Name of the column containing the feature values
        min_val: Minimum allowed value (if None, no minimum check)
        max_val: Maximum allowed value (if None, no maximum check)
        max_missing_pct: Maximum allowed percentage of missing values
        min_std: Minimum required standard deviation
    
    Raises:
        AssertionError: If any validation fails
    """
    # Check DataFrame is not empty
    assert df.height > 0, "Feature result is empty"
    
    # Check column exists
    assert feature_column in df.columns, f"Feature column '{feature_column}' not found in result"
    
    # Get the feature column
    series = df[feature_column]
    
    # Check missing values
    assert_minimal_missing(series, max_missing_pct)
    
    # Check variance
    assert_has_variance(series, min_std)
    
    # Check range if specified
    if min_val is not None and max_val is not None:
        assert_in_range(series, min_val, max_val) 