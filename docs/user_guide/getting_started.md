# Getting Started

This guide will help you quickly get started with the NCAA March Madness Predictor. We'll cover basic installation, downloading data, and running your first prediction.

## Quick Installation

First, make sure you have Python 3.10 or higher installed. Then set up the project:

```bash
# Clone the repository
git clone https://github.com/your-username/march_madness.git
cd march_madness

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

For detailed installation instructions, see the [Installation Guide](installation.md).

## Downloading Data

The NCAA March Madness Predictor uses data from the sportsdataverse/hoopR-mbb-data repository. To download data for recent seasons:

```bash
# Download data for the last three seasons
python -m src.data.loader --years 2022 2023 2024
```

This will download the necessary data files to the `data/raw/` directory.

## Processing the Data

After downloading the raw data, you need to process it:

```bash
# Process the data
python -m src.pipeline.data
```

This will:
- Validate the raw data
- Clean and standardize the data
- Generate processed datasets in `data/processed/`

## Running a Quick Prediction

To generate predictions for the current NCAA tournament:

```bash
# Run the full pipeline for the current year
python -m src.pipeline.main --years 2024
```

This command runs the complete pipeline:
1. Downloads and processes data (if not already done)
2. Generates features
3. Trains a prediction model
4. Makes tournament predictions
5. Creates a bracket visualization

## Viewing Your Results

After running the pipeline, you can find your results:

- **Bracket Visualization**: `predictions/bracket_2024.html`
- **Prediction CSVs**: `predictions/tournament_predictions_2024.csv`
- **Model Files**: `models/ensemble_model.joblib`

## Next Steps

Now that you've run your first prediction, here are some things you might want to explore:

### Customizing the Model

Try using different model types:

```bash
python -m src.pipeline.model --model_type lgbm  # Use LightGBM model
```

### Analyzing Team Data

Explore the processed data to understand team performance:

```python
import polars as pl

# Load team season statistics
team_stats = pl.read_parquet("data/processed/team_season_statistics.parquet")

# Filter for a specific team and season
gonzaga_2023 = team_stats.filter(
    (pl.col("team_name") == "Gonzaga") & 
    (pl.col("season") == 2023)
)

print(gonzaga_2023)
```

### Running Exploratory Analysis

Generate exploratory visualizations:

```bash
python -m src.pipeline.exploratory --seasons 2023 2024
```

This will create visualizations in the `reports/figures/` directory.

## Common Issues and Solutions

### Missing Data

If you encounter errors about missing data, ensure you've downloaded and processed the necessary seasons:

```bash
# Check what data is available
ls data/raw/
ls data/processed/

# Download missing data
python -m src.data.loader --years 2020 2021 2022 2023 2024
```

### Memory Issues

If you run into memory problems:

```bash
# Process one season at a time
python -m src.pipeline.data --years 2024

# Use a lighter model
python -m src.pipeline.model --model_type lgbm
```

### Updating Data

To get the latest data during tournament season:

```bash
python -m src.data.loader --years 2024 --force_download
python -m src.pipeline.data --years 2024
```

## Where to Go Next

- [Pipeline Usage Guide](pipeline_usage.md): Learn more about the pipeline options
- [Configuration Guide](configuration.md): Customize the behavior of the predictor 