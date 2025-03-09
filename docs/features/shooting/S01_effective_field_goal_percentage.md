# Feature: Effective Field Goal Percentage (ID: S01)

## Overview
**Category:** Shooting and Scoring Metrics  
**Complexity:** 1️⃣ (Simple calculation from direct data)  
**Status:** 🟢 Implemented

## Description
Effective Field Goal Percentage (eFG%) is an advanced basketball statistic that adjusts field goal percentage to account for the fact that three-point field goals are worth more than two-point field goals. This metric provides a more accurate measure of shooting efficiency than traditional field goal percentage by giving appropriate credit for made three-pointers.

Unlike traditional FG%, which treats all shots equally, eFG% correctly weights the value of three-point shots, making it especially valuable for evaluating teams with different shooting strategies (e.g., "three-point heavy" vs. "inside scoring" teams).

## Implementation
**File:** [`src/features/shooting/S01_effective_field_goal_percentage.py`](../../../src/features/shooting/S01_effective_field_goal_percentage.py)

## Formula/Calculation
```python
def calculate_efg_percentage(team_stats):
    """
    Calculate Effective Field Goal Percentage for a team.
    
    eFG% = (FGM + 0.5 * 3PM) / FGA
    
    Where:
    - FGM: Field Goals Made
    - 3PM: Three-Point Field Goals Made
    - FGA: Field Goals Attempted
    """
    fg_made = team_stats["field_goals_made"]
    three_pt_made = team_stats["three_point_field_goals_made"]
    fg_attempted = team_stats["field_goals_attempted"]
    
    # Avoid division by zero
    if fg_attempted == 0:
        return 0.0
    
    efg_percentage = (fg_made + 0.5 * three_pt_made) / fg_attempted
    
    return efg_percentage
```

## Data Requirements
- **Input Data:** `team_box.parquet`
- **Required Columns:** 
  - `field_goals_made`: Number of field goals made by the team
  - `three_point_field_goals_made`: Number of three-point field goals made by the team
  - `field_goals_attempted`: Number of field goals attempted by the team
- **Output:** Single float value between 0.0 and 1.0 (can be multiplied by 100 for percentage display)

## Implementation Notes
- Values should be calculated on a per-game basis and then aggregated for season-level metrics
- For aggregation, use weighted average by field goal attempts rather than simple average
- When working with play-by-play data, ensure the values are correctly accumulated
- If a team has no field goal attempts in a game (extremely rare), return 0.0 rather than raising a division by zero error

## Interpretation
- **Range:** Typically between 0.400 (40.0%) and 0.600 (60.0%) for NCAA teams
- **Benchmark:** 
  - Below 0.470: Poor shooting efficiency
  - 0.470-0.520: Average shooting efficiency
  - 0.520-0.550: Good shooting efficiency
  - Above 0.550: Excellent shooting efficiency
- **Context:** 
  - NCAA Division I average is typically around 0.500 (50.0%)
  - Teams with high three-point attempt rates tend to have higher eFG% than teams that focus on two-point shots with similar accuracy
  - Should be evaluated alongside shot selection metrics (Three-Point Rate, S03) for complete context

## Usage Examples
```python
import polars as pl
from src.features.shooting import shooting_metrics

# For a single game
game_stats = pl.read_parquet("data/processed/team_box.parquet").filter(
    (pl.col("game_id") == 401372644) & (pl.col("team_id") == 12345)
)
efg = shooting_metrics.calculate_efg_percentage(game_stats)
print(f"Team eFG% for this game: {efg:.3f}")

# For season aggregation
season_stats = pl.read_parquet("data/processed/team_box.parquet").filter(
    (pl.col("season") == 2023) & (pl.col("team_id") == 12345)
)
# Group by team_id and calculate weighted average
season_efg = season_stats.group_by("team_id").agg([
    ((pl.col("field_goals_made") + 0.5 * pl.col("three_point_field_goals_made")).sum() / 
     pl.col("field_goals_attempted").sum()).alias("efg_percentage")
])
```

## Visualization
- Bar charts comparing team eFG% across conference
- Scatter plots showing relationship between eFG% and offensive efficiency
- Time series showing team eFG% trend throughout the season
- Shot charts colored by team/opponent eFG% from different court regions

## Related Features
- S02 True Shooting Percentage (TS%): A more comprehensive shooting efficiency metric that also accounts for free throws
- S03 Three-Point Rate: Contextualizes eFG% by revealing how much a team relies on three-point shooting
- T03 Team Offensive Efficiency Rating: Uses eFG% as one component of overall offensive effectiveness

## Version History
- 2025-03-08 - Initial implementation 