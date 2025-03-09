"""Feature registry system.

This module provides a registry for managing feature implementations.
The registry keeps track of all available features and provides methods
for retrieving features by ID, category, etc.
"""

import logging

from src.features.core.base import BaseFeature

logger = logging.getLogger(__name__)


class FeatureRegistry:
    """Registry for feature implementations.
    
    This class maintains a mapping of feature IDs to feature classes and
    provides methods for registering and retrieving features.
    """
    
    def __init__(self) -> None:
        """Initialize an empty feature registry."""
        self._features: dict[str, type[BaseFeature]] = {}
        self._categories: dict[str, list[str]] = {}
    
    def register(self, feature_class: type[BaseFeature]) -> None:
        """Register a feature class.
        
        Args:
            feature_class: The feature class to register.
            
        Raises:
            ValueError: If a feature with the same ID is already registered.
        """
        # Create a temporary instance to access attributes
        temp_instance = feature_class()
        feature_id = temp_instance.id
        category = temp_instance.category
        
        if feature_id in self._features:
            existing = self._features[feature_id]
            raise ValueError(
                f"Feature with ID '{feature_id}' already registered: {existing.__name__}"
            )
        
        # Register the feature
        self._features[feature_id] = feature_class
        
        # Update category mapping
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(feature_id)
        
        logger.info(f"Registered feature: {feature_id} - {temp_instance.name}")
    
    def get_feature(self, feature_id: str) -> type[BaseFeature]:
        """Get a feature class by ID.
        
        Args:
            feature_id: The ID of the feature to retrieve.
            
        Returns:
            The feature class.
            
        Raises:
            KeyError: If no feature with the given ID is registered.
        """
        if feature_id not in self._features:
            raise KeyError(f"No feature registered with ID: {feature_id}")
        
        return self._features[feature_id]
    
    def get_all_features(self) -> dict[str, type[BaseFeature]]:
        """Get all registered features.
        
        Returns:
            Dictionary mapping feature IDs to feature classes.
        """
        return self._features.copy()
    
    def get_features_by_category(self, category: str) -> dict[str, type[BaseFeature]]:
        """Get all features in a category.
        
        Args:
            category: The category to retrieve features for.
            
        Returns:
            Dictionary mapping feature IDs to feature classes.
        """
        if category not in self._categories:
            return {}
        
        return {
            feature_id: self._features[feature_id]
            for feature_id in self._categories[category]
        }
    
    def get_categories(self) -> set[str]:
        """Get all available categories.
        
        Returns:
            Set of category names.
        """
        return set(self._categories.keys())
    
    def clear(self) -> None:
        """Clear the registry."""
        self._features.clear()
        self._categories.clear()
    
    def __len__(self) -> int:
        """Get the number of registered features."""
        return len(self._features)
    
    def __contains__(self, feature_id: str) -> bool:
        """Check if a feature is registered."""
        return feature_id in self._features


# Global registry instance
registry = FeatureRegistry() 