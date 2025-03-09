# Possessions

## Overview
The Possessions feature estimates the number of possessions a team has during a game. This is a fundamental metric for calculating possession-based efficiency statistics and understanding game pace.

## Description
Possessions is a core metric that approximates how many times a team had control of the ball during a game. Since possessions aren't directly tracked in box scores, they must be estimated using a formula that accounts for field goal attempts, free throw attempts, offensive rebounds, and turnovers. This metric is essential for normalizing team statistics across different game paces.

## Implementation
- **Feature ID**: P01
- **Category**: Possession
- **Implementation**: [src/features/possession/P01_possessions.py](../../../src/features/possession/P01_possessions.py)

## Formula/Calculation
```
Possessions = FGA + 0.475*FTA - ORB + TO
```

Where:
- FGA = Field goal attempts
- FTA = Free throw attempts
- ORB = Offensive rebounds
- TO = Turnovers
- 0.475 = Coefficient that accounts for and-one situations and technical free throws

## Data Requirements
This feature requires the following data:
- Team box score data with:
  - Team identifier
  - Field goal attempts
  - Free throw attempts
  - Offensive rebounds
  - Turnovers
  - Season information

## Implementation Notes
The implementation:
1. Groups data by team and season
2. Sums the field goal attempts, free throw attempts, offensive rebounds, and turnovers
3. Applies the possessions formula
4. Divides by games played to get possessions per game
5. Returns a DataFrame with team_id, team_name, team_location, season, and possessions columns

```python
# Simplified calculation
possessions = (fga + 0.475 * fta - orb + to) / games_played
```

## Interpretation
- **Range**: Typically between 60 and 80 possessions per game
- **NCAA Division I Average**: Around 68-70 possessions per game
- **Slow Pace**: < 65 possessions per game
- **Fast Pace**: > 75 possessions per game

A higher number of possessions indicates a faster-paced game, while a lower number indicates a slower, more deliberate style of play. This metric is primarily descriptive rather than evaluative - neither fast nor slow pace is inherently better.

## Usage Examples

### Python API
```python
from src.features.possession.P01_possessions import Possessions

# Create the feature
poss_feature = Possessions()

# Calculate for specific data
poss_data = poss_feature.calculate(team_box_data)
```

### Pipeline CLI
```bash
# Calculate all possession features
python src/run_pipeline.py --stage feature --feature-categories possession

# Calculate only Possessions
python src/run_pipeline.py --stage feature --feature-ids P01
```

## Visualization
Possessions is effectively visualized through:
- Bar charts comparing teams
- Histograms showing distribution across the league
- Scatter plots comparing Possessions with efficiency metrics
- Time series plots showing trends over multiple seasons

## Related Features
- **A01: Offensive Efficiency** - Points scored per 100 possessions (uses Possessions)
- **T06: True Tempo** - Possessions adjusted for opponent pace
- **P04: Turnover Percentage** - Turnovers per 100 possessions (uses Possessions)
- **P05: Ball Control Rating** - Combined metric of ball control (uses Possessions)

## Version History
- v1.0 (2024-03-xx): Initial implementation 