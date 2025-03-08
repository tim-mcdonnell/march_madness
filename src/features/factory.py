"""Factory module for creating feature builders."""

from src.features.base import BaseFeatureBuilder

# This dictionary will be populated as feature builders are imported
FEATURE_BUILDERS: dict[str, type[BaseFeatureBuilder]] = {}


def register_feature_builder(name: str, builder_class: type[BaseFeatureBuilder]) -> None:
    """Register a feature builder class.
    
    Args:
        name: Name of the feature builder
        builder_class: The feature builder class
    """
    global FEATURE_BUILDERS
    FEATURE_BUILDERS[name] = builder_class


def create_feature_builder(name: str, config: dict[str, object] | None = None) -> BaseFeatureBuilder:
    """Create a feature builder instance.
    
    Args:
        name: Name of the feature builder to create
        config: Configuration for the feature builder
        
    Returns:
        Feature builder instance
        
    Raises:
        ValueError: If the feature builder name is not registered
    """
    if name not in FEATURE_BUILDERS:
        raise ValueError(f"Unknown feature builder: {name}")
    
    return FEATURE_BUILDERS[name](config)


def get_available_feature_builders() -> list[str]:
    """Get a list of available feature builder names.
    
    Returns:
        List of feature builder names
    """
    return list(FEATURE_BUILDERS.keys()) 