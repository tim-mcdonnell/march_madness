"""Tests for the feature factory module."""

import pytest
from unittest.mock import MagicMock
import polars as pl

from src.features.base import BaseFeatureBuilder
from src.features.factory import (
    register_feature_builder,
    create_feature_builder,
    get_available_feature_builders,
    FEATURE_BUILDERS
)


class MockFeatureBuilder(BaseFeatureBuilder):
    """Mock feature builder for testing."""
    
    def __init__(self, config=None):
        """Initialize the mock feature builder."""
        super().__init__(config)
        self.name = "mock"
        
    def build_features(self, df1, df2):
        """Build mock features."""
        return pl.DataFrame({"mock_feature": [1, 2, 3]})


@pytest.fixture
def reset_feature_builders():
    """Reset the feature builders registry after each test."""
    original_builders = FEATURE_BUILDERS.copy()
    yield
    # Reset the global registry to its original state
    FEATURE_BUILDERS.clear()
    FEATURE_BUILDERS.update(original_builders)


def test_register_feature_builder(reset_feature_builders):
    """Test registering a feature builder."""
    # Mock builder class
    builder_class = MockFeatureBuilder
    
    # Register the builder
    register_feature_builder("test_builder", builder_class)
    
    # Verify it was registered
    assert "test_builder" in FEATURE_BUILDERS
    assert FEATURE_BUILDERS["test_builder"] == builder_class


def test_create_feature_builder(reset_feature_builders):
    """Test creating a feature builder."""
    # Register a mock builder
    register_feature_builder("test_builder", MockFeatureBuilder)
    
    # Create a builder instance
    config = {"test_param": True}
    builder = create_feature_builder("test_builder", config)
    
    # Verify the builder
    assert isinstance(builder, MockFeatureBuilder)
    assert builder.config == config
    assert builder.name == "mock"


def test_create_feature_builder_unknown(reset_feature_builders):
    """Test creating an unknown feature builder."""
    with pytest.raises(ValueError, match="Unknown feature builder: unknown_builder"):
        create_feature_builder("unknown_builder")


def test_get_available_feature_builders(reset_feature_builders):
    """Test getting available feature builders."""
    # Register some builders
    register_feature_builder("builder1", MockFeatureBuilder)
    register_feature_builder("builder2", MockFeatureBuilder)
    
    # Get available builders
    builders = get_available_feature_builders()
    
    # Verify the result includes our test builders
    assert "builder1" in builders
    assert "builder2" in builders
    
    # Should return all registered builders
    assert set(builders) == set(FEATURE_BUILDERS.keys()) 