# True Shooting Percentage (TS%)

## Overview
True Shooting Percentage (TS%) is a shooting efficiency metric that accounts for field goals, three-pointers, and free throws. This metric provides a comprehensive measure of a team's shooting efficiency by including all scoring methods.

## Description
True Shooting Percentage improves upon Effective Field Goal Percentage by adding free throws to the equation. It weights all scoring attempts appropriately to measure overall shooting efficiency. The formula accounts for the fact that free throws are worth 1 point (compared to 2 or 3 for field goals) and that most free throws come in pairs.

## Implementation
- **Feature ID**: S02
- **Category**: Shooting
- **Implementation**: [src/features/shooting/S02_true_shooting_percentage.py](../../../src/features/shooting/S02_true_shooting_percentage.py)

## Formula/Calculation
```
TS% = Points / (2 * (FGA + 0.44 * FTA))
```

Where:
- Points = Total points scored
- FGA = Field goal attempts
- FTA = Free throw attempts
- 0.44 = An approximation factor that accounts for technical free throws and and-ones

## Data Requirements
This feature requires the following data:
- Team box score data with:
  - Team identifier
  - Points scored
  - Field goal attempts
  - Free throw attempts
  - Season information

## Implementation Notes
The implementation:
1. Groups data by team and season
2. Sums the points, field goal attempts, and free throw attempts
3. Applies the TS% formula to calculate the efficiency
4. Returns a DataFrame with team_id, team_name, team_location, season, and true_shooting_percentage columns

```python
# Simplified calculation
true_shooting_percentage = points / (2 * (field_goals_attempted + 0.44 * free_throws_attempted))
```

## Interpretation
- **Range**: Typically between 0.400 and 0.650
- **NCAA Division I Average**: Around 0.530-0.540
- **Good Value**: > 0.570
- **Great Value**: > 0.600
- **Elite Value**: > 0.620

A higher true shooting percentage indicates more efficient scoring, accounting for all scoring methods.

## Usage Examples

### Python API
```python
from src.features.shooting.S02_true_shooting_percentage import TrueShootingPercentage

# Create the feature
ts_feature = TrueShootingPercentage()

# Calculate for specific data
ts_data = ts_feature.calculate(team_box_data)
```

### Pipeline CLI
```bash
# Calculate all shooting features
python src/run_pipeline.py --stage feature --feature-categories shooting

# Calculate only True Shooting Percentage
python src/run_pipeline.py --stage feature --feature-ids S02
```

## Visualization
True Shooting Percentage is effectively visualized through:
- Bar charts comparing teams
- Histograms showing distribution across the league
- Scatter plots comparing TS% with other efficiency metrics like eFG%
- Time series plots showing trends over a season

## Related Features
- **S01: Effective Field Goal Percentage** - Similar metric but excludes free throws
- **S04: Free Throw Rate** - Measures how often a team gets to the free throw line
- **A01: Offensive Efficiency** - Points per 100 possessions (uses TS% indirectly)

## Version History
- v1.0 (2024-03-xx): Initial implementation 