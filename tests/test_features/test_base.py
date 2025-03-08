"""Tests for the base feature builder."""

import pytest
import polars as pl
from pathlib import Path

from src.features.base import BaseFeatureBuilder


class SampleFeatureBuilder(BaseFeatureBuilder):
    """Sample implementation of BaseFeatureBuilder for testing."""
    
    def __init__(self, config=None):
        """Initialize the sample feature builder."""
        super().__init__(config)
        self.name = "test"
        
    def build_features(self, df):
        """Build test features."""
        return df.with_columns(pl.lit(1).alias("test_feature"))


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pl.DataFrame({
        "team_id": [1, 2, 3],
        "value": [10, 20, 30]
    })


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    return tmp_path / "features"


def test_base_feature_builder_init():
    """Test the initialization of BaseFeatureBuilder."""
    # Test with default config
    builder = BaseFeatureBuilder()
    assert builder.config == {}
    assert builder.name == "base"
    
    # Test with custom config
    config = {"param1": "value1", "param2": 42}
    builder = BaseFeatureBuilder(config)
    assert builder.config == config
    assert builder.name == "base"


def test_base_feature_builder_build_features():
    """Test that build_features raises NotImplementedError."""
    builder = BaseFeatureBuilder()
    with pytest.raises(NotImplementedError, match="Subclasses must implement build_features"):
        builder.build_features()


def test_save_features(sample_df, temp_output_dir):
    """Test saving features to a parquet file."""
    # Create the feature builder
    builder = SampleFeatureBuilder()
    
    # Generate features
    features = builder.build_features(sample_df)
    
    # Make sure the output directory exists
    temp_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test with default filename
    output_path = builder.save_features(features, temp_output_dir)
    expected_path = temp_output_dir / "test.parquet"
    assert output_path == expected_path
    assert output_path.exists()
    
    # Load the saved file and check contents
    loaded_df = pl.read_parquet(output_path)
    assert loaded_df.shape == features.shape
    assert set(loaded_df.columns) == set(features.columns)
    assert "test_feature" in loaded_df.columns
    
    # Test with custom filename without extension
    custom_filename = "custom_features"
    output_path = builder.save_features(features, temp_output_dir, custom_filename)
    expected_path = temp_output_dir / "custom_features.parquet"
    assert output_path == expected_path
    assert output_path.exists()
    
    # Test with custom filename with extension
    custom_filename = "another_features.parquet"
    output_path = builder.save_features(features, temp_output_dir, custom_filename)
    expected_path = temp_output_dir / "another_features.parquet"
    assert output_path == expected_path
    assert output_path.exists()
    
    # Verify file contents
    loaded_df = pl.read_parquet(output_path)
    # Compare the frames manually instead of using pl.testing.assert_frame_equal
    assert loaded_df.shape == features.shape
    assert set(loaded_df.columns) == set(features.columns)
    # Check that all values match
    for col in features.columns:
        assert loaded_df[col].to_list() == features[col].to_list() 