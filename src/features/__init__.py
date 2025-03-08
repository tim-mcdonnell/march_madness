"""Features package for March Madness predictor."""

# Import feature builders and utilities
from src.features.base import BaseFeatureBuilder
from src.features.builders.foundation import FoundationFeatureBuilder
from src.features.factory import (
    FEATURE_BUILDERS,
    create_feature_builder,
    get_available_feature_builders,
    register_feature_builder,
)

# Register the feature builders
register_feature_builder("foundation", FoundationFeatureBuilder)

__all__ = [
    "BaseFeatureBuilder",
    "register_feature_builder",
    "create_feature_builder",
    "get_available_feature_builders",
    "FEATURE_BUILDERS",
    "FoundationFeatureBuilder",
]
