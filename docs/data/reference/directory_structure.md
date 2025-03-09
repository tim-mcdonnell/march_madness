# Data Directory Structure

This document outlines the organization of data files in the NCAA March Madness Predictor project, explaining the purpose of each directory and the naming conventions used.

## Root Data Directory

```
data/
├── raw/                  # Original unmodified data
│   ├── play_by_play/     # Play-by-play data
│   ├── player_box/       # Player box scores
│   ├── schedules/        # Game schedules
│   └── team_box/         # Team box scores
├── processed/            # Cleaned and transformed data
│   ├── play_by_play.parquet
│   ├── player_box.parquet
│   ├── schedules.parquet
│   ├── team_box.parquet
│   └── team_season_statistics.parquet
├── features/             # Engineered features for modeling
│   ├── team_performance_metrics.parquet
│   ├── shooting_metrics.parquet
│   └── combined/
│       └── full_feature_set.parquet
└── download.log          # Log file for data downloads
```

## Raw Data

The `raw/` directory contains the unmodified data downloaded directly from the sportsdataverse repository. It is organized by data category:

```
raw/
├── play_by_play/         # Play-by-play data
│   ├── play_by_play_2003.parquet
│   ├── play_by_play_2004.parquet
│   └── ... (one file per season through 2025)
├── player_box/           # Player box scores
│   ├── player_box_2003.parquet
│   ├── player_box_2004.parquet
│   └── ... (one file per season through 2025)
├── schedules/            # Game schedules
│   ├── mbb_schedule_2003.parquet
│   ├── mbb_schedule_2004.parquet
│   └── ... (one file per season through 2025)
└── team_box/             # Team box scores
    ├── team_box_2003.parquet
    ├── team_box_2004.parquet
    └── ... (one file per season through 2025)
```

### Raw Data File Naming

- Files follow the pattern: `{category}_{year}.parquet`
- Exception for schedules: `mbb_schedule_{year}.parquet`
- Years range from 2003 through 2025

## Processed Data

The `processed/` directory contains cleaned and standardized versions of the raw data. Unlike the raw data, processed files are consolidated across all years:

```
processed/
├── play_by_play.parquet           # All play-by-play data across all seasons
├── player_box.parquet             # All player box scores across all seasons
├── schedules.parquet              # All game schedules across all seasons
├── team_box.parquet               # All team box scores across all seasons
└── team_season_statistics.parquet # Season-level aggregated team statistics
```

### Processed Data Transformations

Processed data has undergone the following transformations:
- Standardized column names
- Cleaned data types
- Removed duplicates
- Handled missing values
- Combined data across seasons into a single file per category
- Added computed values directly derivable from raw data

## Feature Data

The `features/` directory contains engineered features derived from the processed data, organized by feature category:

```
features/
├── team_performance_metrics.parquet  # Team performance features (T*)
├── shooting_metrics.parquet          # Shooting and scoring metrics (S*)
├── advanced_team_metrics.parquet     # Advanced team metrics (A*)
└── combined/
    └── full_feature_set.parquet      # All features combined for modeling
```

### Feature Data Organization

- Features are organized by category, matching the feature category structure in the codebase
- Each category file contains all features for that category
- The `combined/` directory contains merged feature sets for convenience

## Log Files

- `download.log`: Records all data download operations, including timestamps, success/failure status, and any error messages

## Important Notes

1. **Data Access Pattern**:
   - Raw data should never be modified directly
   - Always access processed data for analysis and feature engineering
   - Store derived metrics as features, not in processed data

2. **File Formats**:
   - All data is stored in Parquet format for efficiency
   - All data should be loaded using Polars, not Pandas

3. **Data Versioning**:
   - Raw data is versioned by season year
   - Processed data and features represent the latest version across all years 