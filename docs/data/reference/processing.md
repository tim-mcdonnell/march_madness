# Data Processing Documentation

This document outlines the data processing procedures implemented for the NCAA March Madness prediction system.

## Overview

The data processing stage focuses solely on cleaning, standardizing, and organizing the raw NCAA basketball data. Following the project's philosophy, this stage:

1. Performs essential cleaning and standardization of raw data
2. Ensures consistent data types and column names across all files
3. Only includes metrics directly derivable from the source data
4. Does NOT add synthetic values, placeholders, or calculated metrics

Advanced metrics and derived features are created in the separate feature engineering stage.

## Schema Normalization

The schema normalization process ensures that all data frames across different years have a consistent set of columns, even if the original data had different schemas. This is particularly important for data from different years, as the NCAA data format has evolved over time. The main steps in schema normalization include:

1. Identifying all unique columns across all years
2. Determining the best data type for each column
3. Adding missing columns to each data frame with null values
4. Ensuring consistent data types across all data frames

The `normalize_schema` function in `src/data/transformer.py` handles this process and is automatically applied during data loading.

## Processed Datasets

The data processing pipeline creates the following standardized datasets in the `data/processed/` directory:

### 1. play_by_play.parquet

A comprehensive dataset containing detailed event-level data for each play in each game, including:
- Game and play identification
- Team information
- Play type and description
- Scoring information
- Player involvement
- Game clock and period information
- Spatial coordinates (when available)

### 2. player_box.parquet

A detailed record of individual player statistics for each game, including:
- Player identification and basic information
- Team affiliation
- Game participation details
- Standard basketball statistics (points, rebounds, assists, etc.)
- Game context information

### 3. schedules.parquet

Complete game scheduling information for all games played, including:
- Game identification
- Team information
- Game date and time
- Venue information
- Attendance figures
- Game type indicators

### 4. team_box.parquet

Game-level team statistics for each team in each game played, including:
- Game identification
- Team information
- Standard team statistics
- Shooting percentages
- Opponent information
- Game date and context

### 5. team_season_statistics.parquet

Season-level aggregated statistics for each team across all games played, including:
- Team identification
- Games played counts
- Win/loss records
- Points scored and allowed
- Home/away performance metrics

These datasets contain only cleaned, standardized data without advanced derived metrics, which are created in the feature engineering stage.

## Usage

The processed datasets can be loaded using the functions in `src/data/loader.py`:

```python
from src.data.loader import load_processed_data

# Load team season statistics
team_stats = load_processed_data("team_season_statistics")

# Load team box scores
team_box = load_processed_data("team_box")

# Load player box scores
player_box = load_processed_data("player_box")
```

You can also regenerate these processed datasets using the `process_all_transformations` function from `src/data/transformer.py` or by running the appropriate pipeline stage. 