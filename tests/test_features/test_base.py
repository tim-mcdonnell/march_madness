"""Tests for the base feature builder."""

from pathlib import Path

import polars as pl
import pytest

from src.features.base import BaseFeatureBuilder


class SampleFeatureBuilder(BaseFeatureBuilder):
    """Sample implementation of BaseFeatureBuilder for testing."""
    
    def __init__(self, config=None) -> None:
        """Initialize the sample feature builder."""
        super().__init__(config)
        self.name = "test"
        
    def build_features(self, df) -> pl.DataFrame:
        """Build test features."""
        return df.with_columns(pl.lit(1).alias("test_feature"))


@pytest.fixture
def sample_df() -> pl.DataFrame:
    """Create a sample DataFrame for testing."""
    return pl.DataFrame({
        "a": [1, 2, 3],
        "b": [4, 5, 6]
    })


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Create a temporary directory for test outputs."""
    return tmp_path / "features"


def test_base_feature_builder_init() -> None:
    """Test the initialization of BaseFeatureBuilder."""
    # Test with default config
    builder = BaseFeatureBuilder()
    assert builder.config == {}
    
    # Test with custom config
    config = {"key": "value"}
    builder = BaseFeatureBuilder(config)
    assert builder.config == config
    
    # Test that config is a copy
    config["new_key"] = "new_value"
    assert "new_key" not in builder.config


def test_base_feature_builder_build_features() -> None:
    """Test that build_features raises NotImplementedError."""
    builder = BaseFeatureBuilder()
    with pytest.raises(NotImplementedError):
        builder.build_features(None)


def test_save_features(sample_df, temp_output_dir) -> None:
    """Test saving features to a parquet file."""
    # Create the feature builder
    builder = SampleFeatureBuilder()
    
    # Create output directory
    temp_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save features
    output_path = builder.save_features(sample_df, str(temp_output_dir), "test_features.parquet")
    
    # Check that the file exists
    assert output_path.exists()
    
    # Check that we can read it back
    df_read = pl.read_parquet(output_path)
    assert df_read.shape == sample_df.shape
    assert set(df_read.columns) == set(sample_df.columns) 