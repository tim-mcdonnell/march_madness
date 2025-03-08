"""Features package for March Madness predictor."""

import os

# Import feature builders and utilities
from src.features.base import BaseFeatureBuilder
from src.features.builders.foundation import FoundationFeatureBuilder
from src.features.factory import (
    FEATURE_BUILDERS,
    create_feature_builder,
    get_available_feature_builders,
    register_feature_builder,
)

# Register the foundation feature builder
register_feature_builder("foundation", FoundationFeatureBuilder)

# Only register the efficiency feature builder if environment allows it
# This prevents it from being imported during testing and slowing down tests
if os.environ.get("ENABLE_EFFICIENCY_FEATURES", "1") == "1":
    # Import conditionally to avoid unnecessary imports during testing
    from src.features.builders.efficiency import EfficiencyFeatureBuilder
    register_feature_builder("efficiency", EfficiencyFeatureBuilder)
    __all__ = [
        "BaseFeatureBuilder",
        "register_feature_builder",
        "create_feature_builder",
        "get_available_feature_builders",
        "FEATURE_BUILDERS",
        "FoundationFeatureBuilder",
        "EfficiencyFeatureBuilder",
    ]
else:
    __all__ = [
        "BaseFeatureBuilder",
        "register_feature_builder",
        "create_feature_builder",
        "get_available_feature_builders",
        "FEATURE_BUILDERS",
        "FoundationFeatureBuilder",
    ]
