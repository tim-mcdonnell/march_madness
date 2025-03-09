# Three-Point Rate

## Overview
Three-Point Rate measures the percentage of a team's field goal attempts that come from beyond the three-point line. This metric provides insight into a team's shooting strategy and reliance on three-point shots.

## Description
Three-Point Rate is a simple but informative metric that reveals how much a team emphasizes three-point shooting in their offensive strategy. Teams with higher three-point rates tend to space the floor more and may have different strengths and vulnerabilities compared to teams that focus on inside scoring.

## Implementation
- **Feature ID**: S03
- **Category**: Shooting
- **Implementation**: [src/features/shooting/S03_three_point_rate.py](../../../src/features/shooting/S03_three_point_rate.py)

## Formula/Calculation
```
Three-Point Rate = 3PA / FGA
```

Where:
- 3PA = Three-point field goal attempts
- FGA = Total field goal attempts

## Data Requirements
This feature requires the following data:
- Team box score data with:
  - Team identifier
  - Field goal attempts
  - Three-point field goal attempts
  - Season information

## Implementation Notes
The implementation:
1. Groups data by team and season
2. Sums the field goal attempts and three-point field goal attempts
3. Divides the three-point attempts by total field goal attempts
4. Returns a DataFrame with team_id, team_name, team_location, season, and three_point_rate columns

```python
# Simplified calculation
three_point_rate = three_point_field_goals_attempted / field_goals_attempted
```

## Interpretation
- **Range**: Typically between 0.200 and 0.500
- **NCAA Division I Average**: Around 0.350-0.380
- **Low Value**: < 0.300 (Inside-focused team)
- **High Value**: > 0.450 (Three-point heavy team)

A higher three-point rate indicates a team that relies more heavily on three-point shooting as part of their offensive strategy. This doesn't necessarily indicate better performance, just a different style of play.

## Usage Examples

### Python API
```python
from src.features.shooting.S03_three_point_rate import ThreePointRate

# Create the feature
tpr_feature = ThreePointRate()

# Calculate for specific data
tpr_data = tpr_feature.calculate(team_box_data)
```

### Pipeline CLI
```bash
# Calculate all shooting features
python src/run_pipeline.py --stage feature --feature-categories shooting

# Calculate only Three-Point Rate
python src/run_pipeline.py --stage feature --feature-ids S03
```

## Visualization
Three-Point Rate is effectively visualized through:
- Bar charts comparing teams
- Histograms showing distribution across the league
- Scatter plots comparing Three-Point Rate with shooting efficiency metrics
- Time series plots showing trends over multiple seasons

## Related Features
- **S01: Effective Field Goal Percentage** - Efficiency of shooting, including three-pointers
- **S02: True Shooting Percentage** - Overall shooting efficiency including free throws
- **S06: Shooting Distribution** - Breakdown of scoring by shot type

## Version History
- v1.0 (2024-03-xx): Initial implementation 