# NCAA March Madness Pipeline Documentation

This section documents the pipeline architecture for the NCAA March Madness Predictor project, explaining the different stages, their interactions, and how to use the pipeline.

## Pipeline Overview

The NCAA March Madness Predictor uses a modular pipeline architecture that orchestrates data processing, feature engineering, model training, and prediction. This approach ensures:

- **Modularity**: Each stage has a clear responsibility
- **Reproducibility**: The entire process can be consistently reproduced
- **Configurability**: Pipeline behavior can be adjusted via configuration
- **Traceability**: Each step is logged for transparency

## Pipeline Stages

The pipeline is organized into distinct stages:

1. **Data Collection Stage**:
   - Fetches data from sportsdataverse repository
   - Stores raw files in `data/raw/` directory
   - Does not modify the original data

2. **Data Processing Stage**:
   - Cleans and standardizes raw data
   - Combines data across seasons into consistent formats
   - Outputs to `data/processed/` directory

3. **Feature Engineering Stage**:
   - Creates derived metrics using the `BaseFeature` system
   - Applies transformations and calculations
   - Organizes features by category
   - Outputs to `data/features/` directory

4. **Model Training Stage**:
   - Trains predictive models using engineered features
   - Tunes hyperparameters
   - Evaluates model performance
   - Saves models to `models/` directory

5. **Bracket Generation Stage**:
   - Applies trained models to create optimized brackets
   - Generates visualizations
   - Outputs to `reports/` directory

## Pipeline Architecture

```
src/pipeline/
├── __init__.py     # Package definition
├── cli.py          # Command-line interface
├── config.py       # Configuration management
├── data_stage.py   # Data collection/processing implementation
├── feature_stage.py # Feature engineering implementation
├── model_stage.py  # Model training implementation
└── data_management.py # Data cleaning/purging utilities
```

## Pipeline Configuration

The pipeline is configured via a YAML file (`config/pipeline_config.yaml`):

```yaml
# Example configuration
data:
  raw_dir: "data/raw"
  processed_dir: "data/processed"
  feature_dir: "data/features"
  model_dir: "models"
  results_dir: "results"
  years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
  categories: ["play_by_play", "player_box", "schedules", "team_box"]

features:
  # Feature configuration

model:
  # Model configuration
```

## Using the Pipeline

### Command-Line Interface

The pipeline is primarily used through its command-line interface:

```bash
# Run the full pipeline
python run_pipeline.py

# Run only specific stages
python run_pipeline.py --stages data features

# Process specific years
python run_pipeline.py --years 2023 2024

# Process specific data categories
python run_pipeline.py --categories team_box player_box

# Calculate specific feature categories
python run_pipeline.py --stages features --feature-categories shooting team_performance

# Calculate specific features by ID
python run_pipeline.py --stages features --feature-ids S01 T01

# Clean data before running
python run_pipeline.py --clean-raw      # Clean raw data
python run_pipeline.py --clean-all      # Clean all data

# Use a custom configuration
python run_pipeline.py --config custom_config.yaml
```

### Programmatic Interface

You can also use the pipeline programmatically:

```python
from src.pipeline.config import load_config
from src.pipeline.data_stage import run_data_stage
from src.pipeline.feature_stage import FeatureCalculationStage

# Load configuration
config = load_config("config/pipeline_config.yaml")

# Run data stage
run_data_stage(config)

# Run feature stage
feature_stage = FeatureCalculationStage(config)
feature_stage.run(feature_ids=["S01", "T01"])
```

## Stage Dependencies

The pipeline stages have the following dependencies:

1. **Data Collection** → No dependencies
2. **Data Processing** → Depends on Data Collection
3. **Feature Engineering** → Depends on Data Processing
4. **Model Training** → Depends on Feature Engineering
5. **Bracket Generation** → Depends on Model Training

The pipeline enforces these dependencies when running multiple stages together.

## Pipeline Outputs

Each stage produces the following outputs:

1. **Data Collection**: Raw data files in `data/raw/`
2. **Data Processing**: Processed data files in `data/processed/`
3. **Feature Engineering**: Feature files in `data/features/`
4. **Model Training**: Trained models in `models/`
5. **Bracket Generation**: Visualizations and reports in `reports/`

## Logging and Monitoring

The pipeline includes comprehensive logging:

- **Log Files**: Log files are stored in `logs/`
- **Console Output**: Progress and errors are displayed in the console
- **Timing Information**: Each stage reports execution time

## Related Documentation

- [Data Documentation](../data/index.md) - Information about the data processed by the pipeline
- [Feature Documentation](../features/index.md) - Documentation for features generated by the pipeline 