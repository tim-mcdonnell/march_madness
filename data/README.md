# NCAA March Madness Data Directory

This directory contains data used for the NCAA March Madness prediction project.

## Directory Structure

```
data/
├── raw/                  # Original unmodified data
│   ├── play_by_play/     # Play-by-play data
│   ├── player_box/       # Player box scores
│   ├── schedules/        # Game schedules
│   └── team_box/         # Team box scores
├── processed/            # Cleaned and transformed data
├── features/             # Engineered features for modeling 
└── download.log          # Log file for data downloads
```

## Data Sources

All data is sourced from the [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/) GitHub repository, which provides comprehensive NCAA men's basketball data.

### Raw Data Categories

1. **Play-by-Play Data**
   - File pattern: `play_by_play_{YEAR}.parquet`
   - Contains detailed event-level data for each game

2. **Player Box Scores**
   - File pattern: `player_box_{YEAR}.parquet`
   - Contains individual player statistics for each game

3. **Game Schedules**
   - File pattern: `mbb_schedule_{YEAR}.parquet`
   - Contains game scheduling information including date, time, location, etc.

4. **Team Box Scores**
   - File pattern: `team_box_{YEAR}.parquet`
   - Contains team-level statistics for each game

Files are available for seasons 2003 through 2025, providing 22+ years of historical data.

## Data Processing Principles

This project maintains a strict separation between data processing and feature engineering:

1. **Data Processing** (`data/processed/`):
   - Focuses only on cleaning, standardizing, and organizing raw data
   - Removes duplicates, fixes data types, standardizes column names
   - Only contains metrics directly derivable from the source data
   - Does NOT add synthetic values, placeholders, or calculated metrics

2. **Feature Engineering** (`data/features/`):
   - Creates new derived metrics (efficiency ratings, factors, etc.)
   - Applies transformations like normalization and encoding
   - Generates features specifically for model training

### Files in Processed Directory

The processed directory contains standardized versions of the raw data files:

- `play_by_play.parquet` - Cleaned and standardized play-by-play data
- `player_box.parquet` - Cleaned and standardized player statistics
- `schedules.parquet` - Cleaned and standardized game schedules
- `team_box.parquet` - Cleaned and standardized team statistics
- `team_season_statistics.parquet` - Season-aggregated team statistics (wins, losses, points, etc.)

## Data Download

Data can be downloaded using the functions in `src/data/loader.py`. The main functions are:

```python
from src.data.loader import download_all_data

# Download all data for all years (2003-2025)
download_all_data()

# Download data for a specific year range
download_all_data(start_year=2020, end_year=2025)

# Download only specific categories
download_all_data(categories=["play_by_play", "team_box"])
```

## Data Loading

Parquet files can be loaded using the functions in `src/data/loader.py`. The main functions are:

```python
from src.data.loader import load_category_data

# Load play-by-play data for 2023
pbp_data = load_category_data("play_by_play", 2023)

# Load team box scores for 2023
team_box_data = load_category_data("team_box", 2023)
```

## Processed Data Reference

This section provides detailed information about each processed data file, including column descriptions and data types.

### team_season_statistics.parquet

Season-level aggregated statistics for each team across all games played.

**Shape**: 14,080 rows × 19 columns

| Column | Type | Description |
|--------|------|-------------|
| team_id | integer | Unique identifier for the team |
| team_name | string | Name of the team |
| team_display_name | string | Display name of the team |
| season | integer | Season year (e.g., 2023) |
| games_played | integer | Total number of games played in the season |
| total_points | integer | Total points scored across all games |
| points_per_game | float | Average points per game |
| opponent_points | integer | Total points allowed to opponents |
| opponent_points_per_game | float | Average points allowed per game |
| home_games | integer | Number of home games played |
| away_games | integer | Number of away games played |
| wins | integer | Total number of wins |
| losses | integer | Total number of losses |
| home_wins | integer | Number of wins at home |
| away_wins | integer | Number of wins away |
| avg_point_differential | float | Average point difference (team score - opponent score) |
| win_percentage | float | Percentage of games won (0-1) |
| home_win_pct | float | Percentage of home games won (0-1) |
| away_win_pct | float | Percentage of away games won (0-1) |

### team_box.parquet

Game-level team statistics for each team in each game played.

**Shape**: 236,522 rows × 57 columns

| Column | Type | Description |
|--------|------|-------------|
| assists | integer | Number of assists |
| blocks | integer | Number of blocked shots |
| defensive_rebounds | integer | Number of defensive rebounds |
| fast_break_points | string | Number of points scored on fast breaks |
| field_goal_pct | float | Field goal percentage (made/attempted) |
| field_goals_attempted | integer | Number of field goals attempted |
| field_goals_made | integer | Number of field goals made |
| flagrant_fouls | integer | Number of flagrant fouls committed |
| fouls | integer | Number of fouls committed |
| free_throw_pct | float | Free throw percentage (made/attempted) |
| free_throws_attempted | integer | Number of free throws attempted |
| free_throws_made | integer | Number of free throws made |
| game_date | date | Date of the game |
| game_date_time | datetime | Date and time of the game |
| game_id | integer | Unique identifier for the game |
| largest_lead | integer | Largest lead achieved during the game |
| offensive_rebounds | integer | Number of offensive rebounds |
| team_id | integer | Unique identifier for the team |
| team_name | string | Name of the team |
| team_display_name | string | Display name of the team |
| team_score | integer | Total points scored by the team |
| team_home_away | string | Whether team was home or away ("home"/"away") |
| opponent_team_id | integer | Unique identifier for the opposing team |
| opponent_team_name | string | Name of the opposing team |
| opponent_team_score | integer | Total points scored by the opponent |
| season | integer | Season year (e.g., 2023) |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| steals | integer | Number of steals |
| team_turnovers | integer | Number of team turnovers |
| technical_fouls | integer | Number of technical fouls |
| three_point_field_goal_pct | float | Three-point field goal percentage |
| three_point_field_goals_attempted | integer | Number of three-point field goals attempted |
| three_point_field_goals_made | integer | Number of three-point field goals made |
| total_rebounds | integer | Total number of rebounds |
| total_technical_fouls | integer | Total number of technical fouls |
| total_turnovers | integer | Total number of turnovers (team + individual) |
| turnover_points | string | Points scored off turnovers |
| turnovers | integer | Number of individual player turnovers |

### schedules.parquet

Comprehensive game scheduling information for all games played.

**Shape**: 130,089 rows × 87 columns

| Column | Type | Description |
|--------|------|-------------|
| game_id | integer | Unique identifier for the game |
| season | integer | Season year (e.g., 2023) |
| date | date | Date of the game |
| game_date | date | Game date |
| game_date_time | datetime | Game date and time |
| neutral_site | boolean | Whether game was played at a neutral site |
| home_id | integer | Unique identifier for home team |
| home_name | string | Name of home team |
| home_display_name | string | Display name of home team |
| home_abbreviation | string | Abbreviation of home team |
| home_score | integer | Score of home team |
| away_id | integer | Unique identifier for away team |
| away_name | string | Name of away team |
| away_display_name | string | Display name of away team |
| away_abbreviation | string | Abbreviation of away team |
| away_score | integer | Score of away team |
| home_winner | boolean | Whether home team won |
| away_winner | boolean | Whether away team won |
| conference_competition | boolean | Whether game was between conference opponents |
| attendance | float | Number of spectators at the game |
| venue_id | integer | Unique identifier for the venue |
| venue_full_name | string | Full name of the venue |
| venue_address_city | string | City where venue is located |
| venue_address_state | string | State where venue is located |
| venue_capacity | float | Seating capacity of venue |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| notes_headline | string | Additional game notes |
| notes_type | string | Type of notes (e.g., "NCAA Tournament") |

### player_box.parquet

Game-level statistics for individual players in each game.

**Shape**: 3,452,347 rows × 55 columns

| Column | Type | Description |
|--------|------|-------------|
| athlete_id | integer | Unique identifier for the player |
| athlete_display_name | string | Full display name of the player |
| athlete_position_name | string | Position of the player |
| athlete_position_abbreviation | string | Abbreviated position of the player |
| athlete_jersey | string | Jersey number of the player |
| team_id | integer | Unique identifier for the player's team |
| team_name | string | Name of the player's team |
| team_display_name | string | Display name of the player's team |
| team_abbreviation | string | Abbreviation of the player's team |
| game_id | integer | Unique identifier for the game |
| game_date | date | Date of the game |
| game_date_time | datetime | Date and time of the game |
| season | integer | Season year (e.g., 2023) |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| home_away | string | Whether the player's team was home or away |
| starter | boolean | Whether the player was a starter |
| active | boolean | Whether the player was active for the game |
| did_not_play | boolean | Whether the player did not play |
| minutes | string | Minutes played |
| points | integer | Total points scored |
| field_goals_made | integer | Number of field goals made |
| field_goals_attempted | integer | Number of field goals attempted |
| three_point_field_goals_made | integer | Number of three-point field goals made |
| three_point_field_goals_attempted | integer | Number of three-point field goals attempted |
| free_throws_made | integer | Number of free throws made |
| free_throws_attempted | integer | Number of free throws attempted |
| rebounds | integer | Total number of rebounds |
| offensive_rebounds | integer | Number of offensive rebounds |
| defensive_rebounds | integer | Number of defensive rebounds |
| assists | integer | Number of assists |
| steals | integer | Number of steals |
| blocks | integer | Number of blocked shots |
| turnovers | integer | Number of turnovers |
| fouls | integer | Number of fouls committed |
| ejected | boolean | Whether the player was ejected |
| team_score | integer | Score of the player's team |
| opponent_team_id | integer | Unique identifier for the opposing team |
| opponent_team_name | string | Name of the opposing team |
| opponent_team_score | integer | Score of the opposing team |
| team_winner | boolean | Whether the player's team won |

### play_by_play.parquet

Detailed event-level data for each play in each game.

**Shape**: 28,830,165 rows × 67 columns

| Column | Type | Description |
|--------|------|-------------|
| game_id | integer | Unique identifier for the game |
| game_play_number | integer | Sequential play number within the game |
| sequence_number | integer | Sequence number of the play |
| period | integer | Period of the game (1=1st half, 2=2nd half, etc.) |
| period_number | integer | Numerical period indicator |
| period_display_value | string | Display text for the period (e.g., "1st") |
| home_score | integer | Home team score at this point in the game |
| away_score | integer | Away team score at this point in the game |
| clock_display_value | string | Display of the game clock |
| clock_minutes | integer | Minutes on game clock |
| clock_seconds | integer | Seconds on game clock |
| team_id | integer | ID of the team involved in the play |
| home_team_id | integer | ID of the home team |
| home_team_name | string | Name of the home team |
| home_team_mascot | string | Mascot of the home team |
| away_team_id | integer | ID of the away team |
| away_team_name | string | Name of the away team |
| away_team_mascot | string | Mascot of the away team |
| type_id | integer | ID of the play type |
| type_text | string | Description of the play type (e.g., "JumpShot", "Rebound") |
| text | string | Full text description of the play |
| score_value | integer | Point value of the play if scoring play |
| scoring_play | boolean | Whether the play resulted in points |
| shooting_play | boolean | Whether the play was a shot attempt |
| athlete_id_1 | integer | ID of the primary player involved |
| athlete_id_2 | integer | ID of the secondary player involved (if applicable) |
| coordinate_x | float | X-coordinate location of the play |
| coordinate_y | float | Y-coordinate location of the play |
| home_timeout_called | boolean | Whether home team called timeout |
| away_timeout_called | boolean | Whether away team called timeout |
| season | integer | Season year (e.g., 2023) |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| start_game_seconds_remaining | integer | Seconds remaining in the game at start of play |
| end_game_seconds_remaining | integer | Seconds remaining in the game at end of play |
| start_period_seconds_remaining | integer | Seconds remaining in the period at start of play |
| end_period_seconds_remaining | integer | Seconds remaining in the period at end of play |

## Notes

- The raw data files can be large, especially for play-by-play data
- Downloads are cached, so repeated calls to download functions will skip files that already exist (unless `overwrite=True` is specified)
- Progress and errors during download are logged in `data/download.log`