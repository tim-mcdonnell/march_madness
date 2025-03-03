"""
Unit tests for schema validation.
"""

from pathlib import Path

import polars as pl
import pytest

from src.data.schema import SCHEMA_MAP, SchemaType, validate_file, validate_schema
from src.data.validation import (
    generate_validation_report,
    validate_dataframe,
    validate_raw_data,
)


@pytest.fixture
def sample_data() -> list[pl.DataFrame]:
    """Create sample data for testing."""
    # Create a sample play-by-play dataframe
    play_by_play_data = {
        'id': [1.0, 2.0, 3.0],
        'game_id': [401234, 401235, 401236],
        'sequence_number': [1, 2, 3],
        'type_id': [1, 2, 3],
        'type_text': ['Shot', 'Foul', 'Timeout'],
        'text': ['Shot made', 'Foul', 'Timeout'],
        'score_value': [2, 0, 0],
        'home_score': [2, 2, 2],
        'away_score': [0, 0, 0],
        'period': [1, 1, 1],
        'period_number': [1, 1, 1],
        'period_display_value': ['1st', '1st', '1st'],
        'clock_display_value': ['19:45', '19:30', '19:15'],
        'clock_minutes': [19, 19, 19],
        'clock_seconds': [45, 30, 15],
        'team_id': [123, 456, 123],
        'team_name': ['Team A', 'Team B', 'Team A'],
        'team_location': ['Home', 'Away', 'Home'],
        'team_abbreviation': ['TA', 'TB', 'TA'],
        'team_color': ['#FF0000', '#0000FF', '#FF0000'],
        'team_logo_url': ['http://example.com/logo1', 'http://example.com/logo2', 'http://example.com/logo1'],
        'away_team_id': [456, 456, 456],
        'away_team_name': ['Team B', 'Team B', 'Team B'],
        'away_team_location': ['Away', 'Away', 'Away'],
        'away_team_abbreviation': ['TB', 'TB', 'TB'],
        'away_team_abbrev': ['TB', 'TB', 'TB'],
        'away_team_mascot': ['Bears', 'Bears', 'Bears'],
        'away_team_name_alt': ['Team B Alt', 'Team B Alt', 'Team B Alt'],
        'away_team_color': ['#0000FF', '#0000FF', '#0000FF'],
        'away_team_logo_url': [
            'http://example.com/logo2',
            'http://example.com/logo2',
            'http://example.com/logo2'
        ],
        'home_team_id': [123, 123, 123],
        'home_team_name': ['Team A', 'Team A', 'Team A'],
        'home_team_location': ['Home', 'Home', 'Home'],
        'home_team_abbreviation': ['TA', 'TA', 'TA'],
        'home_team_abbrev': ['TA', 'TA', 'TA'],
        'home_team_mascot': ['Tigers', 'Tigers', 'Tigers'],
        'home_team_name_alt': ['Team A Alt', 'Team A Alt', 'Team A Alt'],
        'home_team_color': ['#FF0000', '#FF0000', '#FF0000'],
        'home_team_logo_url': [
            'http://example.com/logo1',
            'http://example.com/logo1',
            'http://example.com/logo1'
        ],
        'season': [2023, 2023, 2023],
        'season_type': [1, 1, 1],
        'athlete_id_1': [1001, 1002, 1003],
        'athlete_id_2': [2001, 2002, 2003],
        'coordinate_x': [25.5, 30.2, None],
        'coordinate_y': [15.3, 20.1, None],
        'coordinate_x_raw': [25.5, 30.2, None],
        'coordinate_y_raw': [15.3, 20.1, None],
        'team_score': [2, 0, 0],
        'opponent_score': [0, 2, 2],
        'game_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'game_date_time': [
            '2023-01-01 19:00:00',
            '2023-01-02 19:00:00',
            '2023-01-03 19:00:00'
        ],
        'scoring_play': [True, False, False],
        'score_change': [2, 0, 0],
        'timestamp': [1672531200, 1672532100, 1672533000],
        'wall_clock': ['19:00', '19:15', '19:30'],
        'shot_type_text': ['Layup', None, None],
        'time': ['19:45', '19:30', '19:15'],
        'half': [1, 1, 1],
        'game_play_number': [1, 2, 3],
        'shooting_play': [True, False, False],
        'home_favorite': [True, True, True],
        'home_team_spread': [-5.5, -5.5, -5.5],
        'game_spread': [5.5, 5.5, 5.5],
        'game_spread_available': [True, True, True],
        'start_game_seconds_remaining': [2400, 2385, 2370],
        'end_game_seconds_remaining': [2385, 2370, 2355],
    }
    valid_play_by_play_df = pl.DataFrame(play_by_play_data)
    # Convert string dates to proper date types
    valid_play_by_play_df = valid_play_by_play_df.with_columns([
        pl.col('game_date').str.to_date(),
        pl.col('game_date_time').str.to_datetime()
    ])

    # Create a sample player box dataframe
    player_box_data = {
        'game_id': [401234, 401235, 401236],
        'team_id': [123, 456, 123],
        'athlete_id': [1001, 1002, 1003],
        'active': [True, True, False],
        'did_not_play': [False, False, True],
        'reason': [None, None, 'Injury'],
        'ejected': [False, False, False],
        'points': [10, 8, 0],
        'field_goals_made': [4, 3, 0],
        'field_goals_attempted': [8, 7, 0],
        'field_goal_pct': [0.5, 0.429, None],
        'three_point_field_goals_made': [2, 1, 0],
        'three_point_field_goals_attempted': [4, 3, 0],
        'three_point_field_goal_pct': [0.5, 0.333, None],
        'free_throws_made': [0, 1, 0],
        'free_throws_attempted': [0, 2, 0],
        'free_throw_pct': [None, 0.5, None],
        'rebounds_offensive': [1, 2, 0],
        'rebounds_defensive': [3, 2, 0],
        'rebounds_total': [4, 4, 0],
        'assists': [2, 1, 0],
        'steals': [1, 0, 0],
        'blocks': [0, 1, 0],
        'turnovers': [1, 2, 0],
        'fouls': [2, 3, 0],
        'plus_minus': [5, -3, 0],
        'minutes': ['25:30', '22:15', '00:00'],
        'position': ['G', 'F', 'C'],
        'athlete_display_name': ['Player A', 'Player B', 'Player C'],
        'athlete_short_name': ['A. Player', 'B. Player', 'C. Player'],
        'athlete_jersey': ['1', '2', '3'],
        'athlete_position_name': ['Guard', 'Forward', 'Center'],
        'athlete_position_abbreviation': ['G', 'F', 'C'],
        'athlete_headshot_href': [
            'http://example.com/headshot1',
            'http://example.com/headshot2',
            'http://example.com/headshot3'
        ],
        'team_display_name': ['Team A', 'Team B', 'Team A'],
        'team_abbreviation': ['TA', 'TB', 'TA'],
        'team_color': ['#FF0000', '#0000FF', '#FF0000'],
        'team_alternate_color': ['#FFFFFF', '#FFFFFF', '#FFFFFF'],
        'team_logo': [
            'http://example.com/logo1',
            'http://example.com/logo2',
            'http://example.com/logo1'
        ],
        'team_location': ['Home', 'Away', 'Home'],
        'team_name': ['Team A', 'Team B', 'Team A'],
        'team_short_display_name': ['TA', 'TB', 'TA'],
        'team_slug': ['team-a', 'team-b', 'team-a'],
        'team_uid': ['team123', 'team456', 'team123'],
        'team_winner': [True, False, True],
        'team_score': [75, 68, 82],
        'home_away': ['home', 'away', 'home'],
        'opponent_team_id': [456, 123, 789],
        'opponent_team_display_name': ['Team B', 'Team A', 'Team C'],
        'opponent_team_abbreviation': ['TB', 'TA', 'TC'],
        'opponent_team_location': ['Away', 'Home', 'Away'],
        'opponent_team_color': ['#0000FF', '#FF0000', '#00FF00'],
        'opponent_team_alternate_color': ['#FFFFFF', '#FFFFFF', '#FFFFFF'],
        'opponent_team_logo': [
            'http://example.com/logo2',
            'http://example.com/logo1',
            'http://example.com/logo3'
        ],
        'opponent_team_name': ['Team B', 'Team A', 'Team C'],
        'opponent_team_score': [68, 75, 75],
        'starter': [True, True, False],
        'rebounds': [4, 4, 0],
        'defensive_rebounds': [3, 2, 0],
        'offensive_rebounds': [1, 2, 0],
        'season': [2023, 2023, 2023],
        'season_type': [1, 1, 1],
        'game_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'game_date_time': [
            '2023-01-01 19:00:00',
            '2023-01-02 19:00:00',
            '2023-01-03 19:00:00'
        ],
    }
    valid_player_box_df = pl.DataFrame(player_box_data)
    # Convert string dates to proper date types
    valid_player_box_df = valid_player_box_df.with_columns([
        pl.col('game_date').str.to_date(),
        pl.col('game_date_time').str.to_datetime()
    ])

    # Create a sample schedules dataframe
    schedules_data = {
        'game_id': [401234, 401235, 401236],
        'season': [2023, 2023, 2023],
        'season_type': [1, 1, 1],
        'game_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'game_date_time': [
            '2023-01-01 19:00:00',
            '2023-01-02 19:00:00',
            '2023-01-03 19:00:00'
        ],
        'home_id': [123, 789, 123],
        'home_name': ['Team A', 'Team C', 'Team A'],
        'home_abbreviation': ['TA', 'TC', 'TA'],
        'home_location': ['Home', 'Home', 'Home'],
        'home_color': ['#FF0000', '#00FF00', '#FF0000'],
        'home_alternate_color': ['#FFFFFF', '#FFFFFF', '#FFFFFF'],
        'home_logo': [
            'http://example.com/logo1',
            'http://example.com/logo3',
            'http://example.com/logo1'
        ],
        'home_score': [75, 68, 82],
        'home_winner': [True, False, True],
        'home_conference_id': [1, 2, 1],
        'home_is_active': [True, True, True],
        'home_short_display_name': ['TA', 'TC', 'TA'],
        'home_uid': ['team123', 'team789', 'team123'],
        'home_venue_id': [1, 2, 1],
        'home_display_name': ['Team A', 'Team C', 'Team A'],
        'away_id': [456, 123, 789],
        'away_name': ['Team B', 'Team A', 'Team C'],
        'away_abbreviation': ['TB', 'TA', 'TC'],
        'away_location': ['Away', 'Away', 'Away'],
        'away_color': ['#0000FF', '#FF0000', '#00FF00'],
        'away_alternate_color': ['#FFFFFF', '#FFFFFF', '#FFFFFF'],
        'away_logo': [
            'http://example.com/logo2',
            'http://example.com/logo1',
            'http://example.com/logo3'
        ],
        'away_score': [68, 72, 75],
        'away_winner': [False, True, False],
        'away_conference_id': [2, 1, 2],
        'away_is_active': [True, True, True],
        'away_short_display_name': ['TB', 'TA', 'TC'],
        'away_uid': ['team456', 'team123', 'team789'],
        'away_venue_id': [2, 1, 2],
        'away_display_name': ['Team B', 'Team A', 'Team C'],
        'status_type_id': [3, 3, 3],
        'status_type_name': ['STATUS_FINAL', 'STATUS_FINAL', 'STATUS_FINAL'],
        'status_type_state': ['post', 'post', 'post'],
        'status_type_completed': [True, True, True],
        'status_type_description': ['Final', 'Final', 'Final'],
        'status_type_detail': ['Final', 'Final', 'Final'],
        'status_type_short_detail': ['Final', 'Final', 'Final'],
        'status_type_alt_detail': ['Final', 'Final', 'Final'],
        'status_clock': [0.0, 0.0, 0.0],
        'status_display_clock': ['0:00', '0:00', '0:00'],
        'status_period': [2.0, 2.0, 2.0],
        'venue_id': [1, 2, 1],
        'venue_full_name': ['Arena 1', 'Arena 2', 'Arena 1'],
        'venue_address_city': ['City A', 'City B', 'City A'],
        'venue_address_state': ['State A', 'State B', 'State A'],
        'venue_capacity': [15000.0, 12000.0, 16000.0],
        'venue_indoor': [True, True, True],
        'conference_competition': [True, False, True],
        'neutral_site': [False, True, False],
        'attendance': [15000.0, 12000.0, 16000.0],
        'id': [401234, 401235, 401236],
        'uid': ['s:40~l:41~e:401234', 's:40~l:41~e:401235', 's:40~l:41~e:401236'],
        'date': ['2023-01-01T19:00Z', '2023-01-02T19:00Z', '2023-01-03T19:00Z'],
        'start_date': ['2023-01-01T19:00Z', '2023-01-02T19:00Z', '2023-01-03T19:00Z'],
        'time_valid': [True, True, True],
        'recent': [False, False, True],
        'type_id': [1, 1, 1],
        'type_abbreviation': ['REG', 'REG', 'REG'],
        'format_regulation_periods': [2.0, 2.0, 2.0],
        'groups_id': [1, 1, 1],
        'groups_name': ['NCAA', 'NCAA', 'NCAA'],
        'groups_short_name': ['NCAA', 'NCAA', 'NCAA'],
        'groups_is_conference': [False, False, False],
        'tournament_id': [1, 1, 1],
        'notes_headline': ['', '', ''],
        'notes_type': ['', '', ''],
        'player_box': [True, True, True],
        'team_box': [True, True, True],
        'PBP': [True, True, True],
        'game_json': [True, True, True],
        'game_json_url': [
            'http://example.com/json1',
            'http://example.com/json2',
            'http://example.com/json3'
        ],
    }
    valid_schedules_df = pl.DataFrame(schedules_data)
    # Convert string dates to proper date types
    valid_schedules_df = valid_schedules_df.with_columns([
        pl.col('game_date').str.to_date(),
        pl.col('game_date_time').str.to_datetime()
    ])

    # Create a sample team box dataframe
    team_box_data = {
        'game_id': [401234, 401235, 401236],
        'team_id': [123, 456, 123],
        'team_uid': ['team123', 'team456', 'team123'],
        'team_slug': ['team-a', 'team-b', 'team-a'],
        'team_location': ['Home', 'Away', 'Home'],
        'team_name': ['Team A', 'Team B', 'Team A'],
        'team_abbreviation': ['TA', 'TB', 'TA'],
        'team_display_name': ['Team A', 'Team B', 'Team A'],
        'team_short_display_name': ['TA', 'TB', 'TA'],
        'team_color': ['#FF0000', '#0000FF', '#FF0000'],
        'team_alternate_color': ['#FFFFFF', '#FFFFFF', '#FFFFFF'],
        'team_logo': [
            'http://example.com/logo1',
            'http://example.com/logo2',
            'http://example.com/logo1'
        ],
        'points': [75, 68, 82],
        'field_goals_made': [28, 25, 30],
        'field_goals_attempted': [60, 58, 65],
        'field_goal_pct': [0.467, 0.431, 0.462],
        'three_point_field_goals_made': [10, 8, 12],
        'three_point_field_goals_attempted': [25, 22, 28],
        'three_point_field_goal_pct': [0.4, 0.364, 0.429],
        'free_throws_made': [9, 10, 10],
        'free_throws_attempted': [12, 15, 14],
        'free_throw_pct': [0.75, 0.667, 0.714],
        'rebounds_offensive': [12, 10, 14],
        'rebounds_defensive': [25, 22, 26],
        'total_rebounds': [37, 32, 40],
        'assists': [15, 12, 18],
        'steals': [8, 6, 9],
        'blocks': [5, 3, 6],
        'turnovers': [12, 15, 10],
        'team_turnovers': [2, 3, 1],
        'total_turnovers': [14, 18, 11],
        'fouls': [18, 15, 16],
        'largest_lead': ['12', '8', '15'],
        'technical_fouls': [0, 1, 0],
        'flagrant_fouls': [0, 0, 0],
        'total_technical_fouls': [0, 1, 0],
        'team_home_away': ['home', 'away', 'home'],
        'team_winner': [True, False, True],
        'team_score': [75, 68, 82],
        'opponent_team_id': [456, 123, 789],
        'opponent_team_abbreviation': ['TB', 'TA', 'TC'],
        'opponent_team_location': ['Away', 'Home', 'Away'],
        'opponent_team_display_name': ['Team B', 'Team A', 'Team C'],
        'opponent_team_color': ['#0000FF', '#FF0000', '#00FF00'],
        'opponent_team_alternate_color': ['#FFFFFF', '#FFFFFF', '#FFFFFF'],
        'opponent_team_logo': [
            'http://example.com/logo2',
            'http://example.com/logo1',
            'http://example.com/logo3'
        ],
        'opponent_team_name': ['Team B', 'Team A', 'Team C'],
        'opponent_team_score': [68, 75, 75],
        'opponent_team_uid': ['team456', 'team123', 'team789'],
        'opponent_team_slug': ['team-b', 'team-a', 'team-c'],
        'opponent_team_short_display_name': ['TB', 'TA', 'TC'],
        'season': [2023, 2023, 2023],
        'season_type': [1, 1, 1],
        'game_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'game_date_time': [
            '2023-01-01 19:00:00',
            '2023-01-02 19:00:00',
            '2023-01-03 19:00:00'
        ],
    }
    valid_team_box_df = pl.DataFrame(team_box_data)
    # Convert string dates to proper date types
    valid_team_box_df = valid_team_box_df.with_columns([
        pl.col('game_date').str.to_date(),
        pl.col('game_date_time').str.to_datetime()
    ])

    return [valid_play_by_play_df, valid_player_box_df, valid_schedules_df, valid_team_box_df]


@pytest.fixture
def sample_data_path(tmp_path: Path) -> Path:
    """Create a temporary directory structure for sample data."""
    # Create directories for each data category
    for category in ['play_by_play', 'player_box', 'schedules', 'team_box']:
        (tmp_path / category).mkdir(exist_ok=True)
    return tmp_path


def test_schema_definitions() -> None:
    """Test that schema definitions exist and have the expected structure."""
    # Check that all schema categories exist
    assert 'play_by_play' in SCHEMA_MAP
    assert 'player_box' in SCHEMA_MAP
    assert 'schedules' in SCHEMA_MAP
    assert 'team_box' in SCHEMA_MAP
    
    # Check that each category has core and optional schemas
    for category in SCHEMA_MAP:
        assert SchemaType.CORE in SCHEMA_MAP[category]
        assert SchemaType.OPTIONAL in SCHEMA_MAP[category]
        
        # Check that core schema is not empty
        assert len(SCHEMA_MAP[category][SchemaType.CORE]) > 0


def test_validate_schema(valid_play_by_play_df: pl.DataFrame) -> None:
    """Test schema validation function."""
    # Validate valid dataframe
    valid, errors = validate_schema(valid_play_by_play_df, 'play_by_play')
    assert valid, f"Schema validation should pass: {errors}"
    assert not errors, "There should be no errors for valid schema"


def test_validate_schema_core_only(valid_play_by_play_df: pl.DataFrame) -> None:
    """Test schema validation with only core columns."""
    # Keep only core columns
    core_cols = list(SCHEMA_MAP['play_by_play'][SchemaType.CORE].keys())
    # Get only the core columns that exist in the dataframe
    available_core_cols = [col for col in core_cols if col in valid_play_by_play_df.columns]
    core_only_df = valid_play_by_play_df.select(available_core_cols)
    
    # Validate with core columns only (should pass)
    valid, errors = validate_schema(core_only_df, 'play_by_play', strict_optional=False)
    assert valid, f"Validation should pass with core columns only: {errors}"
    assert not errors, "There should be no errors for core-only schema"


def test_validate_schema_with_optional(valid_play_by_play_df: pl.DataFrame) -> None:
    """Test schema validation with some optional columns."""
    # Validate with some optional columns (should pass)
    valid, errors = validate_schema(
        valid_play_by_play_df, 'play_by_play', strict_optional=False
    )
    assert valid, f"Validation should pass with optional columns: {errors}"
    assert not errors, "There should be no errors for schema with optional columns"


def test_validate_schema_missing_core(valid_play_by_play_df: pl.DataFrame) -> None:
    """Test schema validation with missing core columns."""
    # Create a dataframe with a missing core column
    core_cols = list(SCHEMA_MAP['play_by_play'][SchemaType.CORE].keys())
    missing_col = core_cols[0]  # Remove the first core column
    remaining_cols = [
        col for col in valid_play_by_play_df.columns if col != missing_col
    ]
    missing_core_df = valid_play_by_play_df.select(remaining_cols)
    
    # Validate with missing core column (should fail)
    valid, errors = validate_schema(missing_core_df, 'play_by_play')
    assert not valid, "Validation should fail with missing core column"
    assert any(
        missing_col in str(err) for err in errors
    ), f"Error should mention missing column {missing_col}"


def test_validate_schema_wrong_type(valid_play_by_play_df: pl.DataFrame) -> None:
    """Test schema validation with wrong column types."""
    # Create a dataframe with wrong type for a column
    wrong_type_data = valid_play_by_play_df.to_dict(as_series=False)
    # Convert id to string - this is a core column that should be a float
    wrong_type_data['id'] = ['1', '2', '3']  # Should be float, not string
    df_wrong_type = pl.DataFrame(wrong_type_data)
    
    # Validate with wrong column type (should fail)
    valid, errors = validate_schema(df_wrong_type, 'play_by_play')
    assert not valid, "Validation should fail with wrong column type"
    assert any(
        "Column 'id' has incorrect type" in error for error in errors
    ), f"Error message should mention wrong type for 'id' column. Errors: {errors}"


def test_validate_file(
    sample_data_path: Path, valid_play_by_play_df: pl.DataFrame
) -> None:
    """Test file validation."""
    # Write a valid file
    file_path = sample_data_path / 'play_by_play' / 'play_by_play_2023.parquet'
    valid_play_by_play_df.write_parquet(file_path)
    
    # Validate the file (should pass)
    valid, errors = validate_file(file_path)
    assert valid, f"File validation should pass: {errors}"
    assert not errors, "There should be no errors for valid file"


def test_validate_raw_data(
    sample_data_path: Path, 
    valid_play_by_play_df: pl.DataFrame, 
    valid_team_box_df: pl.DataFrame
) -> None:
    """Test raw data validation."""
    # Write sample files
    file_path_pbp = sample_data_path / 'play_by_play' / 'play_by_play_2023.parquet'
    valid_play_by_play_df.write_parquet(file_path_pbp)
    
    file_path_team = sample_data_path / 'team_box' / 'team_box_2023.parquet'
    valid_team_box_df.write_parquet(file_path_team)
    
    # Validate raw data (should pass)
    results = validate_raw_data(sample_data_path)
    assert all(
        result[0] for result in results
    ), f"Raw data validation should pass: {results}"


def test_validate_dataframe(valid_play_by_play_df: pl.DataFrame) -> None:
    """Test dataframe validation function."""
    # Validate valid dataframe
    valid, errors = validate_dataframe(valid_play_by_play_df, 'play_by_play')
    assert valid, f"Dataframe validation should pass: {errors}"
    assert not errors, "There should be no errors for valid dataframe"


def test_generate_validation_report(
    sample_data_path: Path, valid_play_by_play_df: pl.DataFrame
) -> None:
    """Test validation report generation."""
    # Write sample files
    file_path = sample_data_path / 'play_by_play' / 'play_by_play_2023.parquet'
    valid_play_by_play_df.write_parquet(file_path)
    
    # Validate data to get results
    validation_results = validate_raw_data(sample_data_path)
    
    # Generate report
    report = generate_validation_report(validation_results)
    
    # Check report structure
    assert isinstance(report, str), "Report should be a string"
    assert "NCAA March Madness Data Validation Report" in report, "Report should have a title"
    assert "Schema Summary" in report, "Report should have a schema summary section"
    assert "Validation Results" in report, "Report should have validation results section"


@pytest.fixture
def valid_play_by_play_df(sample_data: list[pl.DataFrame]) -> pl.DataFrame:
    """Return a valid play-by-play dataframe for testing."""
    return sample_data[0]


@pytest.fixture
def valid_player_box_df(sample_data: list[pl.DataFrame]) -> pl.DataFrame:
    """Return a valid player box dataframe for testing."""
    return sample_data[1]


@pytest.fixture
def valid_schedules_df(sample_data: list[pl.DataFrame]) -> pl.DataFrame:
    """Return a valid schedules dataframe for testing."""
    return sample_data[2]


@pytest.fixture
def valid_team_box_df(sample_data: list[pl.DataFrame]) -> pl.DataFrame:
    """Return a valid team box dataframe for testing."""
    return sample_data[3]


if __name__ == "__main__":
    # Run the tests manually
    test_schema_definitions()
    sample_data = sample_data()
    test_validate_schema(sample_data[0])
    test_validate_dataframe(sample_data[0])
    test_validate_raw_data(sample_data[0], sample_data[0], sample_data[3])
