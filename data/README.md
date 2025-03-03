# NCAA March Madness Data Directory

This directory contains data used for the NCAA March Madness prediction project.

## Directory Structure

```
data/
├── raw/                  # Original unmodified data
│   ├── play_by_play/     # Play-by-play data
│   ├── player_box/       # Player box scores
│   ├── schedules/        # Game schedules
│   └── team_box/         # Team box scores
├── processed/            # Cleaned and transformed data
└── download.log          # Log file for data downloads
```

## Data Sources

All data is sourced from the [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/) GitHub repository, which provides comprehensive NCAA men's basketball data.

### Raw Data Categories

1. **Play-by-Play Data**
   - File pattern: `play_by_play_{YEAR}.parquet`
   - Contains detailed event-level data for each game

2. **Player Box Scores**
   - File pattern: `player_box_{YEAR}.parquet`
   - Contains individual player statistics for each game

3. **Game Schedules**
   - File pattern: `mbb_schedule_{YEAR}.parquet`
   - Contains game scheduling information including date, time, location, etc.

4. **Team Box Scores**
   - File pattern: `team_box_{YEAR}.parquet`
   - Contains team-level statistics for each game

Files are available for seasons 2003 through 2025, providing 22+ years of historical data.

## Data Download

Data can be downloaded using the functions in `src/data/loader.py`. The main functions are:

```python
from src.data.loader import download_all_data

# Download all data for all years (2003-2025)
download_all_data()

# Download data for a specific year range
download_all_data(start_year=2020, end_year=2025)

# Download only specific categories
download_all_data(categories=["play_by_play", "team_box"])
```

## Data Loading

Parquet files can be loaded using the functions in `src/data/loader.py`. The main functions are:

```python
from src.data.loader import load_category_data

# Load play-by-play data for 2023
pbp_data = load_category_data("play_by_play", 2023)

# Load team box scores for 2023
team_box_data = load_category_data("team_box", 2023)
```

## Notes

- The raw data files can be large, especially for play-by-play data
- Downloads are cached, so repeated calls to download functions will skip files that already exist (unless `overwrite=True` is specified)
- Progress and errors during download are logged in `data/download.log` 