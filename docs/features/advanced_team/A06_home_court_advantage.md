# A06: Home Court Advantage

## Overview

Home Court Advantage measures how much better a team performs at home compared to away games. This metric quantifies the benefit teams get from playing on their home court, which is a significant factor in predicting game outcomes.

## Formula

The formula for Home Court Advantage is:

$$\text{Home Court Advantage} = \text{Home Point Differential Per Game} - \text{Away Point Differential Per Game}$$

Where:
- **Home Point Differential Per Game** = Total points scored minus total points allowed in home games, divided by the number of home games
- **Away Point Differential Per Game** = Total points scored minus total points allowed in away games, divided by the number of away games

## Implementation Details

### Data Sources
- Primary: `team_box` data files
- Secondary: `schedules` data files (for neutral site identification)

### Key Parameters
- `min_home_games`: Minimum number of home games required for calculation (default: 5)
- `min_away_games`: Minimum number of away games required for calculation (default: 5)

### Algorithm

1. From the team_box data, identify home and away games using the `team_home_away` column
2. If schedules data is available, identify neutral site games and exclude them from the calculation
3. For each team in each season:
   - Calculate the total point differential for home games
   - Calculate the total point differential for away games
   - Divide each by the number of games to get per-game differentials
   - Subtract the away differential from the home differential
4. Filter out teams that don't have the minimum required number of home and away games

### Column Mapping

The implementation maps data source columns as follows:

| Required Column | Source | Purpose |
|-----------------|--------|---------|
| `team_id` | team_box | Uniquely identify each team |
| `team_name` | team_box | Team name for display purposes |
| `points` | team_box | Points scored by the team |
| `opponent_points` | team_box | Points allowed by the team |
| `season` | team_box | Basketball season year |
| `team_home_away` | team_box | Identifies if team is home or away |
| `game_id` | team_box | Used to join with schedules data |
| `neutral_site` | schedules | Identifies games played at neutral venues |

## Data Quality Considerations

### Common Issues

1. **Neutral Site Games**: The original data doesn't properly account for neutral site games in the team_box data, which can skew the home court advantage calculation. The implementation now incorporates the `neutral_site` flag from schedules data when available.

2. **Column Name Discrepancy**: The implementation previously looked for a `venue_type` column which doesn't exist in the raw data. Instead, it now uses the `team_home_away` column which contains the same information.

3. **Missing Values**: Teams with fewer than the minimum required home or away games will have no Home Court Advantage value. This is by design to ensure statistical validity of the metric.

### Interpretation

- A positive value indicates a team performs better at home than away
- A negative value (rare) indicates a team performs better on the road
- Values typically range from 2-10 points for most college basketball teams
- Elite teams often have higher home court advantages

## Usage Examples

```python
from src.features.advanced_team.A06_home_court_advantage import HomeCourtAdvantage

# Create the feature
feature = HomeCourtAdvantage(min_home_games=5, min_away_games=5)

# Calculate the feature (assuming data is loaded)
result = feature.calculate({
    "team_box": team_box_df,
    "schedules": schedules_df
})
```

## Related Features

- T01: Win Percentage (home/away splits)
- A01: Offensive Efficiency

## References

- [Home Court Advantage in College Basketball](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7182724/)
- [Statistical Analysis of NCAA Home Court Advantage](https://www.stats.com/articles/basketball/quantifying-home-court-advantage/) 