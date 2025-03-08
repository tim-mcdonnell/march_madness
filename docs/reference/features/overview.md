# March Madness Predictor Feature Overview

This document outlines the features we need to build for our prediction model, inspired by Evan Miyakowa's approach and adapted to our available data. Each feature will be built using our processed data files and will serve as input to our neural network model.

The complexity score (1-5) indicates the anticipated implementation difficulty:
- **1**: Simple calculation from direct data
- **2**: Moderate calculation requiring some data manipulation
- **3**: Complex calculation requiring significant data processing
- **4**: Very complex calculation requiring advanced methods
- **5**: Extremely complex requiring sophisticated algorithms

## Team Performance Metrics

- [ ] **Team Offensive Efficiency Rating (O-Rate)** - [3] Points scored per 100 possessions, adjusted for opponent strength
- [ ] **Team Defensive Efficiency Rating (D-Rate)** - [3] Points allowed per 100 possessions, adjusted for opponent strength
- [ ] **Relative Rating** - [3] Combined O-Rate and D-Rate (net efficiency)
- [ ] **True Tempo** - [2] Average possessions per 40 minutes, adjusted for opponents
- [ ] **Opponent Strength Adjustment** - [4] How a team performs against strong vs. weak competition (playing up/down to competition)
- [ ] **Game Pace Adjustment** - [3] How a team performs in fast vs. slow-paced games
- [x] **Recent Form** - [2] Performance trend over the last N games (weighted recency)
- [x] **Consistency Rating** - [2] Variance in game-to-game performance
- [x] **Win Percentage** - [1] Overall, home, away, and neutral site
- [x] **Point Differential** - [1] Average margin of victory/defeat
- [ ] **Strength of Schedule** - [3] Overall schedule difficulty rating

## Advanced Team Metrics

- [ ] **Kill Shots Per Game** - [4] Number of 10-0 or better scoring runs per game
- [ ] **Kill Shots Allowed Per Game** - [4] Number of opponent 10-0 or better scoring runs per game
- [ ] **Kill Shots Margin** - [4] Difference between team's kill shots and opponents'
- [ ] **Clutch Performance** - [4] Performance in close games (last 5 minutes, margin ≤ 5 points)
- [x] **Home Court Advantage** - [2] Rating of how much better a team performs at home
- [ ] **Tournament Experience** - [3] Previous NCAA tournament experience metric

## Shooting and Scoring Metrics

- [x] **Effective Field Goal Percentage (eFG%)** - [1] Field goal percentage adjusted for three-pointers
- [x] **True Shooting Percentage (TS%)** - [1] Shooting efficiency including free throws
- [x] **Three-Point Rate** - [1] Percentage of field goal attempts from three-point range
- [x] **Free Throw Rate** - [1] Free throw attempts relative to field goal attempts
- [ ] **Points Per Possession** - [2] Raw points scored per possession
- [ ] **Shooting Distribution** - [2] Breakdown of scoring by two-pointers, three-pointers, and free throws
- [ ] **Fast Break Points Per Game** - [1] Points scored in transition

## Possession and Ball Control Metrics

- [x] **Offensive Rebound Percentage** - [2] Percentage of offensive rebounds captured
- [x] **Defensive Rebound Percentage** - [2] Percentage of defensive rebounds captured
- [x] **Total Rebound Percentage** - [2] Overall rebounding efficiency
- [x] **Turnover Percentage** - [2] Turnovers per 100 possessions
- [ ] **Ball Control Rating** - [2] Combined metric of assists, steals, and turnovers
- [x] **Assist-to-Turnover Ratio** - [1] Team's ratio of assists to turnovers
- [x] **Assist Rate** - [2] Percentage of field goals that are assisted
- [ ] **Steal Rate** - [2] Steals per opponent possession

## Defensive Metrics

- [ ] **Block Percentage** - [2] Percentage of opponent two-point attempts blocked
- [ ] **Opponent eFG%** - [1] Opponent's effective field goal percentage
- [ ] **Opponent Turnover Rate** - [2] Turnovers forced per 100 opponent possessions
- [ ] **Points Allowed by Play Type** - [4] Breakdown of points allowed by play type
- [ ] **Opponent Three-Point Rate** - [1] Percentage of opponent shots from three-point range
- [ ] **Perimeter Defense Rating** - [3] Effectiveness at defending three-point shots

## Matchup-Specific Features

- [ ] **Head-to-Head History** - [2] Historical performance in direct matchups
- [ ] **Style Matchup Rating** - [4] How well team style matches up against opponent style
- [ ] **Pace Control** - [3] Which team is likely to control the game's pace
- [ ] **Tournament Seeding** - [3] Historical performance based on seed matchups
- [ ] **Home/Away/Neutral Adjustment** - [2] Venue-specific performance adjustment

## Player-Based Aggregated Metrics

- [ ] **Star Player Impact** - [3] Influence of top players on team success
- [ ] **Depth Rating** - [3] Contribution from bench players
- [ ] **Player Efficiency Distribution** - [3] How evenly distributed efficiency is among starters
- [ ] **Player Consistency** - [3] Consistency of individual player performances
- [ ] **Lineup Efficiency** - [4] Performance of most common lineups

## Tournament-Specific Metrics

- [ ] **Round-by-Round Adjustment** - [3] How teams perform in specific tournament rounds
- [ ] **Days of Rest** - [2] Impact of rest days between games
- [ ] **Tournament-vs-Regular Season** - [3] Performance difference in tournament games
- [ ] **Under-Seeded Rating** - [3] Metric identifying teams performing above their seed line

## Data Engineering Features

- [x] **Exponentially Weighted Metrics** - [2] Recency-weighted versions of key statistics
- [ ] **Rolling Averages** - [2] N-game rolling averages of performance metrics
- [ ] **Season Segments** - [2] Performance in different parts of season (early, mid, late)
- [x] **Variance Features** - [2] Standard deviation of key performance metrics
- [ ] **Interaction Terms** - [3] Products of relevant features that may have combined effects
- [ ] **Game Importance Weight** - [3] Weighting games by importance/stakes
- [ ] **Outlier Management** - [2] Handling of outlier performances

## Model-Specific Generated Features

- [ ] **Principal Component Analysis** - [3] Dimension reduction of correlated features
- [ ] **Cluster Assignment** - [3] Team style/archetype classification
- [ ] **Win Probability Model** - [4] Pre-game win probability using multiple factors
- [ ] **Simulation-Based Features** - [4] Features derived from game simulations
- [ ] **Conference Tournament Impact** - [3] Effect of conference tournament performance 

## Implementation Plan

This section outlines our strategy for creating a comprehensive feature dataset for model training.

### Target Dataset

We will create a unified `team_features.parquet` dataset containing:
- All original columns from `team_season_statistics.parquet` (19 columns)
- All engineered features from our feature list (60+ columns)

This comprehensive approach ensures:
- A single, self-contained dataset for modeling
- Simplified data pipeline for training and prediction
- Clear documentation of all available features

### Implementation Phases

#### Phase 1: Foundation (Complexity Level 1-2) ✅

**Data Sources:**
- `team_season_statistics.parquet` - Base dataset structure
- `team_box.parquet` - Game-level statistics

**Features to Implement:**
1. ✅ Simple Shooting Metrics (eFG%, TS%, Three-Point Rate, Free Throw Rate)
2. ✅ Basic Possession Metrics (Rebound Percentages, Assist Rate, Turnover Percentage)
3. ✅ Win Percentage breakdowns (home, away, neutral)
4. ✅ Recent Form and Consistency metrics
5. ✅ Home Court Advantage rating

**Implementation Approach:**
1. ✅ Start with `team_season_statistics.parquet` as the base
2. ✅ Calculate game-level metrics from `team_box.parquet`
3. ✅ Aggregate to season level using appropriate methods (mean, weighted mean, etc.)
4. ✅ Join with the base dataset

#### Phase 2: Efficiency Metrics (Complexity Level 3)

**Data Sources:**
- Phase 1 dataset
- `team_box.parquet` - For calculating possession-based metrics
- `schedules.parquet` - For opponent information

**Features to Implement:**
1. Team Offensive/Defensive Efficiency Ratings
2. True Tempo 
3. Strength of Schedule
4. Tournament Experience metric

**Implementation Approach:**
1. Calculate raw offensive/defensive efficiency ratings
2. Implement iterative algorithm to adjust for opponent strength
3. Calculate tempo-adjusted metrics
4. Add these metrics to the dataset from Phase 1

#### Phase 3: Advanced Metrics (Complexity Level 3-4)

**Data Sources:**
- Phase 2 dataset
- `play_by_play.parquet` - For detailed game flow analysis
- `player_box.parquet` - For player-level contributions

**Features to Implement:**
1. Player-Based Metrics (Star Impact, Depth Rating)
2. Game Pace Adjustment
3. Style Matchup features
4. Tournament-specific metrics
5. Data Engineering features (Rolling Averages, Season Segments)

**Implementation Approach:**
1. Process play-by-play data to extract sequence information
2. Calculate player-level metrics and aggregate to team level
3. Implement tournament-specific logic
4. Generate engineering features from existing metrics

#### Phase 4: Complex Sequence Analysis (Complexity Level 4)

**Data Sources:**
- Phase 3 dataset
- `play_by_play.parquet` - For detailed sequence analysis

**Features to Implement:**
1. Kill Shots metrics
2. Clutch Performance
3. Points Allowed by Play Type
4. Lineup Efficiency
5. Model-Specific Generated Features

**Implementation Approach:**
1. Implement sequence detection algorithms for scoring runs
2. Calculate situational performance metrics (clutch situations)
3. Process multi-dimensional lineup data
4. Apply dimension reduction and clustering techniques
5. Create model-derived features

### Technical Implementation Notes

1. **Incremental Development:**
   - Each phase builds on the previous one
   - Features within each phase can be implemented in parallel
   - Verify data quality after each phase

2. **Data Storage Strategy:**
   - Store intermediate datasets during development
   - Final dataset will combine all features
   - Document all feature calculations in detail

3. **Validation Approach:**
   - Cross-validate features against published metrics where available
   - Run sanity checks on outlier values
   - Verify temporal consistency (features should evolve logically over time)

4. **Column Naming Convention:**
   - Use descriptive names with consistent formatting
   - Group related features with common prefixes
   - Include units in column names where applicable (e.g., _pct, _per_game)

By following this phased approach, we'll create a comprehensive feature dataset that captures the complex dynamics of team performance while maintaining tractable implementation complexity. 