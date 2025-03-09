# Offensive Efficiency

## Overview
Offensive Efficiency (also called Offensive Rating) measures how many points a team scores per 100 possessions. It's a tempo-free measure of offensive performance that allows for fair comparison between teams that play at different paces.

## Description
Offensive Efficiency normalizes scoring by possessions rather than by game, providing a more accurate picture of offensive effectiveness. Unlike raw scoring averages, this metric isn't biased by game pace - teams that play at a faster pace naturally have more scoring opportunities, but aren't necessarily more efficient.

## Implementation
- **Feature ID**: A01
- **Category**: Advanced Team
- **Implementation**: [src/features/advanced_team/A01_offensive_efficiency.py](../../../src/features/advanced_team/A01_offensive_efficiency.py)

## Formula/Calculation
```
Offensive Efficiency = (Points / Possessions) * 100
```

Where:
- Points = Points scored per game
- Possessions = Estimated possessions per game (from P01 feature)

## Data Requirements
This feature requires the following data:
- Team box score data with:
  - Team identifier
  - Points scored
  - Season information
- Possessions data (calculated by the P01 feature)

## Implementation Notes
The implementation:
1. Calculates points per game by team and season
2. Uses the Possessions feature (P01) to get possessions per game
3. Divides points per game by possessions per game and multiplies by 100
4. Returns a DataFrame with team_id, team_name, team_location, season, and offensive_efficiency columns

```python
# Simplified calculation
offensive_efficiency = (points_per_game / possessions) * 100
```

## Dependencies
This feature depends on:
- **P01: Possessions** - Required to normalize points by possessions

## Interpretation
- **Range**: Typically between 85 and 125
- **NCAA Division I Average**: Around 100-105
- **Below Average**: < 95
- **Good Value**: > 110
- **Elite Value**: > 115

A higher offensive efficiency indicates a more effective offense that scores more points per possession. This is generally considered a better predictor of offensive strength than raw scoring averages.

## Usage Examples

### Python API
```python
from src.features.advanced_team.A01_offensive_efficiency import OffensiveEfficiency
from src.features.possession.P01_possessions import Possessions

# Create the dependencies
possessions_feature = Possessions()

# Create the feature with dependencies
oe_feature = OffensiveEfficiency(possessions_feature=possessions_feature)

# Calculate for specific data
oe_data = oe_feature.calculate(team_box_data)
```

### Pipeline CLI
```bash
# Calculate all advanced team features
python src/run_pipeline.py --stage feature --feature-categories advanced_team

# Calculate only Offensive Efficiency
python src/run_pipeline.py --stage feature --feature-ids A01
```

## Visualization
Offensive Efficiency is effectively visualized through:
- Bar charts comparing teams
- Histograms showing distribution across the league
- Scatter plots comparing Offensive Efficiency with Defensive Efficiency
- Time series plots showing trends over a season

## Related Features
- **P01: Possessions** - Estimated possessions per game (dependency)
- **T03: Team Offensive Efficiency Rating** - Adjusted version that accounts for opponent strength
- **T04: Team Defensive Efficiency Rating** - Points allowed per 100 possessions
- **T05: Relative Rating** - Combined offensive and defensive efficiency

## Version History
- v1.0 (2024-03-xx): Initial implementation 