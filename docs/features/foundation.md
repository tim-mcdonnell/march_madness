# Foundation Features

## Overview

Foundation features are the base set of performance metrics that provide essential information about team performance. These features are derived from team box scores and aggregated at the season level. They serve as the building blocks for more complex features and models.

## Feature Categories

The Foundation feature set includes:

1. **Simple Shooting Metrics**
2. **Basic Possession Metrics**
3. **Win Percentage Breakdowns**
4. **Recent Form and Consistency Metrics**
5. **Home Court Advantage Rating**

## Detailed Feature Description

### Shooting Metrics

| Feature | Description | Formula | Meaning |
|---------|-------------|---------|---------|
| `efg_pct` | Effective Field Goal Percentage | (FG + 0.5 * 3PM) / FGA | Adjusts field goal percentage to account for three-pointers being worth more |
| `ts_pct` | True Shooting Percentage | PTS / (2 * (FGA + 0.44 * FTA)) | Measures shooting efficiency including all shot types |
| `three_point_rate` | Three-Point Rate | 3PA / FGA | Percentage of field goal attempts from three-point range |
| `ft_rate` | Free Throw Rate | FTA / FGA | Free throw attempts relative to field goal attempts |

### Possession Metrics

| Feature | Description | Formula | Meaning |
|---------|-------------|---------|---------|
| `orb_pct` | Offensive Rebound Percentage | ORB / (ORB + Opp DRB) | Team's effectiveness at getting offensive rebounds |
| `drb_pct` | Defensive Rebound Percentage | DRB / (DRB + Opp ORB) | Team's effectiveness at getting defensive rebounds |
| `trb_pct` | Total Rebound Percentage | TRB / (TRB + Opp TRB) | Team's overall rebounding effectiveness |
| `ast_rate` | Assist Rate | AST / FGM | Percentage of made field goals that are assisted |
| `tov_pct` | Turnover Percentage | TOV / (FGA + 0.44 * FTA + TOV) | Turnovers per 100 possessions |
| `ast_to_tov_ratio` | Assist-to-Turnover Ratio | AST / TOV | Ratio of assists to turnovers |

### Win Percentage Breakdowns

| Feature | Description | Formula | Meaning |
|---------|-------------|---------|---------|
| `home_win_pct_detailed` | Home Win Percentage | Wins_Home / Games_Home | Winning percentage in home games |
| `away_win_pct_detailed` | Away Win Percentage | Wins_Away / Games_Away | Winning percentage in away games |
| `neutral_win_pct` | Neutral Win Percentage | Wins_Neutral / Games_Neutral | Winning percentage in neutral site games |
| `home_games_played` | Home Games Played | Count | Number of home games played |
| `away_games_played` | Away Games Played | Count | Number of away games played |
| `neutral_games_played` | Neutral Games Played | Count | Number of neutral site games played |

### Form and Consistency Metrics

| Feature | Description | Formula | Meaning |
|---------|-------------|---------|---------|
| `point_diff_stddev` | Point Differential Standard Deviation | Std(Point_Diff) | Consistency of point differential across games |
| `scoring_stddev` | Scoring Standard Deviation | Std(Points) | Consistency of team scoring across games |
| `recent_point_diff` | Recent Point Differential | Weighted Avg(Point_Diff) | Exponentially weighted average of recent point differentials |
| `recent_win_pct` | Recent Win Percentage | Weighted Avg(Win) | Exponentially weighted average of recent wins |

### Home Court Advantage Metrics

| Feature | Description | Formula | Meaning |
|---------|-------------|---------|---------|
| `home_court_advantage` | Home Court Advantage | Margin_Home - Margin_Away | Difference in scoring margin between home and away games |
| `home_win_boost` | Home Win Boost | Win%_Home - Win%_Away | Difference in win percentage between home and away games |

## Using the Features

The foundation features can be used for various purposes:

1. **Team Performance Evaluation**: Assess a team's strengths and weaknesses
2. **Matchup Analysis**: Compare teams across key performance metrics
3. **Trend Analysis**: Analyze how a team's performance evolves over a season
4. **Model Input**: Serve as input features for predictive models

## Implementation Details

These features are implemented in the `FoundationFeatureBuilder` class in `src/features/builders/foundation.py`. To generate these features, run:

```bash
python -m src.features.generate --feature-set foundation --output-dir data/features --output-filename team_performance.parquet
```

This will create a `team_performance.parquet` file in the `data/features` directory containing all the foundation features joined with the base team season statistics.

## Feature Engineering Approach

The foundation features follow these key principles:

1. **Aggregation**: Game-level statistics are aggregated to the season level
2. **Normalization**: Raw counts are converted to rates to account for pace differences
3. **Context**: Performance metrics are contextualized (home/away, opponent strength)
4. **Recency**: Recent performance is given more weight in certain metrics

## Data Quality Considerations

When using these features, be aware of:

1. **Missing Values**: Some features may have missing values for teams with incomplete data
2. **Small Sample Sizes**: Early season metrics may be based on few games
3. **Outliers**: Extreme performances can skew aggregated metrics

## Future Enhancements

Future enhancements to the foundation features could include:

1. **Opponent Strength Adjustment**: Adjust metrics based on opponent quality
2. **Conference-Specific Analysis**: Add conference-level aggregations
3. **Time Series Features**: More sophisticated temporal features
4. **Game Importance Weighting**: Weight games by importance or stakes 