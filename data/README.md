# Data Directory

This directory contains both raw and processed data for the NCAA March Madness Predictor project.

## Structure

- `raw/`: Original unmodified data from sportsdataverse/hoopR-mbb-data
- `processed/`: Cleaned and transformed data ready for model training

## Data Sources

All data comes from the sportsdataverse's hoopR-mbb-data GitHub repository:
- Repository: [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/)

## Data Categories

1. **Play-by-Play Data**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/pbp/parquet/play_by_play_{YEAR}.parquet`

2. **Player Box Scores**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/player_box/parquet/player_box_{YEAR}.parquet`

3. **Game Schedules**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/schedules/parquet/mbb_schedule_{YEAR}.parquet`

4. **Team Box Scores**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/team_box/parquet/team_box_{YEAR}.parquet`

## Data Processing Pipeline

The data processing pipeline consists of the following steps:

1. Download raw parquet files from GitHub
2. Clean and preprocess (handling missing values, etc.)
3. Feature engineering to create predictive variables
4. Combine datasets for model training

Please refer to the notebooks in the `notebooks/` directory for detailed examples of the data processing workflow. 