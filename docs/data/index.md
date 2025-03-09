# NCAA March Madness Data Documentation

This section provides comprehensive documentation for the data used in the NCAA March Madness Predictor project, including data sources, processing methods, and organization.

## Overview

The NCAA March Madness Predictor uses historical NCAA basketball data from the sportsdataverse repository, covering 22+ years of games. Our data pipeline handles the downloading, cleaning, and transformation of this data, followed by feature engineering for model training.

## Data Documentation Structure

```
data/
├── index.md                 # This overview file
├── processing.md            # Data processing principles and methodology
└── reference/               # Technical reference for data
    ├── schema.md            # Data schemas and column definitions
    ├── validation.md        # Data validation rules and procedures
    └── directory_structure.md # File and directory organization
```

## Key Documentation

- [Data Processing](processing.md) - Principles and methodology for data cleaning and transformation
- [Data Schema Reference](reference/schema.md) - Detailed information about data formats and column definitions
- [Data Validation](reference/validation.md) - Rules and procedures for ensuring data quality
- [Directory Structure](reference/directory_structure.md) - Organization of data files and directories

## Data Flow

The project follows a strict separation between different stages of data:

1. **Raw Data**: Original, unmodified data from the sportsdataverse repository
2. **Processed Data**: Cleaned and standardized data, with consistent formats
3. **Feature Data**: Engineered features derived from processed data

This separation ensures data integrity and makes it clear which transformations have been applied at each stage.

## Data Categories

Our data is organized into four main categories:

1. **Play-by-Play Data**: Detailed event-level data for each game
2. **Player Box Scores**: Individual player statistics for each game
3. **Game Schedules**: Game scheduling information including date, time, location, etc.
4. **Team Box Scores**: Team-level statistics for each game

## Data Storage

- Raw data: `data/raw/{category}/{year}.parquet`
- Processed data: `data/processed/{category}/{year}.parquet`
- Feature data: `data/features/{feature_set}/{year}.parquet`

## Related Documentation

- [Feature System](../features/index.md) - Documentation for features derived from this data
- [Pipeline Documentation](../pipeline/index.md) - Information about the data processing pipeline 