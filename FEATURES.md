# NCAA Basketball Prediction Features

## Overview
This document tracks all features for our NCAA basketball prediction model. Features are organized by category and include implementation status and complexity. This registry serves as the single source of truth for feature development tracking.

## Feature Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Implemented
- 📝 Documented
- 🔧 Issue Opened (Data quality/completeness issue identified)

## Complexity Legend
- 1️⃣ Simple calculation from direct data
- 2️⃣ Moderate calculation requiring some data manipulation
- 3️⃣ Complex calculation requiring significant data processing
- 4️⃣ Very complex requiring advanced methods
- 5️⃣ Extremely complex requiring sophisticated algorithms

## Features

### Team Performance Metrics
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| T01 | Win Percentage | Overall, home, away, and neutral site | 1️⃣ | 🟢 🔧 | [src/features/team_performance/T01_win_percentage.py](src/features/team_performance/T01_win_percentage.py) | [docs/features/team_performance/T01_win_percentage.md](docs/features/team_performance/T01_win_percentage.md) |
| T02 | Point Differential | Average margin of victory/defeat | 1️⃣ | 🟢 🔧 | [src/features/team_performance/T02_point_differential.py](src/features/team_performance/T02_point_differential.py) | [docs/features/team_performance/T02_point_differential.md](docs/features/team_performance/T02_point_differential.md) |
| T03 | Team Offensive Efficiency Rating (O-Rate) | Points scored per 100 possessions, adjusted for opponent strength | 3️⃣ | 🟡 | [PR #23](https://github.com/username/repo/pull/23) | - |
| T04 | Team Defensive Efficiency Rating (D-Rate) | Points allowed per 100 possessions, adjusted for opponent strength | 3️⃣ | 🔴 | - | - |
| T05 | Relative Rating | Combined O-Rate and D-Rate (net efficiency) | 3️⃣ | 🔴 | - | - |
| T06 | True Tempo | Average possessions per 40 minutes, adjusted for opponents | 2️⃣ | 🔴 | - | - |
| T07 | Opponent Strength Adjustment | How a team performs against strong vs. weak competition | 4️⃣ | 🔴 | - | - |
| T08 | Game Pace Adjustment | How a team performs in fast vs. slow-paced games | 3️⃣ | 🔴 | - | - |
| T09 | Recent Form | Performance trend over the last N games (weighted recency) | 2️⃣ | 🟢 🔧 | [src/features/team_performance/T09_recent_form.py](src/features/team_performance/T09_recent_form.py) | - |
| T10 | Consistency Rating | Variance in game-to-game performance | 2️⃣ | 🟢 🔧 | [src/features/team_performance/T10_consistency_rating.py](src/features/team_performance/T10_consistency_rating.py) | - |
| T11 | Strength of Schedule | Overall schedule difficulty rating | 3️⃣ | 🔴 | - | - |

### Advanced Team Metrics
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| A01 | Offensive Efficiency | Points scored per 100 possessions | 2️⃣ | 🟢 | [src/features/advanced_team/A01_offensive_efficiency.py](src/features/advanced_team/A01_offensive_efficiency.py) | [docs/features/advanced_team/A01_offensive_efficiency.md](docs/features/advanced_team/A01_offensive_efficiency.md) |
| A02 | Kill Shots Per Game | Number of 10-0 or better scoring runs per game | 4️⃣ | 🔴 | - | - |
| A03 | Kill Shots Allowed Per Game | Number of opponent 10-0 or better scoring runs per game | 4️⃣ | 🔴 | - | - |
| A04 | Kill Shots Margin | Difference between team's kill shots and opponents' | 4️⃣ | 🔴 | - | - |
| A05 | Clutch Performance | Performance in close games (last 5 minutes, margin ≤ 5 points) | 4️⃣ | 🔴 | - | - |
| A06 | Home Court Advantage | Rating of how much better a team performs at home | 2️⃣ | 🟢📝 | [src/features/advanced_team/A06_home_court_advantage.py](src/features/advanced_team/A06_home_court_advantage.py) | [docs/features/advanced_team/A06_home_court_advantage.md](docs/features/advanced_team/A06_home_court_advantage.md) |
| A07 | Tournament Experience | Previous NCAA tournament experience metric | 3️⃣ | 🔴 | - | - |

### Shooting and Scoring Metrics
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| S01 | Effective Field Goal Percentage (eFG%) | Field goal percentage adjusted for three-pointers | 1️⃣ | 🟢 | [src/features/shooting/S01_effective_field_goal_percentage.py](src/features/shooting/S01_effective_field_goal_percentage.py) | [docs/features/shooting/S01_effective_field_goal_percentage.md](docs/features/shooting/S01_effective_field_goal_percentage.md) |
| S02 | True Shooting Percentage (TS%) | Shooting efficiency including free throws | 1️⃣ | 🟢 🔧 | [src/features/shooting/S02_true_shooting_percentage.py](src/features/shooting/S02_true_shooting_percentage.py) | [docs/features/shooting/S02_true_shooting_percentage.md](docs/features/shooting/S02_true_shooting_percentage.md) |
| S03 | Three-Point Rate | Percentage of field goal attempts from three-point range | 1️⃣ | 🟢 🔧 | [src/features/shooting/S03_three_point_rate.py](src/features/shooting/S03_three_point_rate.py) | [docs/features/shooting/S03_three_point_rate.md](docs/features/shooting/S03_three_point_rate.md) |
| S04 | Free Throw Rate | Free throw attempts relative to field goal attempts | 1️⃣ | 🟢 🔧 | [src/features/shooting/S04_free_throw_rate.py](src/features/shooting/S04_free_throw_rate.py) | - |
| S05 | Points Per Possession | Raw points scored per possession | 2️⃣ | 🔴 | - | - |
| S06 | Shooting Distribution | Breakdown of scoring by two-pointers, three-pointers, and free throws | 2️⃣ | 🔴 | - | - |
| S07 | Fast Break Points Per Game | Points scored in transition | 1️⃣ | 🔴 | - | - |

### Possession and Ball Control Metrics
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| P01 | Possessions | Estimated number of possessions per game | 2️⃣ | 🟢 🔧 | [src/features/possession/P01_possessions.py](src/features/possession/P01_possessions.py) | [docs/features/possession/P01_possessions.md](docs/features/possession/P01_possessions.md) |
| P02 | Offensive Rebound Percentage | Percentage of offensive rebounds captured | 2️⃣ | 🟢 🔧 | [src/features/possession/P02_offensive_rebound_percentage.py](src/features/possession/P02_offensive_rebound_percentage.py) | - |
| P03 | Defensive Rebound Percentage | Percentage of defensive rebounds captured | 2️⃣ | 🟢 🔧 | [src/features/possession/P03_defensive_rebound_percentage.py](src/features/possession/P03_defensive_rebound_percentage.py) | - |
| P04 | Total Rebound Percentage | Overall rebounding efficiency | 2️⃣ | 🟢 🔧 | [src/features/possession/P04_total_rebound_percentage.py](src/features/possession/P04_total_rebound_percentage.py) | - |
| P05 | Turnover Percentage | Turnovers per 100 possessions | 2️⃣ | 🟢 🔧 | [src/features/possession/P05_turnover_percentage.py](src/features/possession/P05_turnover_percentage.py) | - |
| P06 | Ball Control Rating | Combined metric of assists, steals, and turnovers | 2️⃣ | 🔴 | - | - |
| P07 | Assist-to-Turnover Ratio | Team's ratio of assists to turnovers | 1️⃣ | 🟢 🔧 | [src/features/possession/P07_assist_to_turnover_ratio.py](src/features/possession/P07_assist_to_turnover_ratio.py) | - |
| P08 | Assist Rate | Percentage of field goals that are assisted | 2️⃣ | 🟢 🔧 | [src/features/possession/P08_assist_rate.py](src/features/possession/P08_assist_rate.py) | - |
| P09 | Steal Rate | Steals per opponent possession | 2️⃣ | 🔴 | - | - |

### Defensive Metrics
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| D01 | Block Percentage | Percentage of opponent two-point attempts blocked | 2️⃣ | 🔴 | - | - |
| D02 | Opponent eFG% | Opponent's effective field goal percentage | 1️⃣ | 🔴 | - | - |
| D03 | Opponent Turnover Rate | Turnovers forced per 100 opponent possessions | 2️⃣ | 🔴 | - | - |
| D04 | Points Allowed by Play Type | Breakdown of points allowed by play type | 4️⃣ | 🔴 | - | - |
| D05 | Opponent Three-Point Rate | Percentage of opponent shots from three-point range | 1️⃣ | 🔴 | - | - |
| D06 | Perimeter Defense Rating | Effectiveness at defending three-point shots | 3️⃣ | 🔴 | - | - |

### Matchup-Specific Features
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| M01 | Head-to-Head History | Historical performance in direct matchups | 2️⃣ | 🔴 | - | - |
| M02 | Style Matchup Rating | How well team style matches up against opponent style | 4️⃣ | 🔴 | - | - |
| M03 | Pace Control | Which team is likely to control the game's pace | 3️⃣ | 🔴 | - | - |
| M04 | Tournament Seeding | Historical performance based on seed matchups | 3️⃣ | 🔴 | - | - |
| M05 | Home/Away/Neutral Adjustment | Venue-specific performance adjustment | 2️⃣ | 🔴 | - | - |

### Player-Based Aggregated Metrics
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| Y01 | Star Player Impact | Influence of top players on team success | 3️⃣ | 🔴 | - | - |
| Y02 | Depth Rating | Contribution from bench players | 3️⃣ | 🔴 | - | - |
| Y03 | Player Efficiency Distribution | How evenly distributed efficiency is among starters | 3️⃣ | 🔴 | - | - |
| Y04 | Player Consistency | Consistency of individual player performances | 3️⃣ | 🔴 | - | - |
| Y05 | Lineup Efficiency | Performance of most common lineups | 4️⃣ | 🔴 | - | - |

### Tournament-Specific Metrics
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| U01 | Round-by-Round Adjustment | How teams perform in specific tournament rounds | 3️⃣ | 🔴 | - | - |
| U02 | Days of Rest | Impact of rest days between games | 2️⃣ | 🔴 | - | - |
| U03 | Tournament-vs-Regular Season | Performance difference in tournament games | 3️⃣ | 🔴 | - | - |
| U04 | Under-Seeded Rating | Metric identifying teams performing above their seed line | 3️⃣ | 🔴 | - | - |

### Data Engineering Features
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| E01 | Exponentially Weighted Metrics | Recency-weighted versions of key statistics | 2️⃣ | 🔴 | - | - |
| E02 | Rolling Averages | N-game rolling averages of performance metrics | 2️⃣ | 🔴 | - | - |
| E03 | Season Segments | Performance in different parts of season (early, mid, late) | 2️⃣ | 🔴 | - | - |
| E04 | Variance Features | Standard deviation of key performance metrics | 2️⃣ | 🔴 | - | - |
| E05 | Interaction Terms | Products of relevant features that may have combined effects | 3️⃣ | 🔴 | - | - |
| E06 | Game Importance Weight | Weighting games by importance/stakes | 3️⃣ | 🔴 | - | - |
| E07 | Outlier Management | Handling of outlier performances | 2️⃣ | 🔴 | - | - |

### Model-Specific Generated Features
| ID | Feature | Description | Complexity | Status | Implementation | Documentation |
|----|---------|-------------|-----------|--------|----------------|---------------|
| G01 | Principal Component Analysis | Dimension reduction of correlated features | 3️⃣ | 🔴 | - | - |
| G02 | Cluster Assignment | Team style/archetype classification | 3️⃣ | 🔴 | - | - |
| G03 | Win Probability Model | Pre-game win probability using multiple factors | 4️⃣ | 🔴 | - | - |
| G04 | Simulation-Based Features | Features derived from game simulations | 4️⃣ | 🔴 | - | - |
| G05 | Conference Tournament Impact | Effect of conference tournament performance | 3️⃣ | 🔴 | - | - |