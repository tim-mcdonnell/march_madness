# Extending the NCAA March Madness Predictor

This guide explains how to extend the NCAA March Madness Predictor with new features, models, and components.

## Project Architecture

Before extending the project, it's important to understand its architecture:

```
src/
├── data/                  # Data handling
│   ├── loader.py          # Data downloading
│   ├── cleaner.py         # Data cleaning
│   ├── transformer.py     # Data transformation
│   ├── validation.py      # Data validation
│   └── schema.py          # Data schemas
├── features/              # Feature engineering
│   ├── builders/          # Feature set builders
│   ├── base.py            # Base feature builder
│   └── factory.py         # Feature builder factory
├── models/                # Prediction models
│   ├── base.py            # Base model class
│   ├── ensemble.py        # Ensemble model
│   ├── lgbm.py            # LightGBM model
│   └── nn.py              # Neural network model
├── evaluation/            # Model evaluation
│   ├── metrics.py         # Evaluation metrics
│   └── visualizations.py  # Evaluation visualizations
├── pipeline/              # Pipeline components
│   ├── main.py            # Main pipeline script
│   ├── data.py            # Data pipeline stage
│   ├── features.py        # Feature pipeline stage
│   ├── model.py           # Model pipeline stage
│   └── predict.py         # Prediction pipeline stage
└── utils/                 # Utility functions
    ├── config.py          # Configuration handling
    ├── logger.py          # Logging utilities
    └── paths.py           # Path management
```

## Data Pipeline Architecture

The data pipeline consists of several modular components:

```
Download → Validation → Cleaning → Processing → Feature Engineering
```

Each component is designed to be extendable with clear interfaces:

- **Loaders**: Download and cache data (`src/data/loader.py`)
- **Validators**: Validate data quality and schemas (`src/data/validation.py`)
- **Cleaners**: Clean and standardize data (`src/data/cleaner.py`)
- **Transformers**: Process and transform data (`src/data/transformer.py`)
- **Feature Engineers**: Create derived features (`src/features/`)

## Extension Points

The project is designed with several extension points:

1. **Feature Sets**: Add new feature engineering approaches
2. **Models**: Implement new prediction models
3. **Data Sources**: Incorporate additional data sources
4. **Evaluation Metrics**: Add new evaluation metrics
5. **Visualization Components**: Create new visualizations

## Adding a New Data Source

To add a new data source to the pipeline:

1. **Update the Loader**

   Modify `src/data/loader.py` to include your new data source:

   ```python
   def download_new_data_source(season=None, force_download=False):
       """Download data from the new source.
       
       Args:
           season: Optional season to download (int or list of ints)
           force_download: Whether to force download even if files exist
           
       Returns:
           List of downloaded file paths
       """
       # Implementation for downloading from new source
       # ...
       
       return downloaded_files
   ```

2. **Create a Schema**

   Define a schema for the new data in `src/data/schema.py`:

   ```python
   NEW_DATA_SCHEMA = {
       "core_columns": {
           "id": pl.Int64,
           "date": pl.Date,
           # Other required columns
       },
       "optional_columns": {
           "additional_field": pl.Utf8,
           # Other optional columns
       }
   }
   ```

3. **Add Validation**

   Extend the validation in `src/data/validation.py`:

   ```python
   def validate_new_data_source(file_path):
       """Validate the new data source file.
       
       Args:
           file_path: Path to the file to validate
           
       Returns:
           ValidationResult with success flag and messages
       """
       return validate_file_against_schema(file_path, schema.NEW_DATA_SCHEMA)
   ```

4. **Implement Cleaning**

   Add cleaning functions in `src/data/cleaner.py`:

   ```python
   def clean_new_data_source(df):
       """Clean the new data source.
       
       Args:
           df: DataFrame to clean
           
       Returns:
           Cleaned DataFrame
       """
       # Apply standard cleaning procedures
       df = handle_missing_values(df)
       df = detect_and_handle_outliers(df)
       
       # Apply source-specific cleaning
       # ...
       
       return df
   ```

5. **Implement Processing**

   Add transformation logic in `src/data/transformer.py`:

   ```python
   def process_new_data_source(df):
       """Process the new data source.
       
       Args:
           df: DataFrame to process
           
       Returns:
           Processed DataFrame
       """
       # Standardize columns
       df = standardize_column_names(df)
       
       # Apply specific transformations
       # ...
       
       return df
   ```

6. **Update the Pipeline**

   Modify `src/pipeline/data.py` to include your new data source:

   ```python
   def run_data_pipeline(config):
       # Existing code...
       
       # Add new data source processing
       if config.get("process_new_source", True):
           logger.info("Processing new data source...")
           new_source_files = download_new_data_source(
               season=config.get("seasons"),
               force_download=config.get("force_download", False)
           )
           
           for file in new_source_files:
               validation_result = validate_new_data_source(file)
               if validation_result.success:
                   df = pl.read_parquet(file)
                   df = clean_new_data_source(df)
                   df = process_new_data_source(df)
                   # Save processed data
                   output_path = os.path.join(config["processed_dir"], "new_source.parquet")
                   df.write_parquet(output_path)
       
       # Existing code...
   ```

## Adding a New Cleaning Method

To add a new cleaning method:

1. **Implement the Cleaning Function**

   Add a new function to `src/data/cleaner.py`:

   ```python
   def new_cleaning_method(df, columns=None, params=None):
       """Apply new cleaning method to the data.
       
       Args:
           df: DataFrame to clean
           columns: List of columns to apply cleaning to (or None for all)
           params: Parameters for the cleaning method
           
       Returns:
           Cleaned DataFrame
       """
       # Implementation of the new cleaning method
       # ...
       
       return cleaned_df
   ```

2. **Integrate with Existing Cleaning Flows**

   Update the relevant cleaning functions to use your new method:

   ```python
   def clean_team_box_scores(df):
       # Existing cleaning steps...
       
       # Apply your new cleaning method
       df = new_cleaning_method(df, columns=["field1", "field2"], params={"threshold": 0.5})
       
       # Continue with existing cleaning...
       return df
   ```

## Adding a New Data Transformation

To add a new data transformation:

1. **Implement the Transformation Function**

   Add a new function to `src/data/transformer.py`:

   ```python
   def new_transformation(df, params=None):
       """Apply new transformation to the data.
       
       Args:
           df: DataFrame to transform
           params: Parameters for the transformation
           
       Returns:
           Transformed DataFrame
       """
       # Implementation of new transformation
       # ...
       
       return transformed_df
   ```

2. **Integrate with Existing Transformations**

   Update the relevant processing functions:

   ```python
   def process_team_box(df):
       # Existing processing...
       
       # Apply your new transformation
       df = new_transformation(df, params={"option1": True})
       
       # Continue with existing processing...
       return df
   ```

## Adding a New Feature Set

To add a new feature set:

1. Create a new file in `src/features/builders/`:

```python
# src/features/builders/my_feature_set.py
from src.features.base import BaseFeatureBuilder
import polars as pl

class MyFeatureBuilder(BaseFeatureBuilder):
    """Custom feature builder for my features."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "my_features"
        
    def build_features(self, team_data, schedules, team_box):
        """Build custom features.
        
        Args:
            team_data: Team season statistics
            schedules: Game schedules
            team_box: Team box scores
            
        Returns:
            DataFrame with new features
        """
        # Implement your feature engineering logic here
        features = team_data.clone()
        
        # Example: Add a custom feature
        features = features.with_columns(
            pl.col("points_per_game").divide(pl.col("points_allowed_per_game")).alias("scoring_ratio")
        )
        
        return features
```

2. Register your feature set in `src/features/factory.py`:

```python
# Add to the import section
from src.features.builders.my_feature_set import MyFeatureBuilder

# Add to the FEATURE_BUILDERS dictionary
FEATURE_BUILDERS = {
    "basic": BasicFeatureBuilder,
    "advanced": AdvancedFeatureBuilder,
    # ... existing feature builders
    "my_features": MyFeatureBuilder,  # Add your feature builder
}
```

3. Update the configuration to include your feature set:

```yaml
features:
  sets: ["basic", "advanced", "my_features"]  # Add your feature set
```

## Implementing a New Model

To add a new prediction model:

1. Create a new file in `src/models/`:

```python
# src/models/my_model.py
from src.models.base import BaseModel
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

class MyModel(BaseModel):
    """Custom prediction model."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "my_model"
        self.model = MyCustomClassifier()  # Your custom model implementation
        
    def train(self, X, y):
        """Train the model.
        
        Args:
            X: Feature matrix
            y: Target values
        """
        self.model.fit(X, y)
        
    def predict(self, X):
        """Make predictions.
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of predictions
        """
        return self.model.predict(X)
        
    def predict_proba(self, X):
        """Predict probabilities.
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of probability predictions
        """
        return self.model.predict_proba(X)


# Example custom classifier implementation
class MyCustomClassifier(BaseEstimator, ClassifierMixin):
    """Custom classifier implementation."""
    
    def __init__(self, param1=1.0, param2="value"):
        self.param1 = param1
        self.param2 = param2
        
    def fit(self, X, y):
        # Implement training logic
        return self
        
    def predict(self, X):
        # Implement prediction logic
        return np.array([0, 1, 0])  # Replace with actual implementation
        
    def predict_proba(self, X):
        # Implement probability prediction
        return np.array([[0.7, 0.3], [0.4, 0.6], [0.8, 0.2]])  # Replace with actual implementation
```

2. Register your model in `src/models/__init__.py`:

```python
from src.models.lgbm import LGBMModel
from src.models.nn import NeuralNetworkModel
from src.models.ensemble import EnsembleModel
from src.models.my_model import MyModel  # Import your model

MODEL_REGISTRY = {
    "lgbm": LGBMModel,
    "nn": NeuralNetworkModel,
    "ensemble": EnsembleModel,
    "my_model": MyModel,  # Register your model
}
```

3. Update the configuration to use your model:

```yaml
model:
  type: "my_model"
  # Add any model-specific parameters
  param1: 2.0
  param2: "custom_value"
```

## Best Practices

When extending the project, follow these best practices:

1. **Maintain Separation of Concerns**
   - Keep download, validation, cleaning, processing, and feature engineering as separate steps
   - Don't mix data processing with feature engineering

2. **Write Tests**
   - Add unit tests for your new components in `tests/`
   - Test with small samples before running on full datasets

3. **Document Changes**
   - Update relevant documentation in `docs/`
   - Add docstrings to all new functions
   - Document parameters, return values, and examples

4. **Handle Errors Gracefully**
   - Use proper exception handling
   - Log meaningful error messages
   - Provide fallback behavior where appropriate

5. **Maintain Backward Compatibility**
   - Ensure existing pipelines continue to work
   - Use optional parameters for new functionality

## Example: Adding Team Strength Metrics

Here's a complete example of adding team strength metrics to the pipeline:

```python
# In src/data/transformer.py

def calculate_team_strength_metrics(df):
    """Calculate additional team strength metrics.
    
    Args:
        df: Team box score DataFrame
        
    Returns:
        DataFrame with added strength metrics
    """
    # Calculate point differential
    df = df.with_columns([
        (pl.col("points") - pl.col("opponent_points")).alias("point_differential")
    ])
    
    # Calculate shooting efficiency
    df = df.with_columns([
        (pl.col("points") / pl.col("field_goals_attempted")).alias("points_per_shot")
    ])
    
    return df

# Update the existing processing function
def process_team_box(df):
    # Existing code...
    
    # Add strength metrics
    df = calculate_team_strength_metrics(df)
    
    return df
```

## Troubleshooting

Common issues when extending the project:

1. **Schema Validation Failures**
   - Ensure your new data source matches the defined schema
   - Check for data type mismatches
   - Verify required columns are present

2. **Memory Issues with Large Datasets**
   - Use Polars' lazy evaluation for large transformations
   - Process data in chunks when possible
   - Filter and select columns early in the pipeline

3. **Integration Problems**
   - Test each component individually before integration
   - Use small test datasets for initial validation
   - Ensure proper data flow between components

## Next Steps

After extending the project, remember to:

1. Update documentation to reflect your changes
2. Add tests for your new components
3. Consider contributing your extensions back to the main project

For more detailed examples, see the [Examples](../examples) directory. 