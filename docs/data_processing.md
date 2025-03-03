# Data Processing Documentation

## Schema Normalization

The schema normalization process ensures that all data frames across different years have a consistent set of columns, even if the original data had different schemas. This is particularly important for data from different years, as the NCAA data format has evolved over time. The main steps in schema normalization include:

1. Identifying all unique columns across all years
2. Determining the best data type for each column
3. Adding missing columns to each data frame with null values
4. Ensuring consistent data types across all data frames

The `normalize_schema` function in `src/data/transformer.py` handles this process and is automatically applied during data loading.

## Merged Datasets for Analysis

The data processing pipeline creates four key integrated datasets that combine information from various source files and add derived metrics to facilitate analysis:

### 1. Team Performance Dataset (`team_performance.parquet`)

A comprehensive dataset containing season-level team statistics with advanced metrics:

- Offensive and defensive efficiency (points per 100 possessions)
- Net efficiency
- Strength-of-schedule adjusted efficiency
- Four Factors metrics (shooting, turnovers, rebounding, free throws)
- Conference performance metrics

This dataset is ideal for team evaluation, comparison, and trend analysis.

### 2. Tournament History Dataset (`tournament_history.parquet`)

A detailed record of all NCAA tournament games with team performance metrics for both the winning and losing teams:

- Team statistics prior to the tournament
- Tournament-specific information (round, region)
- Seed information and upset indicators
- Performance differential metrics

This dataset is designed for analyzing historical tournament performance and identifying patterns in tournament outcomes.

### 3. Conference Summary Dataset (`conference_summary.parquet`)

An aggregated view of conference performance across seasons:

- Average team statistics by conference
- Tournament bid rates and success metrics
- Conference strength indicators
- Year-over-year conference performance

This dataset helps compare the strength of different conferences and track how they evolve over time.

### 4. Complete Season Dataset (`complete_season_data.parquet`)

A game-level dataset that combines regular season and tournament games with advanced metrics:

- Home/away team performance metrics
- Efficiency differentials between teams
- Home court advantage indicators
- Tournament/regular season designation

This dataset is ideal for game prediction modeling and analyzing factors that contribute to game outcomes.

## Usage

The merged datasets are automatically created during the data processing pipeline and stored in the `data/processed` directory. You can access them individually or generate them using the `process_all_transformations` function from `src/data/transformer.py`. 