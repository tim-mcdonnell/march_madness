# March Madness Predictor Feature Overview

This document outlines the features for our prediction model, inspired by Evan Miyakowa's approach and adapted to our available data. Each feature will be built using our processed data files and will serve as input to our neural network model.

## Feature System Structure

Features are now implemented following a standardized approach:

1. Each feature is implemented as a class that inherits from `BaseFeature`
2. Features are organized by category in separate directories
3. Features follow the naming convention `[ID]_[feature_name].py`
4. Features are automatically discovered and loaded at runtime

For implementation details, see:
- Feature implementation template: `src/features/core/base.py`
- Feature Registry: `src/features/core/registry.py`
- Feature Loader: `src/features/core/loader.py`
- Feature Data Manager: `src/features/core/data_manager.py`

For usage information, see the [Features Documentation](../../features/index.md).

## Feature Reference List

The complexity score (1-5) indicates the anticipated implementation difficulty:
- **1**: Simple calculation from direct data
- **2**: Moderate calculation requiring some data manipulation
- **3**: Complex calculation requiring significant data processing
- **4**: Very complex calculation requiring advanced methods
- **5**: Extremely complex requiring sophisticated algorithms

### Team Performance Metrics

- [ ] **Team Offensive Efficiency Rating (O-Rate)** - [3] Points scored per 100 possessions, adjusted for opponent strength
- [ ] **Team Defensive Efficiency Rating (D-Rate)** - [3] Points allowed per 100 possessions, adjusted for opponent strength
- [ ] **Relative Rating** - [3] Combined O-Rate and D-Rate (net efficiency)
- [ ] **True Tempo** - [2] Average possessions per 40 minutes, adjusted for opponents
- [ ] **Opponent Strength Adjustment** - [4] How a team performs against strong vs. weak competition (playing up/down to competition)
- [ ] **Game Pace Adjustment** - [3] How a team performs in fast vs. slow-paced games
- [x] **Recent Form** - [2] Performance trend over the last N games (weighted recency) (Implemented: T09)
- [x] **Consistency Rating** - [2] Variance in game-to-game performance (Implemented: T10)
- [x] **Win Percentage** - [1] Overall, home, away, and neutral site (Implemented: T01)
- [x] **Point Differential** - [1] Average margin of victory/defeat (Implemented: T02)
- [ ] **Strength of Schedule** - [3] Overall schedule difficulty rating

### Advanced Team Metrics

- [x] **Offensive Efficiency** - [2] Points scored per 100 possessions (Implemented: A01)
- [ ] **Kill Shots Per Game** - [4] Number of 10-0 or better scoring runs per game
- [ ] **Kill Shots Allowed Per Game** - [4] Number of opponent 10-0 or better scoring runs per game
- [ ] **Kill Shots Margin** - [4] Difference between team's kill shots and opponents'
- [ ] **Clutch Performance** - [4] Performance in close games (last 5 minutes, margin ≤ 5 points)
- [x] **Home Court Advantage** - [2] Rating of how much better a team performs at home (Implemented: A06)
- [ ] **Tournament Experience** - [3] Previous NCAA tournament experience metric

### Shooting and Scoring Metrics

- [x] **Effective Field Goal Percentage (eFG%)** - [1] Field goal percentage adjusted for three-pointers (Implemented: S01)
- [x] **True Shooting Percentage (TS%)** - [1] Shooting efficiency including free throws (Implemented: S02)
- [x] **Three-Point Rate** - [1] Percentage of field goal attempts from three-point range (Implemented: S03)
- [x] **Free Throw Rate** - [1] Free throw attempts relative to field goal attempts (Implemented: S04)
- [ ] **Points Per Possession** - [2] Raw points scored per possession
- [ ] **Shooting Distribution** - [2] Breakdown of scoring by two-pointers, three-pointers, and free throws
- [ ] **Fast Break Points Per Game** - [1] Points scored in transition

### Possession and Ball Control Metrics

- [x] **Possessions** - [2] Estimated number of possessions per game (Implemented: P01)
- [x] **Offensive Rebound Percentage** - [2] Percentage of offensive rebounds captured (Implemented: P02)
- [x] **Defensive Rebound Percentage** - [2] Percentage of defensive rebounds captured (Implemented: P03)
- [x] **Total Rebound Percentage** - [2] Overall rebounding efficiency (Implemented: P04)
- [x] **Turnover Percentage** - [2] Turnovers per 100 possessions (Implemented: P05)
- [ ] **Ball Control Rating** - [2] Combined metric of assists, steals, and turnovers
- [x] **Assist-to-Turnover Ratio** - [1] Team's ratio of assists to turnovers (Implemented: P07)
- [x] **Assist Rate** - [2] Percentage of field goals that are assisted (Implemented: P08)
- [ ] **Steal Rate** - [2] Steals per opponent possession

### Defensive Metrics

- [ ] **Block Percentage** - [2] Percentage of opponent two-point attempts blocked
- [ ] **Opponent eFG%** - [1] Opponent's effective field goal percentage
- [ ] **Opponent Turnover Rate** - [2] Turnovers forced per 100 opponent possessions
- [ ] **Points Allowed by Play Type** - [4] Breakdown of points allowed by play type
- [ ] **Opponent Three-Point Rate** - [1] Percentage of opponent shots from three-point range
- [ ] **Perimeter Defense Rating** - [3] Effectiveness at defending three-point shots

### Matchup-Specific Features

- [ ] **Head-to-Head History** - [2] Historical performance in direct matchups
- [ ] **Style Matchup Rating** - [4] How well team style matches up against opponent style
- [ ] **Pace Control** - [3] Which team is likely to control the game's pace
- [ ] **Tournament Seeding** - [3] Historical performance based on seed matchups
- [ ] **Home/Away/Neutral Adjustment** - [2] Venue-specific performance adjustment

### Player-Based Aggregated Metrics

- [ ] **Star Player Impact** - [3] Influence of top players on team success
- [ ] **Depth Rating** - [3] Contribution from bench players
- [ ] **Player Efficiency Distribution** - [3] How evenly distributed efficiency is among starters
- [ ] **Player Consistency** - [3] Consistency of individual player performances
- [ ] **Lineup Efficiency** - [4] Performance of most common lineups

### Tournament-Specific Metrics

- [ ] **Round-by-Round Adjustment** - [3] How teams perform in specific tournament rounds
- [ ] **Days of Rest** - [2] Impact of rest days between games
- [ ] **Tournament-vs-Regular Season** - [3] Performance difference in tournament games
- [ ] **Under-Seeded Rating** - [3] Metric identifying teams performing above their seed line

### Data Engineering Features

- [x] **Exponentially Weighted Metrics** - [2] Recency-weighted versions of key statistics
- [ ] **Rolling Averages** - [2] N-game rolling averages of performance metrics
- [ ] **Season Segments** - [2] Performance in different parts of season (early, mid, late)
- [x] **Variance Features** - [2] Standard deviation of key performance metrics
- [ ] **Interaction Terms** - [3] Products of relevant features that may have combined effects
- [ ] **Game Importance Weight** - [3] Weighting games by importance/stakes
- [ ] **Outlier Management** - [2] Handling of outlier performances

### Model-Specific Generated Features

- [ ] **Principal Component Analysis** - [3] Dimension reduction of correlated features
- [ ] **Cluster Assignment** - [3] Team style/archetype classification
- [ ] **Win Probability Model** - [4] Pre-game win probability using multiple factors
- [ ] **Simulation-Based Features** - [4] Features derived from game simulations
- [ ] **Conference Tournament Impact** - [3] Effect of conference tournament performance 

## Implementation Phases

Our implementation will proceed in phases, focusing on features in order of complexity and dependency:

### Phase 1: Foundation Features ✅

**Focus**: Simple metrics from direct data (Complexity 1-2)
* Win percentages, shooting metrics, rebound rates

### Phase 2: Efficiency Metrics 🚧

**Focus**: Advanced efficiency metrics that build on basic stats (Complexity 2-3)
* Offensive/defensive efficiency, tempo metrics, schedule strength

### Phase 3: Advanced Metrics 📅

**Focus**: Complex metrics requiring multiple data sources (Complexity 3-4)
* Player impact metrics, sequence-based metrics, style analysis

### Phase 4: Tournament-Specific and Model-Generated Features 📅

**Focus**: Specialized metrics for tournament prediction (Complexity 3-5)
* Tournament adaptations, simulation features, optimized prediction features

## Implementing a New Feature

To add a new feature:

1. Create a file in the appropriate category directory:
```
src/features/[category]/[ID]_[feature_name].py
```

2. Implement a class that inherits from BaseFeature:
```python
from src.features.core.base import BaseFeature

class MyFeature(BaseFeature):
    id = "X01"
    name = "My Feature"
    category = "my_category"
    description = "Description of what my feature does"
    
    def calculate(self, data):
        # Calculation implementation
        return result_df
```

3. Create documentation:
```
docs/features/[category]/[ID]_[feature_name].md
```

4. Update the FEATURES.md registry with implementation status

For full details, see the [Feature Documentation](../../features/index.md). 