# Feature: Win Percentage (ID: T01)

## Overview
**Category:** Team Performance Metrics  
**Complexity:** 1️⃣ (Simple calculation from direct data)  
**Status:** 🟢 Implemented

## Description
Win Percentage measures the proportion of games won by a team. It provides insight into a team's overall performance and is one of the most fundamental metrics for evaluating team success. This feature includes overall win percentage as well as breakdowns by venue type (home, away, neutral site).

The metric serves as a baseline for team performance evaluation and is particularly valuable when comparing teams across different conferences or divisions.

## Implementation
**File:** [`src/features/team_performance/T01_win_percentage.py`](../../../src/features/team_performance/T01_win_percentage.py)

## Formula/Calculation
```python
def calculate_win_percentage(team_results):
    """
    Calculate Win Percentage for a team.
    
    Formula: win_percentage = wins / (wins + losses)
    
    For home/away/neutral breakdowns, the calculation is applied to the
    corresponding subset of games.
    """
    wins = team_results.filter(pl.col("win") == True).height
    total_games = team_results.height
    
    # Avoid division by zero
    if total_games == 0:
        return 0.0
    
    return wins / total_games
```

## Data Requirements
- **Input Data:** `schedules.parquet`
- **Required Columns:** 
  - `home_id`: ID of the home team
  - `away_id`: ID of the away team
  - `home_score`: Points scored by the home team
  - `away_score`: Points scored by the away team
  - `neutral_site`: Whether the game was played at a neutral site
  - `season`: Season year
- **Output:** DataFrame with team_id, team_location, team_name, season, win_percentage, home_win_percentage, away_win_percentage, and neutral_win_percentage columns

## Implementation Notes
- The calculation separates home, away, and neutral site games to provide venue-specific win percentages
- For teams with no games in a particular venue type, the win percentage is calculated based on available data
- The feature handles games at neutral sites correctly, which is important for tournament analysis
- Division by zero is handled with appropriate defaults when a team hasn't played any games of a certain type

## Interpretation
- **Range:** 0.000 to 1.000 (0% to 100%)
- **Benchmark:** 
  - Below 0.500: Losing record
  - 0.500: Even record (equal wins and losses)
  - 0.600-0.700: Good regular season record
  - Above 0.800: Elite record
- **Context:** 
  - Most NCAA Division I teams have home win percentages significantly higher than away win percentages
  - Top teams typically have overall win percentages above 0.750
  - Tournament-bound teams usually have win percentages above 0.650
  - Should be evaluated alongside strength of schedule metrics for proper context

## Usage Examples
```python
import polars as pl
from src.features import initialize_features, calculate_features

# Initialize features
initialize_features()

# Calculate win percentage feature only
results = calculate_features(feature_ids=["T01"])

# Calculate all team performance features
results = calculate_features(category="team_performance")

# Access the results
win_pct_df = results["team_performance"]
print(f"Team win percentages: {win_pct_df.filter(pl.col('season') == 2024).head()}")
```

## Visualization
- Bar charts comparing team win percentages within conferences
- Scatter plots showing relationship between home and away win percentages
- Line charts tracking win percentage over multiple seasons
- Heat maps showing win percentage by conference and season

## Related Features
- T02 Point Differential: Often correlated with win percentage but provides additional context
- T03 Team Offensive Efficiency Rating: Explains offensive component contributing to wins
- T04 Team Defensive Efficiency Rating: Explains defensive component contributing to wins
- T11 Strength of Schedule: Provides context for evaluating win percentage

## Version History
- 2025-03-08 - Initial implementation 