# Configuration Guide

The NCAA March Madness Predictor uses a flexible configuration system based on YAML files. This guide explains how to customize the behavior of the predictor through configuration.

## Configuration Overview

Configuration in the March Madness Predictor serves several purposes:

1. Control which data is processed
2. Customize feature engineering
3. Select and configure prediction models
4. Define evaluation metrics
5. Specify output formats and locations

## Configuration File Structure

A typical configuration file has the following structure:

```yaml
# Main configuration sections
data:
  # Data loading and processing options
  
features:
  # Feature engineering options
  
model:
  # Model selection and training options
  
evaluation:
  # Evaluation and prediction options
  
output:
  # Output and visualization options
```

## Default Configuration

The system includes a default configuration file at `configs/default.yaml`. This file defines sensible defaults for all configurable parameters:

```yaml
# Default configuration
data:
  years: [2018, 2019, 2020, 2021, 2022, 2023, 2024]
  force_download: false
  include_play_by_play: true
  validation_enabled: true
  cleaning_rules: ["duplicates", "missing_values", "outliers"]
  
features:
  advanced_stats: true
  strength_of_schedule: true
  momentum_features: true
  tournament_experience: true
  feature_selection: true
  
model:
  type: "ensemble"
  hyperparameter_tuning: true
  cross_validation_folds: 5
  test_size: 0.2
  random_state: 42
  
evaluation:
  metrics: ["accuracy", "log_loss", "brier_score"]
  simulation_runs: 1000
  export_predictions: true
  
output:
  prediction_format: "csv"
  visualizations: true
  reports: true
```

## Data Configuration Options

The `data` section controls data loading and processing:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `years` | list | `[2018-2024]` | Years of data to process |
| `force_download` | boolean | `false` | Force redownload of data |
| `include_play_by_play` | boolean | `true` | Include play-by-play data |
| `validation_enabled` | boolean | `true` | Enable data validation |
| `cleaning_rules` | list | (see default) | Data cleaning rules to apply |

Example:

```yaml
data:
  years: [2022, 2023, 2024]
  force_download: true
  include_play_by_play: false  # Exclude play-by-play for faster processing
```

## Feature Configuration Options

The `features` section controls feature engineering:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `advanced_stats` | boolean | `true` | Include advanced statistical features |
| `strength_of_schedule` | boolean | `true` | Include strength of schedule features |
| `momentum_features` | boolean | `true` | Include team momentum features |
| `tournament_experience` | boolean | `true` | Include tournament experience features |
| `feature_selection` | boolean | `true` | Apply feature selection |
| `scaling` | string | `"standard"` | Feature scaling method (`none`, `standard`, `minmax`) |

Example:

```yaml
features:
  advanced_stats: true
  strength_of_schedule: true
  momentum_features: true
  tournament_experience: false  # Exclude tournament experience
  feature_selection: true
  scaling: "standard"
```

## Model Configuration Options

The `model` section controls model selection and training:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | `"ensemble"` | Model type (`logistic`, `lgbm`, `random_forest`, `ensemble`) |
| `hyperparameter_tuning` | boolean | `true` | Enable hyperparameter tuning |
| `cross_validation_folds` | integer | `5` | Number of cross-validation folds |
| `test_size` | float | `0.2` | Proportion of data to use for testing |
| `random_state` | integer | `42` | Random seed for reproducibility |
| `early_stopping` | boolean | `true` | Enable early stopping during training |

### Model-Specific Options

Each model type has its own specific configuration options:

#### Logistic Regression

```yaml
model:
  type: "logistic"
  logistic:
    penalty: "l2"
    C: 1.0
    class_weight: "balanced"
```

#### LightGBM

```yaml
model:
  type: "lgbm"
  lgbm:
    boosting_type: "gbdt"
    num_leaves: 31
    max_depth: -1
    learning_rate: 0.1
    n_estimators: 100
```

#### Random Forest

```yaml
model:
  type: "random_forest"
  random_forest:
    n_estimators: 100
    max_depth: null
    min_samples_split: 2
    min_samples_leaf: 1
```

#### Ensemble

```yaml
model:
  type: "ensemble"
  ensemble:
    models: ["logistic", "lgbm", "random_forest"]
    weights: [0.2, 0.4, 0.4]
```

## Evaluation Configuration Options

The `evaluation` section controls model evaluation and predictions:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `metrics` | list | (see default) | Metrics to evaluate |
| `simulation_runs` | integer | `1000` | Number of tournament simulations |
| `export_predictions` | boolean | `true` | Export predictions to files |
| `historical_evaluation` | boolean | `false` | Evaluate on historical tournaments |
| `test_years` | list | (empty) | Years to use for testing |

Example:

```yaml
evaluation:
  metrics: ["accuracy", "log_loss", "brier_score"]
  simulation_runs: 5000  # More simulations for better estimation
  export_predictions: true
  historical_evaluation: true
  test_years: [2021, 2022, 2023]
```

## Output Configuration Options

The `output` section controls output formats and locations:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `prediction_format` | string | `"csv"` | Format for predictions (`csv`, `json`) |
| `visualizations` | boolean | `true` | Generate visualizations |
| `reports` | boolean | `true` | Generate evaluation reports |
| `output_dir` | string | `"predictions"` | Directory for outputs |

Example:

```yaml
output:
  prediction_format: "json"
  visualizations: true
  reports: true
  output_dir: "predictions/2024"
```

## Creating Custom Configuration Files

You can create custom configuration files for different scenarios:

1. Create a new YAML file in the `configs/` directory
2. Override the default values as needed
3. Use the custom configuration with the `--config` parameter

Example:

```yaml
# configs/tournament_prediction.yaml
data:
  years: [2018, 2019, 2020, 2021, 2022, 2023]
  force_download: false
  
features:
  advanced_stats: true
  strength_of_schedule: true
  
model:
  type: "ensemble"
  hyperparameter_tuning: false  # Use pre-tuned hyperparameters
  
evaluation:
  simulation_runs: 10000  # High number of simulations for tournament
  
output:
  visualizations: true
  output_dir: "predictions/tournament_2024"
```

## Using Configuration Files

To use a custom configuration file:

```bash
python -m src.pipeline.main --config configs/tournament_prediction.yaml
```

## Overriding Configuration Parameters

You can override specific configuration parameters from the command line:

```bash
python -m src.pipeline.main --config configs/default.yaml --param data.years=[2022,2023] --param model.type=lgbm
```

This allows you to make quick changes without editing configuration files.

## Configuration Hierarchy

The system uses a configuration hierarchy:

1. Default configuration (`configs/default.yaml`)
2. Custom configuration file (if specified with `--config`)
3. Command-line overrides (if specified with `--param`)

Later values override earlier ones, allowing for flexible configuration.

## Environment Variables

Some configuration options can be set using environment variables:

```bash
# Set data directory
export MARCH_MADNESS_DATA_DIR="/path/to/data"

# Set output directory
export MARCH_MADNESS_OUTPUT_DIR="/path/to/output"

# Set log level
export MARCH_MADNESS_LOG_LEVEL="DEBUG"
```

## Configuration Validation

The system validates configurations to ensure they're valid:

1. Required fields are present
2. Values are of the correct type
3. Enumerations contain valid values
4. Numeric values are within acceptable ranges

If validation fails, the system will report specific errors.

## Configuration Examples

### Quick Prediction

```yaml
# configs/quick_prediction.yaml
data:
  years: [2023, 2024]
  include_play_by_play: false
  
features:
  advanced_stats: true
  strength_of_schedule: true
  momentum_features: false
  tournament_experience: false
  
model:
  type: "lgbm"
  hyperparameter_tuning: false
  
evaluation:
  simulation_runs: 100
  
output:
  prediction_format: "csv"
  visualizations: true
```

### Comprehensive Model

```yaml
# configs/comprehensive_model.yaml
data:
  years: [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
  include_play_by_play: true
  
features:
  advanced_stats: true
  strength_of_schedule: true
  momentum_features: true
  tournament_experience: true
  feature_selection: true
  
model:
  type: "ensemble"
  hyperparameter_tuning: true
  cross_validation_folds: 10
  
evaluation:
  metrics: ["accuracy", "log_loss", "brier_score", "calibration"]
  simulation_runs: 5000
  historical_evaluation: true
  test_years: [2018, 2019, 2021, 2022, 2023]
```

## Related Documentation

- [Pipeline Usage Guide](pipeline_usage.md)
- [Getting Started Guide](getting_started.md)
- [Pipeline Architecture](../reference/pipeline/overview.md) 