# Working with Data

This guide provides practical information for accessing and working with the datasets in the NCAA March Madness Predictor project.

## Available Datasets

The project provides several standardized datasets:

### Processed Data Files

Located in `data/processed/`:

| File | Description | Size (approx) |
|------|-------------|---------------|
| play_by_play.parquet | Standardized play-by-play event data | Large (5GB+) |
| player_box.parquet | Player statistics for each game | Medium (500MB+) |
| schedules.parquet | Game schedule information | Small (50MB) |
| team_box.parquet | Team statistics for each game | Medium (200MB+) |
| team_season_statistics.parquet | Aggregated team statistics by season | Small (5MB) |

## Loading Data

### Using Polars (Recommended)

The project uses [Polars](https://pola.rs/) as its primary data manipulation library. To load a dataset:

```python
import polars as pl

# Load a processed dataset
team_box = pl.read_parquet("data/processed/team_box.parquet")

# Display the first few rows
print(team_box.head())

# Get summary information
print(team_box.describe())
```

### Using Pandas

If you prefer using pandas:

```python
import pandas as pd

# Load a processed dataset
team_box = pd.read_parquet("data/processed/team_box.parquet")

# Display the first few rows
print(team_box.head())

# Get summary information
print(team_box.describe())
```

## Common Data Operations

### Filtering Data

```python
import polars as pl

# Load team box scores
team_box = pl.read_parquet("data/processed/team_box.parquet")

# Filter by season
season_2023 = team_box.filter(pl.col("season") == 2023)

# Filter by team
duke_games = team_box.filter(pl.col("team_name").str.contains("Duke"))

# Filter by multiple conditions
duke_home_wins = team_box.filter(
    (pl.col("team_name").str.contains("Duke")) & 
    (pl.col("home_away") == "home") & 
    (pl.col("result") == "W")
)
```

### Joining Datasets

```python
import polars as pl

# Load datasets
schedules = pl.read_parquet("data/processed/schedules.parquet")
team_box = pl.read_parquet("data/processed/team_box.parquet")

# Join datasets on game_id
game_details = schedules.join(
    team_box,
    on="game_id",
    how="inner"
)
```

### Grouping and Aggregating

```python
import polars as pl

# Load team box scores
team_box = pl.read_parquet("data/processed/team_box.parquet")

# Group by team and season, then calculate averages
team_averages = team_box.group_by(["team_id", "team_name", "season"]).agg([
    pl.col("points").mean().alias("avg_points"),
    pl.col("field_goals_made").mean().alias("avg_fg_made"),
    pl.col("field_goals_attempted").mean().alias("avg_fg_attempted"),
    pl.col("assists").mean().alias("avg_assists"),
    pl.col("turnovers").mean().alias("avg_turnovers"),
])
```

## Working with Play-by-Play Data

The play-by-play dataset is the most detailed and largest dataset in the project:

```python
import polars as pl

# Load play-by-play data
pbp = pl.read_parquet("data/processed/play_by_play.parquet")

# Filter to specific game
game_events = pbp.filter(pl.col("game_id") == "401403384")

# Get scoring plays
scoring_plays = pbp.filter(
    pl.col("score_value").is_not_null() & 
    (pl.col("score_value") > 0)
)

# Get three-point shots
three_pointers = pbp.filter(
    (pl.col("event_type") == "shot") & 
    (pl.col("score_value") == 3)
)
```

## Performance Tips

1. **Use Lazy Evaluation**: For large datasets, use Polars' lazy API:
   ```python
   import polars as pl
   
   # Create a lazy frame
   pbp_lazy = pl.scan_parquet("data/processed/play_by_play.parquet")
   
   # Build a query
   result = pbp_lazy.filter(pl.col("season") == 2023).select(
       ["game_id", "team_name", "event_type", "score_value"]
   )
   
   # Execute the query when needed
   final_df = result.collect()
   ```

2. **Filter Early**: Apply filters as early as possible to reduce memory usage.

3. **Select Only Needed Columns**: Only load the columns you need for analysis.

4. **Consider Chunking**: For very large operations, process data in chunks.

## Next Steps

After working with the processed data, you may want to:

- Generate [features](../reference/features/overview.md) for modeling
- Explore data patterns with our [visualization tools](visualization.md)
- Build predictive models with the [modeling framework](modeling.md)

If you encounter any issues with the data, please check the [troubleshooting guide](troubleshooting.md) or open an issue in the GitHub repository. 