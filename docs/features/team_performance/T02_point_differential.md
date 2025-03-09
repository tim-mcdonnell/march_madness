# Point Differential

## Overview
Point Differential measures the average margin between a team's score and their opponent's score across all games. This metric provides a more nuanced view of team performance than win-loss record alone.

## Description
Point Differential (also called scoring margin) is a fundamental metric that captures not just whether a team wins or loses, but by how much. Teams with high positive point differentials are consistently outscoring their opponents, which is often a better predictor of future success than win percentage alone.

## Implementation
- **Feature ID**: T02
- **Category**: Team Performance
- **Implementation**: [src/features/team_performance/T02_point_differential.py](../../../src/features/team_performance/T02_point_differential.py)

## Formula/Calculation
```
Point Differential = (Total Points Scored - Total Points Allowed) / Games Played
```

Where:
- Total Points Scored = Sum of points scored by the team across all games
- Total Points Allowed = Sum of points scored by opponents across all games
- Games Played = Number of games played

## Data Requirements
This feature requires the following data:
- Team box score data with:
  - Team identifier
  - Points scored
  - Opponent points
  - Season information

## Implementation Notes
The implementation:
1. Groups data by team and season
2. Calculates total points scored and allowed
3. Computes the difference and divides by games played
4. Returns a DataFrame with team_id, team_name, team_location, season, and point_differential columns

```python
# Simplified calculation
point_differential = (total_points_for - total_points_against) / games_played
```

## Interpretation
- **Range**: Typically between -20.0 and +20.0
- **NCAA Division I Average**: Around 0.0 (zero-sum across all teams)
- **Good Value**: > +5.0
- **Great Value**: > +10.0
- **Elite Value**: > +15.0

A positive point differential indicates a team that outscores its opponents on average, while a negative value indicates a team that is outscored. The magnitude provides insight into the degree of dominance or struggle.

## Usage Examples

### Python API
```python
from src.features.team_performance.T02_point_differential import PointDifferential

# Create the feature
pd_feature = PointDifferential()

# Calculate for specific data
pd_data = pd_feature.calculate(team_box_data)
```

### Pipeline CLI
```bash
# Calculate all team performance features
python src/run_pipeline.py --stage feature --feature-categories team_performance

# Calculate only Point Differential
python src/run_pipeline.py --stage feature --feature-ids T02
```

## Visualization
Point Differential is effectively visualized through:
- Bar charts comparing teams
- Histograms showing distribution across the league
- Scatter plots comparing Point Differential with Win Percentage
- Time series plots showing trends over a season

## Related Features
- **T01: Win Percentage** - Proportion of games won
- **T03: Team Offensive Efficiency Rating** - Points scored per 100 possessions
- **T04: Team Defensive Efficiency Rating** - Points allowed per 100 possessions
- **T05: Relative Rating** - Combined offensive and defensive efficiency

## Version History
- v1.0 (2024-03-xx): Initial implementation 