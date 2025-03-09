# NCAA Basketball Data Overview

This document provides a high-level overview of how data is handled in the NCAA March Madness Predictor project.

## Data Philosophy

The project maintains a strict separation between different data handling stages:

1. **Data Collection**: Fetching raw data from sources
2. **Data Validation**: Ensuring data quality and consistency
3. **Data Processing**: Cleaning and standardizing raw data
4. **Feature Engineering**: Creating derived metrics and model-ready features

This separation ensures clean, maintainable code and a clear understanding of where and how data transformations occur.

## Data Sources

All data is sourced from the [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/) GitHub repository, which provides comprehensive NCAA men's basketball data in four main categories:

1. **Play-by-Play Data**: Detailed event-level data for each game
2. **Player Box Scores**: Individual player statistics for each game
3. **Game Schedules**: Game scheduling information
4. **Team Box Scores**: Team-level statistics for each game

Files are available for seasons 2003 through 2025, providing 22+ years of historical data.

## Data Pipeline

The data flows through the pipeline in these stages:

```
Raw Data → Validation → Processing → Feature Engineering → Model Training
```

Each stage has specific responsibilities:

- **Raw Data**: Original unmodified data from the source
- **Validation**: Schema validation and data consistency checks
- **Processing**: Cleaning, standardization, and basic aggregation
- **Feature Engineering**: Creation of advanced metrics and model features

## Directory Structure

```
data/
├── raw/                  # Original unmodified data
│   ├── play_by_play/     # Play-by-play data
│   ├── player_box/       # Player box scores
│   ├── schedules/        # Game schedules
│   └── team_box/         # Team box scores
├── processed/            # Cleaned and standardized data
├── features/             # Engineered features for modeling
└── download.log          # Log file for data downloads
```

## Key Principles

1. **No Synthetic Data**: Processing only works with values directly derivable from the source data
2. **Separation of Concerns**: Clear boundaries between data stages
3. **Validation First**: Validate data before processing
4. **Documentation**: All data transformations are documented
5. **Reproducibility**: All data operations can be reproduced from raw data

## Related Documentation

- [Data Cleaning](cleaning.md): How data cleaning is implemented
- [Data Processing](processing.md): Data processing procedures
- [Data Validation](validation.md): Schema validation framework
- [Data Schema](schema.md): Reference for data schemas 