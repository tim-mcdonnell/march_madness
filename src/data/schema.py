"""
NCAA March Madness Data Schema and Validation

This module defines the schemas for the NCAA basketball data and provides
validation functions to ensure data quality and consistency.
"""

import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any

import polars as pl
from polars.exceptions import PolarsError

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Schema type enum (core vs optional columns)
class SchemaType(Enum):
    """Enum to differentiate between core and optional columns in schemas."""
    CORE = "core"
    OPTIONAL = "optional"

# Core schema columns (present in >90% of files)
# Define expected schemas for each data category
PLAY_BY_PLAY_SCHEMA = {
    SchemaType.CORE: {
        # Core columns (present in all files)
        'athlete_id_1': pl.Int32,
        'away_score': pl.Int32,
        'away_team_abbrev': pl.Utf8,
        'away_team_id': pl.Int32,
        'away_team_mascot': pl.Utf8,
        'away_team_name': pl.Utf8,
        'away_team_name_alt': pl.Utf8,
        'clock_display_value': pl.Utf8,
        'clock_minutes': [pl.Utf8, pl.Int32],  # Inconsistent type
        'clock_seconds': [pl.Utf8, pl.Int32],  # Inconsistent type
        'coordinate_x': pl.Float64,
        'coordinate_x_raw': pl.Float64,
        'coordinate_y': pl.Float64,
        'coordinate_y_raw': pl.Float64,
        'end_game_seconds_remaining': pl.Int32,
        'game_date': pl.Date,
        'game_date_time': pl.Datetime,
        'game_id': pl.Int32,
        'game_play_number': pl.Int32,
        'game_spread': pl.Float64,
        'game_spread_available': pl.Boolean,
        'half': [pl.Utf8, pl.Int32],  # Inconsistent type
        'home_favorite': pl.Boolean,
        'home_score': pl.Int32,
        'home_team_abbrev': pl.Utf8,
        'home_team_id': pl.Int32,
        'home_team_mascot': pl.Utf8,
        'home_team_name': pl.Utf8,
        'home_team_name_alt': pl.Utf8,
        'home_team_spread': pl.Float64,
        'id': pl.Float64,
        'period_display_value': pl.Utf8,
        'period_number': pl.Int32,
        'score_value': pl.Int32,
        'scoring_play': pl.Boolean,
        'season': pl.Int32,
        'season_type': pl.Int32,
        'sequence_number': [pl.Utf8, pl.Int32],  # Inconsistent type
        'shooting_play': pl.Boolean,
        'start_game_seconds_remaining': pl.Int32,
        'team_id': pl.Int32,
        'text': pl.Utf8,
        'time': pl.Utf8,
        'type_id': pl.Int32,
        'type_text': pl.Utf8,
    },
    SchemaType.OPTIONAL: {
        # Commonly present but not in all files
        'athlete_id_2': pl.Int32,  # Present in 95.2% of files
        # Present in 75-90% of files
        'end_half_seconds_remaining': pl.Int32,  # Present in 85.7% of files
        'end_quarter_seconds_remaining': pl.Int32,  # Present in 85.7% of files
        'game_half': pl.Utf8,  # Present in 85.7% of files
        'lag_game_half': pl.Utf8,  # Present in 85.7% of files
        'lag_qtr': pl.Int32,  # Present in 85.7% of files
        'lead_game_half': pl.Utf8,  # Present in 85.7% of files
        'lead_qtr': pl.Int32,  # Present in 85.7% of files
        'period': pl.Int32,  # Present in 85.7% of files
        'qtr': pl.Int32,  # Present in 85.7% of files
        'start_half_seconds_remaining': pl.Int32,  # Present in 85.7% of files
        'start_quarter_seconds_remaining': pl.Int32,  # Present in 85.7% of files
        # Less common columns
        'media_id': pl.Utf8,  # Present in 42.9% of files
        'wallclock': pl.Utf8,  # Present in 23.8% of files
        'away_timeout_called': pl.Boolean,  # Present in 14.3% of files
        'end_period_seconds_remaining': pl.Int32,  # Present in 14.3% of files
        'home_timeout_called': pl.Boolean,  # Present in 14.3% of files
        'lag_half': pl.Int32,  # Present in 14.3% of files
        'lag_period': pl.Int32,  # Present in 14.3% of files
        'lead_half': pl.Int32,  # Present in 14.3% of files
        'lead_period': pl.Int32,  # Present in 14.3% of files
        'start_period_seconds_remaining': pl.Int32,  # Present in 14.3% of files
    }
}

PLAYER_BOX_SCHEMA = {
    SchemaType.CORE: {
        # Core columns (present in all files)
        'active': pl.Boolean,
        'assists': pl.Int32,
        'athlete_display_name': pl.Utf8,
        'athlete_id': pl.Int32,
        'athlete_jersey': pl.Utf8,
        'athlete_position_abbreviation': pl.Utf8,
        'athlete_position_name': pl.Utf8,
        'athlete_short_name': pl.Utf8,
        'blocks': pl.Int32,
        'defensive_rebounds': pl.Int32,
        'did_not_play': pl.Boolean,
        'ejected': pl.Boolean,
        'field_goals_attempted': pl.Int32,
        'field_goals_made': pl.Int32,
        'fouls': pl.Int32,
        'free_throws_attempted': pl.Int32,
        'free_throws_made': pl.Int32,
        'game_date': pl.Date,
        'game_date_time': pl.Datetime,
        'game_id': pl.Int32,
        'home_away': pl.Utf8,
        'minutes': pl.Float64,
        'offensive_rebounds': pl.Int32,
        'opponent_team_abbreviation': pl.Utf8,
        'opponent_team_alternate_color': pl.Utf8,
        'opponent_team_color': pl.Utf8,
        'opponent_team_display_name': pl.Utf8,
        'opponent_team_id': pl.Int32,
        'opponent_team_location': pl.Utf8,
        'opponent_team_logo': pl.Utf8,
        'opponent_team_name': pl.Utf8,
        'opponent_team_score': pl.Int32,
        'points': pl.Int32,
        'rebounds': pl.Int32,
        'season': pl.Int32,
        'season_type': pl.Int32,
        'starter': pl.Boolean,
        'steals': pl.Int32,
        'team_abbreviation': pl.Utf8,
        'team_alternate_color': pl.Utf8,
        'team_color': pl.Utf8,
        'team_display_name': pl.Utf8,
        'team_id': pl.Int32,
        'team_location': pl.Utf8,
        'team_logo': pl.Utf8,
        'team_name': pl.Utf8,
        'team_score': pl.Int32,
        'team_short_display_name': pl.Utf8,
        'team_slug': pl.Utf8,
        'team_uid': pl.Utf8,
        'team_winner': pl.Boolean,
        'three_point_field_goals_attempted': pl.Int32,
        'three_point_field_goals_made': pl.Int32,
        'turnovers': pl.Int32,
    },
    SchemaType.OPTIONAL: {
        'athlete_headshot_href': pl.Utf8,  # Present in 56.5% of files
    }
}

SCHEDULES_SCHEMA = {
    SchemaType.CORE: {
        'PBP': pl.Boolean,
        'attendance': pl.Float64,
        'away_abbreviation': pl.String,
        'away_alternate_color': pl.String,
        'away_color': pl.String,
        'away_conference_id': pl.Int32,
        'away_display_name': pl.String,
        'away_id': pl.Int32,
        'away_is_active': pl.Boolean,
        'away_location': pl.String,
        'away_logo': pl.String,
        'away_name': pl.String,
        'away_score': pl.Int32,
        'away_short_display_name': pl.String,
        'away_uid': pl.String,
        'away_venue_id': pl.Int32,
        'away_winner': pl.Boolean,
        'conference_competition': pl.Boolean,
        'date': pl.String,
        'format_regulation_periods': pl.Float64,
        'game_date': pl.Date,
        'game_date_time': pl.Datetime(time_unit='us', time_zone='America/New_York'),
        'game_id': pl.Int32,
        'game_json': pl.Boolean,
        'game_json_url': pl.String,
        'groups_id': pl.Int32,
        'groups_is_conference': pl.Boolean,
        'groups_name': pl.String,
        'groups_short_name': pl.String,
        'home_abbreviation': pl.String,
        'home_alternate_color': pl.String,
        'home_color': pl.String,
        'home_conference_id': pl.Int32,
        'home_display_name': pl.String,
        'home_id': pl.Int32,
        'home_is_active': pl.Boolean,
        'home_location': pl.String,
        'home_logo': pl.String,
        'home_name': pl.String,
        'home_score': pl.Int32,
        'home_short_display_name': pl.String,
        'home_uid': pl.String,
        'home_venue_id': pl.Int32,
        'home_winner': pl.Boolean,
        'id': pl.Int32,
        'neutral_site': pl.Boolean,
        'notes_headline': pl.String,
        'notes_type': pl.String,
        'player_box': pl.Boolean,
        'recent': pl.Boolean,
        'season': pl.Int32,
        'season_type': pl.Int32,
        'start_date': pl.String,
        'status_clock': pl.Float64,
        'status_display_clock': pl.String,
        'status_period': pl.Float64,
        'status_type_alt_detail': pl.String,
        'status_type_completed': pl.Boolean,
        'status_type_description': pl.String,
        'status_type_detail': pl.String,
        'status_type_id': pl.Int32,
        'status_type_name': pl.String,
        'status_type_short_detail': pl.String,
        'status_type_state': pl.String,
        'team_box': pl.Boolean,
        'time_valid': pl.Boolean,
        'tournament_id': pl.Int32,
        'type_abbreviation': pl.String,
        'type_id': pl.Int32,
        'uid': pl.String,
        'venue_address_city': pl.String,
        'venue_address_state': pl.String,
        'venue_full_name': pl.String,
        'venue_id': pl.Int32,
        'venue_indoor': pl.Boolean,
    },
    SchemaType.OPTIONAL: {
        'away_current_rank': pl.Float64,
        'away_linescores': pl.String,
        'away_records': pl.String,
        'broadcast': pl.String,
        'broadcast_market': pl.String,
        'broadcast_name': pl.String,
        'highlights': pl.String,
        'home_current_rank': pl.Float64,
        'home_linescores': pl.String,
        'home_records': pl.String,
        'play_by_play_available': pl.Boolean,
        'venue_capacity': pl.Int32,  # Present in 91.3% of files
    }
}

TEAM_BOX_SCHEMA = {
    SchemaType.CORE: {
        'assists': pl.Int32,
        'blocks': pl.Int32,
        'defensive_rebounds': pl.Int32,
        'field_goal_pct': pl.Float64,
        'field_goals_attempted': pl.Int32,
        'field_goals_made': pl.Int32,
        'flagrant_fouls': pl.Int32,
        'fouls': pl.Int32,
        'free_throw_pct': pl.Float64,
        'free_throws_attempted': pl.Int32,
        'free_throws_made': pl.Int32,
        'game_date': pl.Date,
        'game_date_time': pl.Datetime(time_unit='us', time_zone='America/New_York'),
        'game_id': pl.Int32,
        'largest_lead': pl.String,
        'offensive_rebounds': pl.Int32,
        'season': pl.Int32,
        'season_type': pl.Int32,
        'steals': pl.Int32,
        'team_abbreviation': pl.String,
        'team_alternate_color': pl.String,
        'team_color': pl.String,
        'team_display_name': pl.String,
        'team_home_away': pl.String,
        'team_id': pl.Int32,
        'team_location': pl.String,
        'team_logo': pl.String,
        'team_name': pl.String,
        'team_score': pl.Int32,
        'team_short_display_name': pl.String,
        'team_slug': pl.String,
        'team_turnovers': pl.Int32,
        'team_uid': pl.String,
        'team_winner': pl.Boolean,
        'technical_fouls': pl.Int32,
        'three_point_field_goal_pct': pl.Float64,
        'three_point_field_goals_attempted': pl.Int32,
        'three_point_field_goals_made': pl.Int32,
        'total_rebounds': pl.Int32,
        'total_technical_fouls': pl.Int32,
        'total_turnovers': pl.Int32,
        'turnovers': pl.Int32,
        'opponent_team_abbreviation': pl.String,
        'opponent_team_alternate_color': pl.String,
        'opponent_team_color': pl.String,
        'opponent_team_display_name': pl.String,
        'opponent_team_id': pl.Int32,
        'opponent_team_location': pl.String,
        'opponent_team_logo': pl.String,
        'opponent_team_name': pl.String,
        'opponent_team_score': pl.Int32,
        'opponent_team_short_display_name': pl.String,
        'opponent_team_slug': pl.String,
        'opponent_team_uid': pl.String,
    },
    SchemaType.OPTIONAL: {
        'fast_break_points': pl.String,
        'points_in_paint': pl.String,
        'turnover_points': pl.String,
    }
}

# Map categories to schemas
SCHEMA_MAP = {
    'play_by_play': PLAY_BY_PLAY_SCHEMA,
    'player_box': PLAYER_BOX_SCHEMA,
    'schedules': SCHEDULES_SCHEMA,
    'team_box': TEAM_BOX_SCHEMA
}


def validate_schema(
    df: pl.DataFrame, 
    category: str, 
    strict_optional: bool = False
) -> tuple[bool, list[str]]:
    """
    Validate a DataFrame against the schema for a given category.
    
    Args:
        df: DataFrame to validate
        category: Data category name
        strict_optional: If True, optional columns are treated as required
        
    Returns:
        Tuple containing:
            - Boolean indicating if validation passed
            - List of error messages if validation failed
    """
    if category not in SCHEMA_MAP:
        return False, [f"Unknown category: {category}"]
    
    schema = SCHEMA_MAP[category]
    core_schema = schema[SchemaType.CORE]
    optional_schema = schema[SchemaType.OPTIONAL]
    
    errors = []
    
    # Check for required core columns
    df_columns = set(df.columns)
    core_columns = set(core_schema.keys())
    optional_columns = set(optional_schema.keys())
    
    # First check for missing required columns
    missing_columns = core_columns - df_columns
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
    
    # If strict_optional is True, check for missing optional columns
    if strict_optional:
        missing_optional = optional_columns - df_columns
        if missing_optional:
            errors.append(f"Missing optional columns (strict mode): {missing_optional}")
    
    # Check for unexpected columns
    unexpected_columns = df_columns - core_columns - optional_columns
    if unexpected_columns:
        # This is just a warning, not an error
        logger.warning(f"Unexpected columns in {category}: {unexpected_columns}")
    
    # Check column types for core columns
    for col in df_columns.intersection(core_columns):
        expected_type = core_schema[col]
        actual_type = df.schema[col]
        
        if not is_compatible_type(actual_type, expected_type):
            errors.append(
                f"Column '{col}' has incorrect type. "
                f"Expected {expected_type}, got {actual_type}"
            )
    
    # Then check optional columns if they exist
    for col in df_columns.intersection(optional_columns):
        expected_type = optional_schema[col]
        actual_type = df.schema[col]
        
        if not is_compatible_type(actual_type, expected_type):
            errors.append(
                f"Optional column '{col}' has incorrect type. "
                f"Expected {expected_type}, got {actual_type}"
            )
    
    return len(errors) == 0, errors


def is_compatible_type(
    actual_type: pl.DataType, 
    expected_type: pl.DataType | list[pl.DataType]
) -> bool:
    """
    Check if the actual data type is compatible with the expected type.
    
    Args:
        actual_type: Actual data type from the dataframe
        expected_type: Expected data type from the schema
        
    Returns:
        bool: True if the types are compatible, False otherwise
    """
    # If they're directly equal, return True
    if actual_type == expected_type:
        return True
    
    # Handle multiple accepted types
    if isinstance(expected_type, list):
        return any(is_compatible_type(actual_type, exp_type) for exp_type in expected_type)
    
    # Handle string/pl.DataType conversion
    if isinstance(expected_type, str):
        try:
            # Convert string representation to polars DataType
            expected_type = getattr(pl, expected_type)
        except (AttributeError, TypeError):
            return False  # Invalid data type string
    
    # Compatibility between numeric types
    numeric_types = {
        pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
        pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
        pl.Float32, pl.Float64
    }
                     
    if actual_type in numeric_types and expected_type in numeric_types:
        # Special case: if expected is float and actual is int, that's okay
        # Float when expecting int is not okay
        int_types = (
            pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64
        )
        float_types = (pl.Float32, pl.Float64)
        return not (isinstance(actual_type, float_types) and isinstance(expected_type, int_types))
    
    # Default case
    return False


def validate_file(
    file_path: str | Path, 
    category: str = None, 
    strict_optional: bool = False
) -> tuple[bool, list[str]]:
    """
    Validate a data file against its expected schema.
    
    Args:
        file_path: Path to the data file
        category: Data category. If None, will be inferred from the file path
        strict_optional: If True, treat optional columns as required
        
    Returns:
        Tuple containing:
            - Boolean indicating if validation passed
            - List of error messages if validation failed
    """
    file_path = Path(file_path)
    
    # Infer category from file path if not provided
    if category is None:
        file_name = file_path.name
        for cat in SCHEMA_MAP:
            if cat in file_name:
                category = cat
                break
        
        if category is None:
            return False, [f"Could not infer category from file name: {file_name}"]
    
    try:
        df = pl.read_parquet(file_path)
        return validate_schema(df, category, strict_optional=strict_optional)
    except PolarsError as e:
        return False, [f"Error reading file {file_path}: {e}"]
    except Exception as e:
        return False, [f"Unexpected error validating {file_path}: {e}"]


def validate_directory(
    directory_path: str | Path, 
    categories: list[str] = None, 
    years: list[int] = None, 
    strict_optional: bool = False
) -> dict[str, dict[str, Any]]:
    """
    Validate all data files in the specified directory and categories.
    
    Args:
        directory_path: Directory containing the data files
        categories: List of categories to validate. If None, all categories will be validated
        years: List of years to filter data files
        strict_optional: If True, treat optional columns as required
        
    Returns:
        Dictionary with validation results for each file
    """
    directory_path = Path(directory_path)
    
    if not categories:
        categories = list(SCHEMA_MAP.keys())
    
    results = {}
    
    for category in categories:
        category_dir = directory_path / category
        if not category_dir.exists():
            logger.warning(f"Category directory not found: {category_dir}")
            continue
        
        for file_path in category_dir.glob('*.parquet'):
            # Extract year from filename if years filter is provided
            year_match = re.search(r'_(\d{4})\.parquet$', file_path.name)
            year = int(year_match.group(1)) if year_match else None
            
            # Skip if years filter is provided and this file doesn't match
            if years and year and year not in years:
                continue
                
            # Use year-aware validation
            valid, errors = validate_with_year_awareness(
                file_path, 
                category, 
                strict_optional=strict_optional
            )
            
            results[str(file_path)] = {
                'valid': valid,
                'errors': errors,
                'category': category
            }
            
            if valid:
                logger.info(f"Validation passed: {file_path}")
            else:
                logger.error(f"Validation failed for {file_path}: {errors}")
    
    return results


def get_schema_summary() -> dict[str, dict[str, Any]]:
    """
    Generate a summary of schema definitions.
    
    Returns:
        Dictionary with summaries for each data category, including total columns and type counts
    """
    summary = {}
    
    for category, schema in SCHEMA_MAP.items():
        core_schema = schema[SchemaType.CORE]
        optional_schema = schema[SchemaType.OPTIONAL]
        
        # Count total columns
        total_columns = len(core_schema) + len(optional_schema)
        
        # Count types
        type_counts = {}
        
        for col_type in list(core_schema.values()) + list(optional_schema.values()):
            type_name = str(col_type)
            if type_name not in type_counts:
                type_counts[type_name] = 0
            type_counts[type_name] += 1
        
        summary[category] = {
            'total_columns': total_columns,
            'core_columns': len(core_schema),
            'optional_columns': len(optional_schema),
            'type_counts': type_counts
        }
    
    return summary


def validate_with_year_awareness(
    file_path: str | Path,
    category: str = None,
    strict_optional: bool = False
) -> tuple[bool, list[str]]:
    """
    Validate a file with year-aware schema adjustments.
    
    This function extracts the year from the filename and applies different
    validation rules based on recency:
    - For recent years (2023+), certain historically required columns that are 
      now missing from the data source are treated as optional
    - For older years, the standard schema validation is applied
    
    Args:
        file_path: Path to the file to validate
        category: Data category (play_by_play, schedules, etc.)
        strict_optional: Whether to strictly validate optional columns
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    file_path = Path(file_path)
    
    # Extract year from filename
    # Pattern matching for different filename formats
    year = None
    filename = file_path.name
    
    # Try to extract year from filename
    if 'schedule' in filename and filename.endswith('.parquet'):
        year_match = re.search(r'_(\d{4})\.parquet$', filename)
        if year_match:
            year = int(year_match.group(1))
    elif filename.endswith('.parquet'):
        # Format: play_by_play_2024.parquet, team_box_2024.parquet, etc.
        year_match = re.search(r'_(\d{4})\.parquet$', filename)
        if year_match:
            year = int(year_match.group(1))
    
    # If we couldn't extract a year or category is not provided, fall back to standard validation
    if year is None or category is None:
        return validate_file(file_path, category, strict_optional)
    
    # For recent years, adjust schema expectations
    if year >= 2023:
        # Read the file
        try:
            df = pl.read_parquet(file_path)
            
            # Get schema for the category
            if category not in SCHEMA_MAP:
                return False, [f"Unknown category: {category}"]
            
            schema = SCHEMA_MAP[category]
            core_schema = schema[SchemaType.CORE]
            optional_schema = schema[SchemaType.OPTIONAL]
            
            errors = []
            
            # Year-specific adjustments
            year_specific_optional = []
            if category == 'schedules' and year >= 2023:
                # venue_capacity is now optional for recent schedules
                year_specific_optional.append('venue_capacity')
            elif category == 'play_by_play' and year >= 2023:
                # athlete_id_2 is now optional for recent play-by-play data
                year_specific_optional.append('athlete_id_2')
            
            # Validate core columns with year-specific exceptions
            df_columns = set(df.columns)
            for col_name, expected_type in core_schema.items():
                if col_name in year_specific_optional:
                    # Skip validation for columns that are now optional for recent years
                    continue
                
                if col_name not in df_columns:
                    errors.append(f"Missing required column: {col_name}")
                    continue
                
                actual_type = df.schema[col_name]
                if not is_compatible_type(actual_type, expected_type):
                    errors.append(
                        f"Type mismatch for column {col_name}: "
                        f"expected {expected_type}, got {actual_type}"
                    )
            
            # Validate optional columns if strict_optional is True
            if strict_optional:
                for col_name, expected_type in optional_schema.items():
                    if col_name in df_columns:
                        actual_type = df.schema[col_name]
                        if not is_compatible_type(actual_type, expected_type):
                            errors.append(
                                f"Type mismatch for optional column {col_name}: "
                                f"expected {expected_type}, got {actual_type}"
                            )
            
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except pl.exceptions.ComputeError as e:
            return False, [f"Error computing data in {file_path}: {e}"]
        except Exception as e:
            return False, [f"Unexpected error validating {file_path}: {e}"]
    else:
        # For older years, use standard validation
        return validate_file(file_path, category, strict_optional)


if __name__ == "__main__":
    
    summary = get_schema_summary()
    for _category, info in summary.items():
        for _type_name, _count in info['type_counts'].items():
            pass 