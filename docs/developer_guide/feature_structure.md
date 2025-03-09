# Feature Structure and Requirements

This document outlines the structure, organization, and requirements for implementing features in the NCAA March Madness Predictor.

## Feature Organization

Features are organized into categories based on the basketball metrics they represent:

- **Team Performance (`team_performance/`)**: Basic team performance metrics like win percentage and point differential
- **Shooting (`shooting/`)**: Shooting efficiency metrics like effective field goal percentage and true shooting percentage
- **Possession (`possession/`)**: Possession-based metrics like turnover rate and offensive rebound percentage
- **Advanced Team (`advanced_team/`)**: Advanced team metrics like home court advantage and strength of schedule

Each feature is implemented as a separate Python module within its category directory, following a consistent naming pattern:

```
src/features/
├── team_performance/
│   ├── T01_win_percentage.py
│   ├── T02_point_differential.py
│   └── ...
├── shooting/
│   ├── S01_effective_field_goal_percentage.py
│   ├── S02_true_shooting_percentage.py
│   └── ...
├── possession/
│   ├── P01_turnover_rate.py
│   ├── P02_offensive_rebound_percentage.py
│   └── ...
└── advanced_team/
    ├── A01_home_court_advantage.py
    ├── A02_strength_of_schedule.py
    └── ...
```

## Feature Implementation Requirements

Each feature must be implemented as a class that inherits from the `BaseFeature` class and follows these requirements:

### Required Attributes

- `id`: A unique identifier for the feature (e.g., "T01", "S02")
- `name`: A human-readable name for the feature
- `category`: The category the feature belongs to (e.g., "team_performance", "shooting")
- `description`: A detailed description of what the feature measures and how it's calculated

### Required Methods

- `get_required_data()`: Returns a dictionary of required data sources
- `calculate(data_dict)`: Performs the feature calculation and returns a DataFrame with the results

### Example Feature Implementation

```python
from src.features.base import BaseFeature
import polars as pl

class WinPercentage(BaseFeature):
    """Feature that calculates win percentage for each team."""
    
    def __init__(self):
        """Initialize the feature."""
        self.id = "T01"
        self.name = "Win Percentage"
        self.category = "team_performance"
        self.description = "Percentage of games won by a team."
        
    def get_required_data(self):
        """Return the required data sources."""
        return {"team_box": "Team box score data"}
        
    def calculate(self, data_dict):
        """Calculate the win percentage for each team.
        
        Args:
            data_dict: Dictionary containing the required data sources.
                
        Returns:
            DataFrame with team_id, team_name, team_location, season, and win_percentage columns.
        """
        # Implementation details...
```

## Feature Output Requirements

All features must return a DataFrame with the following columns:

- `team_id`: Unique identifier for the team
- `team_name`: Name of the team
- `team_location`: Location of the team
- `season`: Season the feature is calculated for
- Feature value column(s): The calculated feature value(s) with a descriptive name

## Data Validation Requirements

Features must validate their input data and handle edge cases appropriately:

1. **Required Columns**: Check that all required columns are present in the input data
2. **Missing Values**: Handle missing values appropriately (e.g., filter out, impute, or raise error)
3. **Zero Division**: Handle potential division by zero cases
4. **Edge Cases**: Consider and handle edge cases specific to the feature

## Testing Requirements

Each feature must have corresponding tests in the `tests/features/` directory that verify:

1. **Instantiation**: The feature can be instantiated correctly
2. **Required Data**: The feature correctly reports its required data sources
3. **Calculation**: The feature calculates correctly with mock data
4. **Calculation Logic**: The calculation logic is correct using simplified test cases
5. **Error Handling**: The feature handles missing required columns and other error cases
6. **Edge Cases**: The feature handles edge cases correctly (e.g., zero division)

Tests should follow the same directory structure as the features:

```
tests/features/
├── test_utils.py
├── conftest.py
├── team_performance/
│   ├── test_T01_win_percentage.py
│   ├── test_T02_point_differential.py
│   └── ...
├── shooting/
│   ├── test_S01_effective_field_goal_percentage.py
│   ├── test_S02_true_shooting_percentage.py
│   └── ...
└── ...
```

## Feature Quality Standards

All features must meet these quality standards:

1. **Variance**: Features should have sufficient variance (not all identical values)
2. **Missing Values**: Features should have minimal missing values (typically < 10%)
3. **Range**: Feature values should be within a reasonable range for the metric
4. **Documentation**: Features should be well-documented with clear descriptions
5. **Performance**: Features should be implemented efficiently

## Adding New Features

To add a new feature:

1. Identify the appropriate category for the feature
2. Create a new module in the category directory with a unique ID
3. Implement the feature class inheriting from `BaseFeature`
4. Implement the required attributes and methods
5. Create corresponding tests in the `tests/features/` directory
6. Update the feature documentation in `docs/features/`
7. Add the feature to the feature registry in `src/features/__init__.py`

## Feature Documentation

Each feature should be documented in the `docs/features/` directory with:

1. **Purpose**: What the feature measures and why it's important
2. **Formula**: The mathematical formula used to calculate the feature
3. **Interpretation**: How to interpret the feature values
4. **Limitations**: Any limitations or caveats to be aware of
5. **Example**: An example of the feature in use 