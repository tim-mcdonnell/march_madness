# Data Schema Reference

This document provides a detailed reference for the schema of each processed dataset in the project. Understanding these schemas is essential for working with the data effectively.

## play_by_play.parquet

Contains detailed event-level data for each play in every game.

| Column | Type | Description |
|--------|------|-------------|
| game_id | string | Unique identifier for the game |
| play_id | int | Sequential identifier for the play within the game |
| sequence_number | int | Order of the play within the game |
| period | int | Game period (1-2 for halves, can be higher for overtime) |
| period_type | string | Type of period (HALF, OVERTIME) |
| time_remaining_minutes | int | Minutes remaining in the period |
| time_remaining_seconds | int | Seconds remaining in the period |
| timestamp | timestamp | Date and time of the play |
| team_id | string | ID of the team involved in the play |
| team_name | string | Name of the team involved in the play |
| athlete_id | string | ID of the athlete involved (if applicable) |
| athlete_name | string | Name of the athlete involved (if applicable) |
| event_type | string | Type of play event (SHOT, REBOUND, TURNOVER, etc.) |
| event_description | string | Text description of the play |
| location_x | float | X-coordinate on court (if available) |
| location_y | float | Y-coordinate on court (if available) |
| shot_type | string | Type of shot (2PTR, 3PTR, FREE THROW) |
| shot_outcome | string | Outcome of shot (MADE, MISSED) |
| home_score | int | Home team score after the play |
| away_score | int | Away team score after the play |
| season | int | Season year (e.g., 2023 for 2022-2023 season) |

## player_box.parquet

Contains individual player statistics for each game.

| Column | Type | Description |
|--------|------|-------------|
| game_id | string | Unique identifier for the game |
| team_id | string | ID of the player's team |
| team_name | string | Name of the player's team |
| athlete_id | string | Unique identifier for the player |
| athlete_name | string | Name of the player |
| position | string | Player's position |
| starter | boolean | Whether player was a starter |
| minutes_played | float | Minutes played in the game |
| field_goals_made | int | Number of field goals made |
| field_goals_attempted | int | Number of field goals attempted |
| three_point_made | int | Number of three-pointers made |
| three_point_attempted | int | Number of three-pointers attempted |
| free_throws_made | int | Number of free throws made |
| free_throws_attempted | int | Number of free throws attempted |
| offensive_rebounds | int | Number of offensive rebounds |
| defensive_rebounds | int | Number of defensive rebounds |
| assists | int | Number of assists |
| steals | int | Number of steals |
| blocks | int | Number of blocks |
| turnovers | int | Number of turnovers |
| fouls | int | Number of personal fouls |
| points | int | Total points scored |
| season | int | Season year (e.g., 2023 for 2022-2023 season) |

## schedules.parquet

Contains scheduling information for all games.

| Column | Type | Description |
|--------|------|-------------|
| game_id | string | Unique identifier for the game |
| season | int | Season year (e.g., 2023 for 2022-2023 season) |
| season_type | string | Type of season (REGULAR, POSTSEASON) |
| game_date | date | Date of the game |
| game_time | string | Time of the game |
| neutral_site | boolean | Whether game was played at a neutral site |
| conference_game | boolean | Whether game was a conference matchup |
| tournament_type | string | Tournament type (NCAA, NIT, etc.) if applicable |
| tournament_round | string | Tournament round if applicable |
| home_team_id | string | ID of the home team |
| home_team_name | string | Name of the home team |
| home_team_score | int | Final score of the home team |
| away_team_id | string | ID of the away team |
| away_team_name | string | Name of the away team |
| away_team_score | int | Final score of the away team |
| venue_id | string | ID of the venue |
| venue_name | string | Name of the venue |
| venue_city | string | City of the venue |
| venue_state | string | State of the venue |

## team_box.parquet

Contains team-level box score statistics for each game.

| Column | Type | Description |
|--------|------|-------------|
| game_id | string | Unique identifier for the game |
| team_id | string | ID of the team |
| team_name | string | Name of the team |
| home_away | string | Whether team was home or away |
| field_goals_made | int | Number of field goals made |
| field_goals_attempted | int | Number of field goals attempted |
| field_goal_percentage | float | Field goal percentage (made/attempted) |
| three_point_made | int | Number of three-pointers made |
| three_point_attempted | int | Number of three-pointers attempted |
| three_point_percentage | float | Three-point percentage (made/attempted) |
| free_throws_made | int | Number of free throws made |
| free_throws_attempted | int | Number of free throws attempted |
| free_throw_percentage | float | Free throw percentage (made/attempted) |
| offensive_rebounds | int | Number of offensive rebounds |
| defensive_rebounds | int | Number of defensive rebounds |
| total_rebounds | int | Total rebounds (offensive + defensive) |
| assists | int | Number of assists |
| steals | int | Number of steals |
| blocks | int | Number of blocks |
| turnovers | int | Number of turnovers |
| fouls | int | Number of team fouls |
| points | int | Total points scored |
| opponent_id | string | ID of the opponent team |
| opponent_name | string | Name of the opponent team |
| season | int | Season year (e.g., 2023 for 2022-2023 season) |
| season_type | string | Type of season (REGULAR, POSTSEASON) |

## team_season_statistics.parquet

Contains aggregated team statistics for each season.

| Column | Type | Description |
|--------|------|-------------|
| team_id | string | Unique identifier for the team |
| team_name | string | Name of the team |
| season | int | Season year (e.g., 2023 for 2022-2023 season) |
| games_played | int | Number of games played |
| wins | int | Number of wins |
| losses | int | Number of losses |
| win_percentage | float | Win percentage (wins/games_played) |
| points_per_game | float | Average points scored per game |
| points_allowed_per_game | float | Average points allowed per game |
| field_goals_made_per_game | float | Average field goals made per game |
| field_goals_attempted_per_game | float | Average field goals attempted per game |
| field_goal_percentage | float | Season field goal percentage |
| three_point_made_per_game | float | Average three-pointers made per game |
| three_point_attempted_per_game | float | Average three-pointers attempted per game |
| three_point_percentage | float | Season three-point percentage |
| free_throws_made_per_game | float | Average free throws made per game |
| free_throws_attempted_per_game | float | Average free throws attempted per game |
| free_throw_percentage | float | Season free throw percentage |
| offensive_rebounds_per_game | float | Average offensive rebounds per game |
| defensive_rebounds_per_game | float | Average defensive rebounds per game |
| total_rebounds_per_game | float | Average total rebounds per game |
| assists_per_game | float | Average assists per game |
| steals_per_game | float | Average steals per game |
| blocks_per_game | float | Average blocks per game |
| turnovers_per_game | float | Average turnovers per game |
| fouls_per_game | float | Average fouls per game |

## Schema Validation

All datasets are validated against these schemas during the data processing stage. The validation ensures that:

1. Required columns are present
2. Data types are correct
3. Value ranges are within expected bounds

For details on the validation process, see the [Data Validation](validation.md) documentation. 