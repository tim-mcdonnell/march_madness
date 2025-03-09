# NCAA March Madness Data Cleaning

This document outlines the data cleaning procedures implemented for the NCAA March Madness prediction system.

## Overview

The data cleaning module (`src/data/cleaner.py`) provides functionality to clean and preprocess NCAA basketball data, building on the existing validation framework. The module implements various cleaning strategies for different types of data issues.

## Core Cleaning Operations

### 1. Missing Values Handling

The system supports multiple strategies for handling missing values:

- **drop**: Remove rows with missing values
- **mean**: Fill missing values with the column mean (numeric only)
- **median**: Fill missing values with the column median (numeric only)
- **mode**: Fill missing values with the column mode
- **zero**: Fill missing values with zero
- **custom**: Fill missing values with a specified value

Strategy selection is based on:
- Column importance (core vs. optional)
- Data type (numeric, categorical, etc.)
- Domain-specific considerations

### 2. Outlier Detection

Two methods are implemented for outlier detection:

1. **Z-score Method**
   - Identifies values beyond a specified number of standard deviations
   - Default threshold: 3.0 standard deviations
   - Suitable for normally distributed data

2. **IQR Method**
   - Uses interquartile range
   - Identifies values beyond 1.5 * IQR from Q1/Q3
   - More robust for non-normal distributions

### 3. Entity Resolution

The system includes comprehensive entity resolution capabilities specifically designed for NCAA basketball data:

#### Team Name Standardization
- NCAA-specific fuzzy matching of team name variants
- Built-in dictionary of common NCAA team abbreviations
- Pattern recognition for university/college naming conventions
- String similarity threshold of 0.85 with context-aware boosting
- Canonical name selection based on completeness and clarity
- Handles common variations like:
  - Full name vs. short name ("Duke Blue Devils" vs "Duke")
  - Abbreviations vs. full names ("UNC" vs "North Carolina")
  - With/without qualifiers ("University of Kentucky" vs "Kentucky")
  - Regional campuses ("UNC Chapel Hill" vs "North Carolina")

#### Team ID Resolution
- Maps variant team IDs to canonical IDs
- Based on standardized team names
- Preserves cross-season consistency
- Handles conference changes and team renames
- Prioritizes official NCAA identifiers when available

#### Player ID Resolution
- Enhanced cross-season player tracking
- Sophisticated handling of player transfers between teams
- Name variation detection and standardization
- Season-aware ID resolution for better continuity
- Maintains consistent IDs across a player's career
- Uses name, team, and season information for matching
- Special handling for:
  - Name variations (e.g., "Mike" vs "Michael")
  - Players transferring between schools
  - Players with the same name on different teams
  - ID changes across seasons for the same player

### 4. Date/Time Handling

(To be implemented)
- Timezone standardization
- Season boundary handling

## Usage

### Basic Cleaning

```python
from src.data.cleaner import DataCleaner

# Initialize cleaner
cleaner = DataCleaner(data_dir="path/to/data")

# Define cleaning strategy
missing_value_strategy = {
    "points": "mean",
    "player_id": "drop",
    "minutes": "zero"
}

# Clean data
cleaned_df = cleaner.clean_data(
    df=input_df,
    category="player_box",
    missing_value_strategy=missing_value_strategy,
    outlier_columns=["points", "rebounds", "assists"]
)
```

### Entity Resolution

```python
# Configure team name standardization
team_name_columns = ['team_name', 'opponent_team_name']

# Configure team ID standardization
team_id_columns = ['team_id', 'opponent_team_id']

# Configure player ID resolution
player_config = {
    'id_column': 'athlete_id',
    'name_column': 'athlete_name',
    'team_id_column': 'team_id'
}

# Clean data with entity resolution
cleaned_df = cleaner.clean_data(
    df=input_df,
    category="player_box",
    missing_value_strategy=missing_value_strategy,
    team_name_columns=team_name_columns,
    team_id_columns=team_id_columns,
    player_resolution_config=player_config
)

# Get cleaning report
report = cleaner.get_cleaning_report()
```

## Quality Metrics

The cleaning process tracks various metrics:

1. **Missing Value Metrics**
   - Count/percentage of missing values per column
   - Number of rows dropped/imputed
   - Imputation statistics

2. **Outlier Metrics**
   - Number of outliers detected
   - Outlier percentage per column
   - Method-specific statistics

3. **Entity Resolution Metrics**
   - Number of team name variants resolved
   - Number of team ID mappings created
   - Number of player ID conflicts resolved
   - Number of player transfers handled
   - Number of name variations standardized
   - Resolution confidence scores
   - Cross-season consistency metrics

## Implementation Status

- [x] Basic framework setup
- [x] Missing value handling
- [x] Outlier detection
- [x] Entity resolution
  - [x] Team name standardization
  - [x] Team ID resolution
  - [x] Player ID resolution
  - [x] NCAA-specific name patterns
  - [x] Cross-season consistency
  - [x] Transfer handling
- [ ] Date/time handling
- [ ] Advanced cleaning rules
- [ ] Performance optimization

## Next Steps

1. Implement date/time handling
2. Add sport-specific cleaning rules
3. Optimize for large datasets
4. Add more comprehensive testing
5. Implement caching for entity resolution mappings 