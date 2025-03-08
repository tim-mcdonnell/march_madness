"""Base feature builder classes for March Madness predictor."""

from pathlib import Path

import polars as pl


class BaseFeatureBuilder:
    """Base class for all feature builders.
    
    This class defines the interface that all feature builders must implement.
    Feature builders are responsible for creating features from processed data.
    """
    
    def __init__(self, config: dict[str, object] | None = None) -> None:
        """Initialize the feature builder.
        
        Args:
            config: Configuration parameters for the feature builder
        """
        self.config = config or {}
        self.name = "base"
        
    def build_features(self, *args: pl.DataFrame) -> pl.DataFrame:
        """Build features from input data.
        
        This method must be implemented by subclasses.
        
        Returns:
            DataFrame with calculated features
        """
        raise NotImplementedError("Subclasses must implement build_features")
    
    def save_features(self, df: pl.DataFrame, output_dir: str, 
                     filename: str | None = None) -> Path:
        """Save features to a parquet file.
        
        Args:
            df: DataFrame with features to save
            output_dir: Directory to save the features to
            filename: Filename to use (without extension)
            
        Returns:
            Path to the saved file
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            filename = f"{self.name}.parquet"
        elif not filename.endswith(".parquet"):
            filename = f"{filename}.parquet"
            
        output_path = output_dir / filename
        df.write_parquet(output_path)
        
        return output_path 