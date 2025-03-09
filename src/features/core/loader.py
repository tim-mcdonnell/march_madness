"""Feature discovery and loading.

This module provides utilities for discovering and loading feature
implementations from the file system.
"""

import importlib
import importlib.util
import inspect
import logging
import os
import pkgutil
from pathlib import Path

from src.features.core.base import BaseFeature
from src.features.core.registry import registry

logger = logging.getLogger(__name__)


class FeatureLoader:
    """Discovers and loads feature implementations.
    
    This class scans the file system for feature implementations and
    registers them with the global feature registry.
    """
    
    def __init__(self, features_path: str | None = None) -> None:
        """Initialize the feature loader.
        
        Args:
            features_path: Path to the features directory.
                           If not provided, uses the parent directory of this file.
        """
        if features_path is None:
            # Default to the parent directory of the 'core' module
            features_path = str(Path(__file__).parent.parent)
        
        self.features_path = features_path
        logger.debug(f"Feature loader initialized with path: {features_path}")
    
    def discover_categories(self) -> list[str]:
        """Discover available feature categories.
        
        Scans the features directory for subdirectories that contain feature
        implementations.
        
        Returns:
            List of category names.
        """
        features_dir = Path(self.features_path)
        categories = []
        
        for item in features_dir.iterdir():
            # Skip non-directories, special directories, and the 'core' directory
            if not item.is_dir() or item.name.startswith('_') or item.name == 'core':
                continue
            
            # Check if the directory contains a python module
            if (item / "__init__.py").exists():
                categories.append(item.name)
        
        logger.info(f"Discovered {len(categories)} feature categories: {categories}")
        return categories
    
    def load_features_from_category(self, category: str) -> int:
        """Load features from a specific category.
        
        Args:
            category: The category to load features from.
            
        Returns:
            Number of features loaded.
        """
        category_path = os.path.join(self.features_path, category)
        if not os.path.isdir(category_path):
            logger.warning(f"Category directory not found: {category_path}")
            return 0
        
        # Import the category package
        try:
            category_package = f"src.features.{category}"
            importlib.import_module(category_package)
        except ImportError as e:
            logger.error(f"Failed to import category package {category_package}: {e}")
            return 0
        
        # Find feature modules in the category package
        package_path = os.path.join(self.features_path, category)
        feature_modules = []
        
        for _finder, name, is_pkg in pkgutil.iter_modules([package_path]):
            if is_pkg or name.startswith('_'):
                continue
            
            if "_" in name and any(c.isdigit() for c in name):
                feature_modules.append(name)
        
        # Import feature modules and register feature classes
        count = 0
        for module_name in feature_modules:
            try:
                full_module_name = f"src.features.{category}.{module_name}"
                module = importlib.import_module(full_module_name)
                
                # Find feature classes in the module
                found = False
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseFeature) and 
                            obj.__module__ == full_module_name and 
                            obj is not BaseFeature):
                        registry.register(obj)
                        count += 1
                        found = True
                
                if not found:
                    logger.warning(f"No feature class found in module: {full_module_name}")
            
            except Exception as e:
                logger.error(f"Error loading feature module {module_name}: {e}")
        
        logger.info(f"Loaded {count} features from category: {category}")
        return count
    
    def load_all_features(self) -> int:
        """Load all available features.
        
        Returns:
            Total number of features loaded.
        """
        categories = self.discover_categories()
        total_count = 0
        
        for category in categories:
            count = self.load_features_from_category(category)
            total_count += count
        
        logger.info(f"Loaded {total_count} features total")
        return total_count 