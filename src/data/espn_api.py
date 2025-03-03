"""
ESPN API integration for NCAA basketball team data.

This module provides functions for fetching and processing team data from the ESPN API
to use as a source of truth for team name standardization.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ESPN API endpoints
TEAMS_API_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams"
TEAM_API_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{team_id}"

# Static data file paths
STATIC_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "static"
TEAMS_STATIC_FILE = STATIC_DATA_DIR / "espn_teams.json"


def get_all_teams() -> list[dict[str, Any]]:
    """
    Get all NCAA basketball teams from the static data file.
    
    Returns:
        List of team data dictionaries
    """
    try:
        # Check if the static file exists
        if not TEAMS_STATIC_FILE.exists():
            logger.warning(f"Static teams data file not found: {TEAMS_STATIC_FILE}")
            return []
            
        # Load data from the static file
        with open(TEAMS_STATIC_FILE) as f:
            logger.info(f"Loading ESPN team data from static file: {TEAMS_STATIC_FILE}")
            data = json.load(f)
            return extract_team_data(data)
            
    except Exception as e:
        logger.error(f"Failed to load ESPN team data from static file: {e}")
        return []


def extract_team_data(api_response: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract relevant team data from the ESPN API response.
    
    Args:
        api_response: Raw ESPN API response
        
    Returns:
        List of processed team data dictionaries
    """
    teams = []
    
    try:
        # Navigate through the nested structure to get to teams
        sports = api_response.get('sports', [])
        if not sports:
            logger.error("No sports data found in ESPN API response")
            return teams
            
        leagues = sports[0].get('leagues', [])
        if not leagues:
            logger.error("No leagues data found in ESPN API response")
            return teams
            
        teams_data = leagues[0].get('teams', [])
        if not teams_data:
            logger.error("No teams data found in ESPN API response")
            return teams
        
        # Process each team
        for team_entry in teams_data:
            team_info = team_entry.get('team', {})
            if not team_info:
                continue
                
            # Extract the key information we need
            team = {
                'id': team_info.get('id'),
                'espn_id': team_info.get('id'),  # For clarity when using multiple sources
                'abbreviation': team_info.get('abbreviation'),
                'display_name': team_info.get('displayName'),
                'short_name': team_info.get('shortDisplayName'),
                'mascot': team_info.get('name'),
                'location': team_info.get('location'),
                'color': team_info.get('color'),
                'alternate_color': team_info.get('alternateColor'),
                'name_variants': []
            }
            
            # Create a list of name variants for matching
            name_variants = [
                team_info.get('displayName'),
                team_info.get('shortDisplayName'),
                team_info.get('location')
            ]
            
            # Add nickname as "{location} {mascot}"
            location = team_info.get('location')
            mascot = team_info.get('name')
            if location and mascot:
                name_variants.append(f"{location} {mascot}")
            
            # Also add just the location name (e.g., "Duke")
            if location:
                name_variants.append(location)
                
            # Filter out None values and duplicates
            team['name_variants'] = list(set([v for v in name_variants if v]))
            
            teams.append(team)
        
        logger.info(f"Processed {len(teams)} teams from ESPN data")
        return teams
        
    except Exception as e:
        logger.error(f"Error extracting team data from ESPN data: {e}")
        return teams


def get_team_name_mapping() -> dict[str, str]:
    """
    Generate a mapping of all team name variants to canonical names.
    
    Returns:
        Dictionary mapping variant names to canonical (display) names
    """
    teams = get_all_teams()
    
    # If static data file is empty or not found, use mock data for testing
    if not teams:
        logger.warning("No teams found in static data, using mock data for testing")
        return get_mock_team_name_mapping()
    
    name_map = {}
    
    for team in teams:
        canonical_name = team['display_name']
        
        # Map all variants to the canonical name
        for variant in team['name_variants']:
            name_map[variant] = canonical_name
            
        # Map abbreviation to canonical name
        if team['abbreviation']:
            name_map[team['abbreviation']] = canonical_name
    
    logger.info(f"Generated team name mapping with {len(name_map)} entries")
    return name_map


def get_team_by_abbreviation(abbrev: str) -> dict[str, Any] | None:
    """
    Find a team by its abbreviation.
    
    Args:
        abbrev: Team abbreviation (e.g., 'DUKE')
        
    Returns:
        Team data dictionary or None if not found
    """
    teams = get_all_teams()
    
    # If static data file is empty or not found, use mock data for testing
    if not teams:
        logger.warning("No teams found in static data, using mock data for testing")
        return get_mock_team_by_abbreviation(abbrev)
    
    for team in teams:
        if team['abbreviation'] == abbrev:
            return team
    
    return None


def get_team_by_name(name: str) -> dict[str, Any] | None:
    """
    Find a team by any of its name variants.
    
    Args:
        name: Team name to search for
        
    Returns:
        Team data dictionary or None if not found
    """
    teams = get_all_teams()
    
    # If static data is empty, use mock data for testing
    if not teams:
        logger.warning("No teams found in static data, using mock data for testing")
        return get_mock_team_by_name(name)
    
    name_lower = name.lower()
    
    for team in teams:
        # Check all variants
        for variant in team['name_variants']:
            if variant and variant.lower() == name_lower:
                return team
                
        # Check abbreviation
        if team['abbreviation'] and team['abbreviation'].lower() == name_lower:
            return team
    
    return None


def get_mock_teams_for_testing() -> list[dict[str, Any]]:
    """
    Get mock team data for testing purposes.
    This provides data when the static file is not populated.
    
    Returns:
        List of mock team data dictionaries
    """
    return [
        {
            'id': '150',
            'espn_id': '150',
            'abbreviation': 'DUKE',
            'display_name': 'Duke Blue Devils',
            'short_name': 'Duke',
            'mascot': 'Blue Devils',
            'location': 'Duke',
            'name_variants': ['Duke Blue Devils', 'Duke', 'Duke University']
        },
        {
            'id': '153',
            'espn_id': '153',
            'abbreviation': 'UNC',
            'display_name': 'North Carolina Tar Heels',
            'short_name': 'North Carolina',
            'mascot': 'Tar Heels',
            'location': 'North Carolina',
            'name_variants': ['North Carolina Tar Heels', 'North Carolina', 'UNC', 'UNC Tar Heels']
        },
        {
            'id': '152',
            'espn_id': '152',
            'abbreviation': 'NCST',
            'display_name': 'NC State Wolfpack',
            'short_name': 'NC State',
            'mascot': 'Wolfpack',
            'location': 'NC State',
            'name_variants': ['NC State Wolfpack', 'North Carolina State', 'NC State', 'NCST']
        },
        {
            'id': '96',
            'espn_id': '96',
            'abbreviation': 'UK',
            'display_name': 'Kentucky Wildcats',
            'short_name': 'Kentucky',
            'mascot': 'Wildcats',
            'location': 'Kentucky',
            'name_variants': ['Kentucky Wildcats', 'Kentucky', 'University of Kentucky', 'UK']
        },
        {
            'id': '30',
            'espn_id': '30',
            'abbreviation': 'USC',
            'display_name': 'USC Trojans',
            'short_name': 'USC',
            'mascot': 'Trojans',
            'location': 'Southern California',
            'name_variants': ['USC Trojans', 'USC', 'Southern California', 'University of Southern California']
        }
    ]


def get_mock_team_name_mapping() -> dict[str, str]:
    """
    Generate a mapping of team name variants to canonical names using mock data.
    For testing purposes.
    
    Returns:
        Dictionary mapping variant names to canonical (display) names
    """
    teams = get_mock_teams_for_testing()
    name_map = {}
    
    for team in teams:
        canonical_name = team['display_name']
        
        # Map all variants to the canonical name
        for variant in team['name_variants']:
            name_map[variant] = canonical_name
            
        # Map abbreviation to canonical name
        if team['abbreviation']:
            name_map[team['abbreviation']] = canonical_name
    
    return name_map


def get_mock_team_by_abbreviation(abbrev: str) -> dict[str, Any] | None:
    """
    Find a team by its abbreviation using mock data.
    For testing purposes.
    
    Args:
        abbrev: Team abbreviation (e.g., 'DUKE')
        
    Returns:
        Team data dictionary or None if not found
    """
    teams = get_mock_teams_for_testing()
    
    for team in teams:
        if team['abbreviation'] == abbrev:
            return team
    
    return None


def get_mock_team_by_name(name: str) -> dict[str, Any] | None:
    """
    Find a team by any of its name variants using mock data.
    For testing purposes.
    
    Args:
        name: Team name to search for
        
    Returns:
        Team data dictionary or None if not found
    """
    teams = get_mock_teams_for_testing()
    name_lower = name.lower()
    
    for team in teams:
        # Check all variants
        for variant in team['name_variants']:
            if variant and variant.lower() == name_lower:
                return team
                
        # Check abbreviation
        if team['abbreviation'] and team['abbreviation'].lower() == name_lower:
            return team
    
    return None 