# Pipeline Overview

> **Documentation Relocated**: This document has been consolidated into the main pipeline documentation. 
> 
> Please see the [Pipeline Architecture Overview](../reference/pipeline/overview.md) for the complete and updated documentation.

This page has been moved as part of documentation reorganization to reduce redundancy and improve content organization.

The NCAA March Madness Predictor uses a modular pipeline architecture to process data, train models, and generate predictions. This page provides an overview of the pipeline components and how they work together.

## Pipeline Architecture

The pipeline is built around a series of stages that can be run independently or as a complete end-to-end workflow:

```
Data Collection → Exploratory Analysis → Feature Engineering → Model Development → Evaluation
```

Each stage is implemented as a separate module that can:
- Be configured through the central YAML configuration
- Be executed individually or as part of the full pipeline
- Access outputs from previous stages
- Produce well-defined outputs for subsequent stages

## Key Components

### Configuration Management

The pipeline uses a centralized configuration system (`src/pipeline/config.py`) that:
- Loads settings from a YAML file (`config/pipeline_config.yaml`)
- Validates configuration against required fields
- Provides defaults for missing values
- Can generate a default configuration if none exists

### Data Management

Data management utilities (`src/pipeline/data_management.py`) provide:
- Directory structure enforcement
- Data purging capabilities (selective or complete)
- Consistent file path handling across the pipeline

### Command-Line Interface

The pipeline can be controlled through a flexible CLI (`src/pipeline/cli.py`) that offers:
- Selection of specific pipeline stages
- Filtering by years and data categories
- Data cleaning options
- Logging configuration

### Pipeline Stages

#### 1. Data Collection Stage

The data stage (`src/pipeline/data_stage.py`):
- Downloads NCAA basketball data from the hoopR-mbb-data repository
- Organizes data by year and category
- Implements smart caching to avoid redundant downloads
- Provides data loading functions for subsequent stages

#### 2. Exploratory Data Analysis Stage
*(Not yet implemented)*

This stage will:
- Generate statistical summaries of the data
- Create visualizations of key trends and patterns
- Identify correlations between variables
- Produce reports for data understanding

#### 3. Feature Engineering Stage
*(Not yet implemented)*

This stage will:
- Transform raw data into predictive features
- Calculate advanced basketball metrics
- Generate team performance indicators
- Create feature matrices for model training

#### 4. Model Development Stage
*(Not yet implemented)*

This stage will:
- Train predictive models on historical data
- Optimize hyperparameters
- Implement various model architectures
- Create model persistence functionality

#### 5. Evaluation Stage
*(Not yet implemented)*

This stage will:
- Assess model performance on test data
- Generate predictions for tournament matchups
- Simulate tournament brackets
- Create visualizations of model results

## Pipeline Flow

The main pipeline script (`run_pipeline.py`) orchestrates the flow:
1. Parses command-line arguments
2. Loads configuration
3. Enables appropriate logging
4. Executes requested pipeline stages
5. Collects and reports results

## Running the Pipeline

The pipeline can be run using the `run_pipeline.py` script:

```bash
# Run the full pipeline
python run_pipeline.py

# Run specific stages
python run_pipeline.py --stages data features

# Run with specific data filters
python run_pipeline.py --years 2023 2024 --categories team_box player_box

# Clean data before running
python run_pipeline.py --clean-raw
```

## CI/CD Integration

The pipeline is integrated with GitHub Actions for continuous integration and deployment:
- Scheduled runs during basketball season
- Manual execution via workflow dispatch
- Data caching for efficiency
- Results logging and artifact storage 