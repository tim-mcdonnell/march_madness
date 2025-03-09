# NCAA March Madness Feature Documentation

This directory contains detailed documentation for each feature in the NCAA March Madness prediction system. Each feature has its own documentation file that follows a standardized format.

## Feature Organization

Features are organized by category in both code and documentation:

```
src/features/
├── core/                       # Core functionality
├── team_performance/          # Team Performance Metrics (T*)
├── shooting/                  # Shooting and Scoring Metrics (S*)
├── advanced_team/             # Advanced Team Metrics (A*)
├── possession/                # Possession Metrics (P*)
├── defensive/                 # Defensive Metrics (D*)
├── matchup/                   # Matchup-Specific Features (M*)
├── player_based/              # Player-Based Aggregated Metrics (Y*)
├── tournament/                # Tournament-Specific Metrics (U*)
├── data_engineering/          # Data Engineering Features (E*)
└── model_specific/            # Model-Specific Generated Features (G*)
```

Documentation follows the same structure:

```
docs/features/
├── team_performance/          # Team Performance Metrics
├── shooting/                  # Shooting and Scoring Metrics
└── ... (other categories)
```

## Feature Naming Convention

Features follow a consistent naming convention:

* **Source code**: `src/features/[category]/[ID]_[feature_name].py`
* **Documentation**: `docs/features/[category]/[ID]_[feature_name].md`

For example:
* Source: `src/features/shooting/S01_effective_field_goal_percentage.py`
* Documentation: `docs/features/shooting/S01_effective_field_goal_percentage.md`

## Feature Structure

Each feature follows these implementation principles:

1. **Inherits from BaseFeature**: All features inherit from the `BaseFeature` class
2. **Required attributes**: `id`, `name`, `category`, `description`
3. **Required methods**: `calculate` (additional optional methods include `get_required_data`, `validate_result`, etc.)

Example:

```python
class EffectiveFieldGoalPercentage(BaseFeature):
    """Feature class documentation."""
    
    id = "S01"  # Unique identifier
    name = "Effective Field Goal Percentage"  # Human-readable name
    category = "shooting"  # Category (matches directory name)
    description = "Field goal percentage adjusted for three-pointers"  # Short description
    
    def calculate(self, data):
        """Calculate the feature from input data."""
        # Implementation
        return result
```

## Data Organization

Features are calculated from processed data (`data/processed/`) and stored in category-specific files:

```
data/features/
├── team_performance_metrics.parquet    # All team performance metrics
├── shooting_metrics.parquet           # All shooting metrics
├── ... (other category files)
└── combined/
    └── full_feature_set.parquet       # Combined features file
```

## Using Features

You can use the feature system through the pipeline or directly:

### Via Pipeline CLI

```bash
# Calculate all features
python run_pipeline.py --stages features

# Calculate specific categories
python run_pipeline.py --stages features --feature-categories shooting team_performance

# Calculate specific features
python run_pipeline.py --stages features --feature-ids S01 T01
```

### Via Python API

```python
from src.features import calculate_features, initialize_features

# Initialize feature discovery
initialize_features()

# Calculate all features
results = calculate_features()

# Calculate specific categories
results = calculate_features(category="shooting")

# Calculate specific features
results = calculate_features(feature_ids=["S01", "T01"])
```

## Available Features

For a complete list of features and their implementation status, see [FEATURES.md](../../FEATURES.md).

## Feature Migration

For a summary of the feature migration from the old system to the new feature framework, see [Migration Summary](migration_summary.md).

## Feature Documentation Format

Each feature documentation file follows a standardized format:

1. **Overview**: Category, complexity, status
2. **Description**: Detailed explanation of what the feature measures
3. **Implementation**: Link to implementation file
4. **Formula/Calculation**: Mathematical formula and code explanation
5. **Data Requirements**: Input data and required columns
6. **Implementation Notes**: Considerations, edge cases, optimization
7. **Interpretation**: Typical range, benchmark values, context
8. **Usage Examples**: Code examples showing how to use the feature
9. **Visualization**: Recommended visualization approaches
10. **Related Features**: Connections to other features
11. **Version History**: Changes to the implementation 