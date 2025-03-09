# NCAA March Madness Data Reference

This section contains detailed technical documentation on the data used in the NCAA March Madness Predictor project.

## Data Documentation Structure

```
docs/reference/data/
├── README.md            # This overview file
├── overview.md          # General data overview
├── schema.md            # Data schemas for each data category
├── processing.md        # Data processing methodology
├── cleaning.md          # Data cleaning approach and procedures
└── validation.md        # Data validation rules and procedures
```

## Data Directory Structure

The project uses a structured approach to organizing data:

```
data/
├── raw/                  # Original unmodified data
│   ├── play_by_play/     # Play-by-play data
│   ├── player_box/       # Player box scores
│   ├── schedules/        # Game schedules
│   └── team_box/         # Team box scores
├── processed/            # Cleaned and transformed data
│   ├── play_by_play.parquet
│   ├── player_box.parquet
│   ├── schedules.parquet
│   ├── team_box.parquet
│   └── team_season_statistics.parquet
├── features/             # Engineered features for modeling
│   ├── team_performance_metrics.parquet
│   ├── shooting_metrics.parquet
│   └── combined/
│       └── full_feature_set.parquet
└── download.log          # Log file for data downloads
```

## Data Categories and Sources

All data is sourced from the [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/) GitHub repository. The data is organized in four main categories:

1. **Play-by-Play Data**: Detailed event-level data for each game
2. **Player Box Scores**: Individual player statistics for each game
3. **Game Schedules**: Game scheduling information (date, time, location, etc.)
4. **Team Box Scores**: Team-level statistics for each game

These files are available for seasons 2003 through 2025, providing 22+ years of historical data.

## Key Data Files

### Processed Data

| File | Description | Shape | Key Columns |
|------|-------------|-------|-------------|
| team_box.parquet | Game-level team statistics | ~236K rows × 57 cols | game_id, team_id, points, opponent_team_id |
| schedules.parquet | Game scheduling information | ~130K rows × 87 cols | game_id, home_id, away_id, season_type |
| player_box.parquet | Individual player statistics | ~3.4M rows × 55 cols | athlete_id, team_id, game_id, points |
| play_by_play.parquet | Event-level play data | ~28.8M rows × 67 cols | game_id, period, clock_display_value, type_text |
| team_season_statistics.parquet | Season-aggregated team stats | ~14K rows × 19 cols | team_id, season, games_played, win_percentage |

### Feature Data

Feature data is organized by feature category:

| File | Description | Associated Feature IDs |
|------|-------------|------------------------|
| team_performance_metrics.parquet | Team performance features | T01-T11 |
| shooting_metrics.parquet | Shooting and scoring features | S01-S07 |
| advanced_team_metrics.parquet | Advanced team metrics | A01-A06 |

## Related Documentation

- [Data Processing Guide](../../data_processing.md) - High-level overview of data processing principles
- [Data README](../../../data/README.md) - Additional information on the data directory organization
- [Feature Documentation](../../features/index.md) - Documentation for features built from this data 