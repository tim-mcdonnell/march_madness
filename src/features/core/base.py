"""Base class for all features.

This module defines the BaseFeature class that all feature implementations 
must inherit from to ensure consistent structure and behavior.
"""

import abc
import logging

import polars as pl

logger = logging.getLogger(__name__)


class BaseFeature(abc.ABC):
    """Base class for all feature implementations.
    
    All feature implementations must inherit from this class and provide
    the required attributes and methods.
    
    Attributes:
        id (str): Unique feature identifier (e.g., "S01").
        name (str): Human-readable feature name.
        category (str): Feature category (e.g., "shooting", "team_performance").
        description (str, optional): Detailed description of the feature.
    """
    
    # Required class attributes to be defined by subclasses
    id: str = None
    name: str = None
    category: str = None
    description: str = None
    
    def __init__(self) -> None:
        """Initialize the feature.
        
        Validates that required attributes are defined.
        """
        # Validate required attributes
        if not all([self.id, self.name, self.category]):
            cls_name = self.__class__.__name__
            raise ValueError(
                f"Feature {cls_name} must define 'id', 'name', and 'category' attributes"
            )
        
        self._validate_id()
        
        logger.debug(f"Initialized feature: {self.id} - {self.name}")
    
    def _validate_id(self) -> None:
        """Validate that the ID follows the required pattern."""
        if not self.id:
            raise ValueError("Feature ID must be defined")
        
        if not isinstance(self.id, str):
            raise TypeError(f"Feature ID must be a string, got {type(self.id)}")
        
        if len(self.id) < 2:
            raise ValueError(f"Feature ID must be at least 2 characters, got {self.id}")
        
        category_prefix = self.id[0].upper()
        if not self.category.startswith(category_prefix.lower()):
            logger.warning(
                f"Feature ID {self.id} does not match category prefix: expected {category_prefix}, "
                f"got {self.category[0].upper() if self.category else 'None'}"
            )
    
    @abc.abstractmethod
    def calculate(self, data: pl.DataFrame | dict[str, pl.DataFrame]) -> pl.DataFrame:
        """Calculate the feature from input data.
        
        This method must be implemented by all feature classes to perform the
        actual feature calculation.
        
        Args:
            data: Input data, either a single DataFrame or a dictionary of DataFrames
                 with keys representing data types (e.g., "team_box", "player_box").
        
        Returns:
            DataFrame with calculated feature values. Must include at minimum:
                - team_id: Team identifier
                - team_location: Team location (e.g., "Duke")
                - team_name: Team name (e.g., "Blue Devils")
                - season: Season year
                - [feature_name]: Calculated feature value
        """
        pass
    
    def get_required_data(self) -> list[str]:
        """Get the list of required data sources.
        
        Returns:
            List of data source names required by this feature.
            Default implementation returns ["team_box"].
        """
        return ["team_box"]
    
    def validate_result(self, result: pl.DataFrame) -> None:
        """Validate the calculated result.
        
        Ensures the result contains the required columns and meets any
        feature-specific validation requirements.
        
        Args:
            result: DataFrame with calculated feature values.
            
        Raises:
            ValueError: If the result is invalid.
        """
        required_columns = ["team_id", "team_location", "team_name", "season"]
        missing_columns = [col for col in required_columns if col not in result.columns]
        
        if missing_columns:
            raise ValueError(f"Result missing required columns: {missing_columns}")
    
    def transform_result(self, result: pl.DataFrame) -> pl.DataFrame:
        """Transform the calculated result before storage.
        
        This method can be overridden to perform any final transformations
        on the result before it is stored.
        
        Args:
            result: DataFrame with calculated feature values.
            
        Returns:
            Transformed DataFrame.
        """
        return result
    
    def __str__(self) -> str:
        """Get a string representation of the feature."""
        return f"{self.id} - {self.name} ({self.category})"
    
    def __repr__(self) -> str:
        """Get a detailed string representation of the feature."""
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, category={self.category})" 