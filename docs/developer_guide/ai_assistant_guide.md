# AI Assistant Guide - NCAA March Madness Predictor

This guide is designed to help AI coding assistants understand the structure, patterns, and workflows of the NCAA March Madness Predictor project. It provides essential context about the codebase organization to help you generate correct, compatible code without requiring the entire codebase as context.

## 1. Project Overview

The NCAA March Madness Predictor is a data science project that builds optimal March Madness brackets using historical NCAA men's basketball data. It uses a pipeline-based architecture to:

1. Collect and process 22+ years of NCAA basketball data from the sportsdataverse repository
2. Engineer features that predict tournament success
3. Train neural network models for game outcome prediction
4. Generate optimized brackets with visualizations

### Key Technology Stack

- **Python 3.11+**: Core programming language
- **uv**: Package manager and environment tool
- **Polars**: High-performance DataFrame library (primary data manipulation tool)
- **PyTorch**: Deep learning framework
- **Plotly Dash**: Interactive visualization
- **Parquet/PyArrow**: Data storage format
- **YAML**: Configuration files

## 2. Directory Structure & Purpose

```
march_madness/
├── config/                 # YAML configuration files
│   └── pipeline_config.yaml # Main pipeline configuration
├── data/                   # Data storage (gitignored)
│   ├── raw/                # Original unmodified data
│   ├── processed/          # Cleaned and transformed data
│   └── features/           # Engineered features
├── docs/                   # Documentation files
├── models/                 # Saved model files
├── notebooks/              # Jupyter notebooks (exploratory)
├── src/                    # Source code
│   ├── data/               # Data processing modules
│   ├── features/           # Feature engineering
│   ├── models/             # Model code
│   ├── pipeline/           # Pipeline framework
│   └── visualization/      # Visualization code
├── tests/                  # Test code
├── visualizations/         # Output visualization files
├── .github/                # GitHub configurations
├── run_pipeline.py         # Main pipeline execution script
└── pyproject.toml          # Project configuration and dependencies
```

## 3. Core Modules & Relationships

### 3.1 Pipeline Framework (`src/pipeline/`)

The backbone of the project is the pipeline framework that orchestrates data processing, feature engineering, model training, and prediction:

- **`cli.py`**: Command-line interface for the pipeline
- **`config.py`**: Configuration management (loading, validation)
- **`data_stage.py`**: Implementation of the data collection stage
- **`data_management.py`**: Utilities for data organization and cleaning

The pipeline is designed to be modular, with separate stages that can run independently:
1. **Data Collection**: Fetches and stores raw data
2. **Data Processing**: Cleans and transforms raw data
3. **Feature Engineering**: Creates model features
4. **Model Training**: Trains prediction models
5. **Bracket Generation**: Creates optimized brackets

### 3.2 Data Processing (`src/data/`)

This module handles the loading, cleaning, and transformation of NCAA basketball data:

- **Data Sources**: Data is sourced exclusively from sportsdataverse's hoopR-mbb-data repository
- **Data Categories**: play_by_play, player_box, schedules, team_box
- **Data Format**: Parquet files, loaded using Polars (not Pandas)
- **Data Years**: 2003-2025 (22+ years of historical data)

### 3.3 Feature Engineering (`src/features/`)

Transforms processed data into features for model training:

- Team statistics (offensive/defensive efficiency, etc.)
- Historical tournament performance
- Match-up specific features
- Temporal features (trends, momentum)

### 3.4 Models (`src/models/`)

Implements neural network models for game outcome prediction:

- PyTorch-based neural network architecture
- Training utilities
- Evaluation metrics
- Prediction generation

### 3.5 Visualization (`src/visualization/`)

Creates visualizations for insights and bracket presentation:

- Plotly/Dash-based interactive visualizations
- Bracket visualization utilities
- Performance metric plotting

## 4. Code Conventions & Patterns

### 4.1 Naming Conventions

- **Files**: Snake case (`feature_engineering.py`)
- **Classes**: Pascal case (`DataProcessor`)
- **Functions/Methods**: Snake case (`process_data()`)
- **Variables**: Snake case (`team_stats`)
- **Constants**: Uppercase with underscores (`BASE_URL`)

### 4.2 Type Hints & Documentation

- All functions should include type hints
- Documentation follows Google-style docstrings
- Complex logic includes inline comments

```python
def calculate_team_efficiency(
    team_data: pl.DataFrame,
    season: int
) -> pl.DataFrame:
    """
    Calculate offensive and defensive efficiency ratings for teams.
    
    Args:
        team_data: DataFrame containing team statistics
        season: Basketball season year (e.g., 2023)
        
    Returns:
        DataFrame with added efficiency columns
    """
    # Implementation...
```

### 4.3 Data Processing Standards

- **Primary DataFrame Library**: Use Polars, not Pandas
- **Schema Enforcement**: All DataFrames use explicit schemas
- **Error Handling**: Use explicit try/except blocks with informative error messages
- **File Paths**: Generated using pathlib.Path, not string concatenation

```python
# CORRECT: Using Polars with schema
import polars as pl
from pathlib import Path

# Define schema
team_schema = {
    "team_id": pl.Int64,
    "team_name": pl.Utf8,
    "points": pl.Float64,
    # Other fields...
}

# Load data with proper path handling
file_path = Path("data/processed") / f"team_stats_{season}.parquet"
team_stats = pl.read_parquet(file_path, schema=team_schema)

# INCORRECT: Avoid these patterns
# import pandas as pd
# team_stats = pd.read_csv("data/processed/team_stats_" + str(season) + ".csv")
```

### 4.4 Configuration Management

- Configuration is loaded from YAML files in the `config/` directory
- Use the `config.py` module to access configuration

```python
from src.pipeline.config import load_config

# Load the configuration
config = load_config("config/pipeline_config.yaml")

# Access config values
data_dir = config.data.raw_dir
years = config.data.years
```

### 4.5 Logging

- Use the built-in logging framework
- Log messages should be informative and include context
- Don't use print statements for operational logging

```python
import logging

logger = logging.getLogger(__name__)

# Informative logs with context
logger.info(f"Processing season {season} data")
logger.error(f"Failed to load file: {file_path}")
```

## 5. Key Workflows

### 5.1 Pipeline Execution

The main entry point is `run_pipeline.py` which accepts command-line arguments to configure the pipeline execution:

```bash
# Run the full pipeline
python run_pipeline.py

# Run only specific stages
python run_pipeline.py --stages data features

# Process specific years
python run_pipeline.py --years 2023 2024

# Clean data before running
python run_pipeline.py --clean-raw
```

### 5.2 Data Processing Workflow

1. **Data Collection**: 
   - Raw data is downloaded from sportsdataverse GitHub repository
   - Data is stored in `data/raw/{category}/{year}.parquet`

2. **Data Cleaning**:
   - Raw data is processed to handle missing values, outliers, etc.
   - Cleaned data is stored in `data/processed/{category}/{year}.parquet`

3. **Feature Engineering**:
   - Features are created from processed data
   - Feature data is stored in `data/features/{feature_set}/{year}.parquet`

### 5.3 Model Training Workflow

1. **Data Preparation**:
   - Features are loaded and split into training/validation sets
   - Data is normalized/standardized as needed

2. **Model Training**:
   - PyTorch models are trained with specified hyperparameters
   - Models are evaluated using cross-validation

3. **Model Persistence**:
   - Trained models are saved to the `models/` directory
   - Model metadata is stored alongside model weights

### 5.4 Prediction Workflow

1. **Model Loading**:
   - Trained models are loaded from the `models/` directory

2. **Prediction Generation**:
   - Tournament match-ups are evaluated
   - Win probabilities are calculated

3. **Bracket Creation**:
   - Optimal brackets are generated based on predictions
   - Visualizations are created and saved to `visualizations/`

## 6. Common Pitfalls & Guidelines

### 6.1 Data Storage Locations

⚠️ **Common Mistake**: Writing data to incorrect locations

✅ **Correct Approach**:
- Raw data: `data/raw/{category}/{year}.parquet`
- Processed data: `data/processed/{category}/{year}.parquet`
- Feature data: `data/features/{feature_set}/{year}.parquet`

### 6.2 Data Processing vs. Feature Engineering

⚠️ **Common Mistake**: Mixing data processing with feature engineering or generating placeholder data during processing

✅ **Correct Approach**:
- **Data Processing**: Focus only on cleaning, standardizing, and organizing raw data
  - Only include metrics directly derivable from the raw data
  - Do not calculate advanced metrics or add synthetic/placeholder values
  - Store processed data in `data/processed/`

- **Feature Engineering**: Create derived metrics and features in a separate stage
  - Calculate advanced metrics like efficiency ratings, strength indicators, etc.
  - Apply transformations like normalization, encoding, etc.
  - Store engineered features in `data/features/`

```python
# CORRECT: Clean separation between processing and feature engineering

# Data processing: Clean and standardize raw data
def process_team_data(team_data: pl.DataFrame) -> pl.DataFrame:
    """Process team data without adding synthetic values."""
    return team_data.filter(
        pl.col("team_id").is_not_null()
    ).with_columns([
        pl.col("points").cast(pl.Float64),
        # Only transformations of existing data, no new metrics calculated
    ])

# Feature engineering: Calculate advanced metrics
def engineer_team_features(processed_data: pl.DataFrame) -> pl.DataFrame:
    """Calculate advanced team metrics as features."""
    return processed_data.with_columns([
        # Advanced metrics calculated here
        (pl.col("points") * 100 / pl.col("possessions")).alias("offensive_efficiency"),
        (pl.col("assists") / pl.col("field_goals_made")).alias("assist_rate")
    ])
```

### 6.3 Data Processing

⚠️ **Common Mistake**: Using Pandas instead of Polars, not handling missing data

✅ **Correct Approach**:
```python
import polars as pl

# Load data with Polars
data = pl.read_parquet(file_path)

# Handle missing values explicitly
data = data.filter(pl.col("team_id").is_not_null())

# Use Polars syntax for transformations
data = data.with_columns([
    pl.col("points").fill_null(0),
    (pl.col("fg_made") / pl.col("fg_attempted")).alias("fg_pct")
])
```

### 6.4 Pipeline Integration

⚠️ **Common Mistake**: Not following the stage-based pattern or ignoring configuration

✅ **Correct Approach**:
- Implement new processing as a pipeline stage
- Follow the existing logging and error handling patterns
- Respect configuration-driven behavior

### 6.5 File Paths

⚠️ **Common Mistake**: Using hardcoded paths or string concatenation

✅ **Correct Approach**:
```python
from pathlib import Path

# Get configuration
config = load_config("config/pipeline_config.yaml")
base_dir = Path(config.data.processed_dir)

# Construct paths properly
file_path = base_dir / category / f"{year}.parquet"
```

### 6.6 Error Handling

⚠️ **Common Mistake**: Not handling errors or using overly broad except clauses

✅ **Correct Approach**:
```python
try:
    data = pl.read_parquet(file_path)
except pl.exceptions.NoDataError:
    logger.error(f"File contains no data: {file_path}")
    return None
except Exception as e:
    logger.exception(f"Error loading data from {file_path}: {e}")
    raise
```

## 7. Documentation Organization

The project documentation follows a three-part structure designed to serve different user needs:

### 7.1 Documentation Structure

- **User Guide** (`docs/user_guide/`): 
  - Task-oriented documentation focused on "how to use it"
  - Contains practical, step-by-step instructions for users
  - Includes getting started guides, installation instructions, and usage examples
  - *Contribute here when*: Adding instructions for users on how to perform specific tasks

- **Technical Reference** (`docs/reference/`):
  - Reference-oriented documentation focused on "how it works"
  - Contains detailed technical specifications and architecture documentation
  - Includes data schemas, pipeline architecture details, and API references
  - *Contribute here when*: Documenting technical details about the system's internal structure

- **Developer Guide** (`docs/developer_guide/`):
  - Process-oriented documentation focused on "how to contribute"
  - Contains information for developers extending or modifying the project
  - Includes code standards, contribution guidelines, and extension examples
  - *Contribute here when*: Providing guidance for developers contributing to the project

### 7.2 Documentation Guidelines

When creating or updating documentation:

1. **Place content appropriately**:
   - User-facing instructions → User Guide
   - Technical specifications → Technical Reference
   - Development workflows → Developer Guide

2. **Maintain consistent style**:
   - Use Markdown formatting consistently
   - Follow the established section hierarchy
   - Include code examples where applicable

3. **Cross-reference between sections**:
   - Link to technical reference from user guides when additional details might be helpful
   - Reference user guides from developer documentation when explaining use cases

4. **Keep documentation synchronized with code**:
   - Update documentation when making significant code changes
   - Ensure examples in documentation reflect current API and workflows

When suggesting documentation improvements, identify which section would best house the new content according to this organization.

## 8. Code Examples

### 8.1 Feature Engineering Example

```python
def calculate_offensive_rating(team_stats: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate offensive rating for teams based on points and possessions.
    
    Args:
        team_stats: DataFrame with team statistics
        
    Returns:
        DataFrame with added offensive_rating column
    """
    return team_stats.with_columns([
        (pl.col("points") * 100 / pl.col("possessions")).alias("offensive_rating")
    ])
```

### 8.2 Data Loading Example

```python
def load_team_data(year: int, config: Config) -> pl.DataFrame:
    """
    Load team box score data for a specific season.
    
    Args:
        year: Season year (e.g., 2023)
        config: Pipeline configuration
        
    Returns:
        DataFrame with team statistics
    """
    # Construct file path
    data_dir = Path(config.data.raw_dir)
    file_path = data_dir / "team_box" / f"team_box_{year}.parquet"
    
    logger.info(f"Loading team data for {year} from {file_path}")
    
    try:
        # Define schema
        schema = {
            "game_id": pl.Int64,
            "team_id": pl.Int64,
            "team_name": pl.Utf8,
            "points": pl.Int32,
            # Other fields...
        }
        
        # Load data
        return pl.read_parquet(file_path, schema=schema)
    except Exception as e:
        logger.exception(f"Error loading team data for {year}: {e}")
        raise
```

### 8.3 Pipeline Stage Example

```python
def run_feature_engineering(
    years: list[int],
    config: Config,
    categories: list[str] = None
) -> bool:
    """
    Run the feature engineering stage of the pipeline.
    
    Args:
        years: List of years to process
        config: Pipeline configuration
        categories: Optional list of data categories to process
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Running feature engineering for years: {years}")
    
    feature_dir = Path(config.data.feature_dir)
    feature_dir.mkdir(exist_ok=True, parents=True)
    
    # Process each year
    for year in years:
        logger.info(f"Processing features for year {year}")
        
        try:
            # Load processed data
            team_data = load_processed_team_data(year, config)
            
            # Engineer features
            team_features = engineer_team_features(team_data)
            
            # Save features
            output_path = feature_dir / f"team_features_{year}.parquet"
            team_features.write_parquet(output_path)
            
            logger.info(f"Features saved to {output_path}")
        except Exception as e:
            logger.exception(f"Error processing features for {year}: {e}")
            return False
    
    return True
```

## 9. Quick Reference

### Data Sources
- Repository: sportsdataverse/hoopR-mbb-data
- URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/{category}/parquet/{filename}_{YEAR}.parquet`
- Categories: play_by_play, player_box, schedules, team_box
- Years: 2003-2025

### Key File Paths
- Raw data: `data/raw/{category}/{year}.parquet`
- Processed data: `data/processed/{category}/{year}.parquet`
- Features: `data/features/{feature_set}/{year}.parquet`
- Models: `models/{model_type}/{model_name}.pt`
- Visualizations: `visualizations/{viz_type}/{viz_name}.{ext}`

### Important Libraries
- Data Processing: `polars` (not pandas)
- Deep Learning: `torch`
- Visualization: `plotly`
- Configuration: `pyyaml`

### CLI Commands
```bash
# Full pipeline
python run_pipeline.py

# Specific stages
python run_pipeline.py --stages data features

# Specific years
python run_pipeline.py --years 2023 2024

# Specific categories
python run_pipeline.py --categories team_box player_box

# Clean data
python run_pipeline.py --clean-raw  # Clean raw data
python run_pipeline.py --clean-all  # Clean all data

# Custom configuration
python run_pipeline.py --config custom_config.yaml
``` 