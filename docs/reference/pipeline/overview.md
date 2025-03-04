# Pipeline Architecture Overview

This document provides a technical overview of the NCAA March Madness Predictor pipeline architecture.

## Pipeline Framework

The pipeline is implemented as a modular, configurable system with several key stages:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│     Data     │    │  Exploratory │    │   Feature   │    │    Model    │    │  Evaluation │
│   Pipeline   │───▶│   Analysis   │───▶│ Engineering │───▶│   Training  │───▶│      &      │
│     Stage    │    │     Stage    │    │    Stage    │    │    Stage    │    │ Prediction  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

Each stage can be run independently or as part of the complete pipeline.

## Key Components

### 1. Configuration Management

The pipeline uses a centralized configuration system that:

- Loads settings from YAML files
- Supports command-line overrides
- Provides environment variable integration
- Enforces validation on configuration values

```python
from src.utils.config import load_config

# Load configuration with potential overrides
config = load_config("configs/default.yml", overrides=command_line_args)
```

### 2. Data Management

The pipeline includes utilities for:

- Establishing and managing directory structure
- Tracking dataset versions and lineage
- Purging or archiving old data
- Caching intermediate results

```python
from src.utils.paths import get_path

# Get path to a specific dataset
data_path = get_path("processed", "team_season_statistics.parquet")
```

### 3. Pipeline Stages

#### Data Stage

The data stage:
- Downloads raw data from sources
- Validates data against schema definitions
- Cleans and standardizes data
- Processes data into normalized formats
- Saves processed datasets

```python
from src.pipeline.data import run_data_stage

# Run the data stage with configuration
run_data_stage(config)
```

#### Exploratory Analysis Stage

The exploratory analysis stage:
- Generates statistical summaries
- Creates visualization dashboards
- Identifies patterns and outliers
- Exports reports and visualizations

```python
from src.pipeline.exploratory import run_exploratory_stage

# Run the exploratory analysis stage
run_exploratory_stage(config)
```

#### Feature Engineering Stage

The feature engineering stage:
- Creates derived metrics and indicators
- Implements domain-specific basketball metrics
- Generates tournament-specific features
- Performs feature selection
- Exports features for modeling

```python
from src.pipeline.features import run_feature_stage

# Run the feature engineering stage
run_feature_stage(config)
```

#### Model Training Stage

The model training stage:
- Prepares training and validation datasets
- Trains predictive models
- Optimizes hyperparameters
- Saves trained models
- Records training metadata

```python
from src.pipeline.model import run_model_stage

# Run the model training stage
run_model_stage(config)
```

#### Evaluation & Prediction Stage

The evaluation and prediction stage:
- Evaluates model performance
- Generates tournament predictions
- Creates bracket visualizations
- Performs sensitivity analysis
- Exports prediction results

```python
from src.pipeline.evaluation import run_evaluation_stage
from src.pipeline.predict import run_prediction_stage

# Run evaluation and prediction stages
run_evaluation_stage(config)
run_prediction_stage(config)
```

### 4. Command-Line Interface

The pipeline provides a comprehensive CLI:

```
python -m src.pipeline.main [OPTIONS]

Options:
  --config TEXT                 Path to configuration file
  --stages TEXT                 Comma-separated list of stages to run
  --years TEXT                  Years to process (comma-separated)
  --force_download              Force redownload of data
  --model_type TEXT             Type of model to train
  --output_dir TEXT             Output directory
  --debug                       Enable debug mode
  --help                        Show this message and exit
```

## Pipeline Flow

The typical flow through the pipeline is:

1. **Configuration Loading**: Load and validate configuration
2. **Stage Selection**: Determine which stages to run
3. **Data Collection**: Download and validate data
4. **Data Processing**: Clean and standardize data
5. **Feature Engineering**: Create model-ready features
6. **Model Training**: Train and validate models
7. **Prediction**: Generate tournament predictions
8. **Visualization**: Create visualizations and reports

## Extending the Pipeline

The pipeline is designed to be extended with:

- New data sources
- Custom feature engineering approaches
- Alternative model architectures
- Additional evaluation metrics
- Custom visualization components

See the [Extending the Project](../../developer_guide/extending.md) guide for details.

## Parallel Processing

The pipeline supports parallel processing for performance optimization:

```python
# In configuration
system:
  n_jobs: 4  # Number of parallel jobs

# In code
from src.utils.parallel import parallelize

results = parallelize(process_function, items_to_process, n_jobs=config.system.n_jobs)
```

## Error Handling

The pipeline implements a comprehensive error handling strategy:

- Graceful degradation when components fail
- Detailed logging of errors and warnings
- Error recovery mechanisms when possible
- Validation at stage boundaries

## Logging

The pipeline includes a robust logging system:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Starting data processing")
logger.debug("Processing details: %s", details)
logger.warning("Missing data for %s", team_id)
logger.error("Failed to process %s", dataset_name)
```

## Examples

### Running the Full Pipeline

```bash
python -m src.pipeline.main
```

### Running Specific Stages

```bash
python -m src.pipeline.main --stages data,features,model
```

### Running with Custom Configuration

```bash
python -m src.pipeline.main --config configs/research_config.yml
```

### Running for Specific Years

```bash
python -m src.pipeline.main --years 2022,2023,2024
```

## Related Documentation

- [Pipeline Usage Guide](../../user_guide/pipeline_usage.md): Detailed usage instructions
- [Configuration Guide](../../user_guide/configuration.md): Configuration options and examples
- [Data Processing](../data/processing.md): Details on data processing procedures
- [Feature Engineering](../../examples/feature_engineering.md): Examples of feature engineering
- [Model Development](../models/overview.md): Information on model development 