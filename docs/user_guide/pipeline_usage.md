# Pipeline Usage Guide

This guide provides detailed information on using the NCAA March Madness Predictor pipeline to generate basketball tournament predictions.

## Pipeline Overview

The NCAA March Madness Predictor uses a modular pipeline architecture to process data, engineer features, train models, and generate predictions. The pipeline consists of five main stages:

1. **Data Stage**: Download, validate, clean, and process data
2. **Exploratory Analysis Stage**: Generate statistical summaries and visualizations
3. **Feature Engineering Stage**: Create derived metrics and features
4. **Model Training Stage**: Train and validate prediction models
5. **Evaluation & Prediction Stage**: Evaluate models and generate tournament predictions

## Running the Full Pipeline

To run the entire pipeline with default settings:

```bash
python -m src.pipeline.main
```

This will execute all stages in sequence with the default configuration.

## Running Specific Pipeline Stages

You can run specific stages of the pipeline:

```bash
# Run only the data stage
python -m src.pipeline.main --stage data

# Run only the exploratory analysis stage
python -m src.pipeline.main --stage exploratory

# Run only the feature engineering stage
python -m src.pipeline.main --stage features

# Run only the model training stage
python -m src.pipeline.main --stage model

# Run only the evaluation stage
python -m src.pipeline.main --stage evaluate
```

## Specifying Seasons

You can specify which seasons to process:

```bash
# Process only the 2023 season
python -m src.pipeline.main --years 2023

# Process multiple seasons
python -m src.pipeline.main --years 2021 2022 2023

# Process a range of seasons
python -m src.pipeline.main --years 2018-2023
```

## Configuration Options

### Using Configuration Files

The pipeline can be configured using YAML configuration files:

```bash
# Use a specific configuration file
python -m src.pipeline.main --config configs/advanced_features.yaml
```

### Overriding Configuration Parameters

You can override specific configuration parameters from the command line:

```bash
# Override specific parameters
python -m src.pipeline.main --param data.years=[2022,2023] --param features.advanced_stats=True
```

### Configuration File Structure

A typical configuration file looks like:

```yaml
# configs/example.yaml
data:
  years: [2022, 2023]
  force_download: False
  include_play_by_play: True
  
features:
  advanced_stats: True
  strength_of_schedule: True
  momentum_features: True
  tournament_experience: True
  
model:
  type: "ensemble"
  hyperparameter_tuning: True
  cross_validation_folds: 5
  
evaluation:
  metrics: ["accuracy", "log_loss", "brier_score"]
  simulation_runs: 1000
```

## Advanced Pipeline Options

### Parallel Processing

Enable parallel processing for faster execution:

```bash
python -m src.pipeline.main --parallel
```

### Caching Results

The pipeline caches intermediate results to speed up reruns. To force recomputation:

```bash
python -m src.pipeline.main --no_cache
```

To clear all cached results:

```bash
python -m src.pipeline.main --clear_cache
```

### Verbose Output

For more detailed logging:

```bash
python -m src.pipeline.main --verbose
```

## Running with Different Model Types

You can specify different model types:

```bash
# Use a logistic regression model
python -m src.pipeline.main --param model.type=logistic

# Use a LightGBM model
python -m src.pipeline.main --param model.type=lgbm

# Use a Random Forest model
python -m src.pipeline.main --param model.type=random_forest

# Use an ensemble of models
python -m src.pipeline.main --param model.type=ensemble
```

## Generating Tournament Predictions

To generate predictions for the current NCAA tournament:

```bash
python -m src.pipeline.main --tournament_year 2024
```

This will:
1. Use historical data to train the model
2. Load the current tournament bracket
3. Generate win probabilities for all possible matchups
4. Create a bracket prediction

## Customizing Feature Engineering

To control which features are generated:

```bash
# Generate only basic features
python -m src.pipeline.main --param features.advanced_stats=False

# Include strength of schedule features
python -m src.pipeline.main --param features.strength_of_schedule=True

# Include momentum-based features
python -m src.pipeline.main --param features.momentum_features=True
```

## Running Hyperparameter Tuning

To tune model hyperparameters:

```bash
python -m src.pipeline.main --param model.hyperparameter_tuning=True --param model.tuning_trials=50
```

## Bracket Simulation

To run simulations of the tournament:

```bash
python -m src.pipeline.main --param evaluation.simulation_runs=10000
```

This will simulate the tournament multiple times to estimate each team's chances of advancing to different rounds.

## Export Options

You can specify output formats for predictions:

```bash
# Export predictions to CSV
python -m src.pipeline.main --param export.format=csv

# Export predictions to JSON
python -m src.pipeline.main --param export.format=json

# Export visualizations
python -m src.pipeline.main --param export.visualizations=True
```

## Logging

The pipeline logs information to both the console and log files:

```bash
# Set logging level to DEBUG
python -m src.pipeline.main --log_level debug

# Specify a custom log file
python -m src.pipeline.main --log_file custom_log.txt
```

## Examples of Common Workflows

### Quick Prediction Workflow

```bash
# Download latest data, train on historical data, predict current tournament
python -m src.pipeline.main --years 2010-2023 --tournament_year 2024
```

### Model Comparison Workflow

```bash
# Train and evaluate multiple model types
for model_type in logistic lgbm random_forest ensemble; do
    python -m src.pipeline.main --stage model --param model.type=$model_type --param evaluation.save_metrics=True
done

# Compare results
python -m src.pipeline.evaluate --compare_models
```

### Feature Importance Analysis

```bash
# Generate features and analyze importance
python -m src.pipeline.main --stage features --param features.importance_analysis=True
```

### Historical Accuracy Evaluation

```bash
# Evaluate prediction accuracy on historical tournaments
python -m src.pipeline.main --param evaluation.historical_evaluation=True --param evaluation.test_years=[2018,2019,2021,2022,2023]
```

## Troubleshooting Pipeline Issues

### Missing Data

If you encounter errors about missing data:

```bash
# Check data availability
python -m src.data.validator --check_availability

# Download missing data
python -m src.data.loader --years 2018-2023
```

### Model Performance Issues

If your model performance is poor:

```bash
# Run with more extensive feature engineering
python -m src.pipeline.main --param features.comprehensive=True

# Try different model types
python -m src.pipeline.main --param model.type=ensemble

# Analyze feature importance to identify useful features
python -m src.pipeline.features --importance_analysis
```

### Memory Issues

If you encounter memory problems:

```bash
# Process one year at a time
for year in {2018..2023}; do
    python -m src.pipeline.main --years $year
done

# Reduce the data volume by excluding play-by-play data
python -m src.pipeline.main --param data.include_play_by_play=False
```

## Related Documentation

- [Getting Started Guide](getting_started.md)
- [Configuration Guide](configuration.md)
- [Data Reference](../reference/data/overview.md)
- [Model Reference](../reference/models/overview.md)
- [Feature Engineering Example](../examples/feature_engineering.md) 