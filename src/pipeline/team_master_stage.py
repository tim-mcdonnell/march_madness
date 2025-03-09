"""
NCAA March Madness - Team Master Data Population Stage

This module handles the population of master team data for the NCAA March Madness
prediction pipeline. It scans raw data files to extract unique team IDs, fetches
team metadata from the ESPN API, and stores it in a master data file.
"""

import logging
import time
from pathlib import Path
from typing import Any

import polars as pl
import requests

from src.pipeline.config import get_raw_data_dir

# Configure logging
logger = logging.getLogger(__name__)

class TeamMasterStage:
    """
    Pipeline stage for populating team master data.
    
    This stage extracts team IDs from all raw data files and creates a master reference
    table with team info by querying the ESPN API.
    """
    
    ESPN_API_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{team_id}"
    RETRY_DELAY = 1.0  # seconds between API requests when hitting rate limits
    
    def __init__(
        self,
        data_dir: str = "data",
        config: dict[str, Any] | None = None,
        test_team_id: int | None = None,
    ) -> None:
        """
        Initialize the team master data stage.
        
        Args:
            data_dir: Base data directory
            config: Pipeline configuration
            test_team_id: Team ID to use for testing (instead of real ESPN API)
        """
        self.test_team_id = test_team_id
        
        # Set up directories
        if config:
            self.raw_data_dir = get_raw_data_dir(config)
        else:
            self.raw_data_dir = Path(data_dir) / "raw"
            
        # Create master data directory
        self.master_data_dir = Path(data_dir) / "master"
        self.master_data_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up file path (single file approach)
        self.output_file = self.master_data_dir / "team_master.parquet"
    
    def _extract_unique_team_ids(self) -> dict[int, set[int]]:
        """
        Extract unique team IDs from raw data files.
        
        Returns:
            Dictionary mapping team IDs to a set of seasons they appear in
        """
        logger.info("Extracting unique team IDs from raw data...")
        
        # Dictionary to store team_id -> set of seasons
        team_seasons: dict[int, set[int]] = {}
        raw_dir = Path(self.raw_data_dir)
        
        # Valid columns that contain team IDs
        team_id_columns = [
            'team_id', 'home_id', 'away_id', 'home_team_id', 'away_team_id',
            'opponent_team_id'
        ]
        
        # Walk through the raw data directory
        for category_dir in raw_dir.iterdir():
            if category_dir.is_dir():
                logger.info(f"Scanning category: {category_dir.name}")
                
                # For each parquet file in this category
                for parquet_file in category_dir.glob("*.parquet"):
                    try:
                        # Extract year from filename
                        # Assuming format like: team_box_2023.parquet or 2023.parquet
                        filename = parquet_file.stem
                        year_str = filename.split('_')[-1] if '_' in filename else filename
                        
                        try:
                            year = int(year_str)
                        except ValueError:
                            logger.warning(f"Could not extract year from filename: {parquet_file.name}")
                            continue
                        
                        logger.debug(f"Loading {parquet_file} to extract team IDs")
                        
                        # Load parquet file
                        df = pl.read_parquet(parquet_file)
                        
                        # Find team ID columns in this DataFrame
                        unique_teams = {}
                        for col in df.columns:
                            if col in team_id_columns:
                                unique_teams[col] = df.select(pl.col(col)).unique().to_series().to_list()
                        
                        # Process team IDs
                        for col, ids in unique_teams.items():
                            logger.debug(f"Found {len(ids)} unique team IDs in column {col}")
                            
                            for team_id in unique_teams[col]:
                                # Skip non-integer or invalid team IDs
                                if not isinstance(team_id, int | float) or team_id <= 0:
                                    continue
                                
                                team_id = int(team_id)  # Ensure integer
                                
                                # Add to team seasons dictionary
                                if team_id not in team_seasons:
                                    team_seasons[team_id] = set()
                                team_seasons[team_id].add(year)
                    
                    except Exception as e:
                        logger.exception(f"Error processing {parquet_file}: {e}")
        
        logger.info(f"Extracted {len(team_seasons)} unique team IDs across all raw data files")
        return team_seasons
    
    def _create_master_file(self, team_seasons: dict[int, set[int]]) -> None:
        """
        Create and save a master data file with team IDs and seasons.
        
        Args:
            team_seasons: Dictionary mapping team IDs to a set of seasons
        """
        logger.info("Creating team master data file...")
        
        # Create rows for team/season combinations
        rows = []
        for team_id, seasons in team_seasons.items():
            for season in seasons:
                rows.append({
                    "team_id": team_id, 
                    "season": season,
                    "location": "",  # Empty string instead of None
                    "name": ""       # Empty string instead of None
                })
        
        if rows:
            # Define schema explicitly with appropriate types
            schema = {
                "team_id": pl.Int64,
                "season": pl.Int64,
                "location": pl.Utf8,
                "name": pl.Utf8
            }
            
            # Create DataFrame with schema
            df = pl.DataFrame(rows, schema=schema)
            
            # Save master data
            df.write_parquet(self.output_file)
            logger.info(f"Initial team master data saved to {self.output_file}")
        else:
            logger.error("No team data was collected")
    
    def _fetch_team_data_from_espn(self, team_id: int) -> dict[str, Any]:
        """
        Fetch team metadata from the ESPN API.
        
        Args:
            team_id: ESPN team ID
            
        Returns:
            Dictionary with team data or empty dict if error
        """
        url = self.ESPN_API_URL.format(team_id=team_id)
        
        try:
            if self.test_team_id is not None and self.test_team_id == team_id:
                # Use test data for unit tests
                return {
                    "team": {
                        "id": str(team_id),
                        "location": "Test University",
                        "name": "Test Team",
                        "abbreviation": "TEST",
                        "displayName": "Test University Test Team",
                        "color": "123456",
                        "alternateColor": "654321",
                        "logos": [{"href": "https://example.com/logo.png"}],
                        "conference": {"id": "99", "name": "Test Conference"}
                    }
                }
                
            response = requests.get(url, timeout=10)
            
            if response.status_code == 429:  # Rate limited
                time.sleep(self.RETRY_DELAY)
                return self._fetch_team_data_from_espn(team_id)  # Retry
                
            if response.status_code == 200:
                return response.json()
                
            logger.warning(f"Failed to fetch team data for ID {team_id}: HTTP {response.status_code}")
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching data for team ID {team_id}: {e}")
            return {}
    
    def _process_espn_response(self, team_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process ESPN API response to extract relevant team data.
        
        Args:
            team_id: Team ID
            data: ESPN API response data
            
        Returns:
            Dictionary with processed team data fields
        """
        # Initialize with default values to ensure all fields are present
        result = {
            "team_id": team_id,
            "location": "",
            "name": ""
        }
        
        try:
            # Check if there's team data
            if "team" not in data:
                return result
                
            team_data = data["team"]
            
            # Extract basic team info
            result["location"] = team_data.get("location", "")
            result["name"] = team_data.get("name", "")
                
        except Exception as e:
            logger.error(f"Error processing ESPN data for team ID {team_id}: {e}")
            
        return result
    
    def _enrich_team_data(self, batch_size: int = 50) -> bool:
        """
        Enrich team master data with metadata from ESPN API.
        
        Args:
            batch_size: Number of teams to process in one batch before saving
            
        Returns:
            True if successful, False otherwise
        """
        # Check if master file exists
        if not self.output_file.exists():
            logger.error(f"Master file not found: {self.output_file}")
            return False
            
        logger.info(f"Enriching team master data from {self.output_file}")
        
        try:
            # Load master data
            df = pl.read_parquet(self.output_file)
            
            # Identify teams that need data
            # We'll only process teams that have empty location strings
            needs_data = df.filter(pl.col("location") == "")
            
            # Get unique team IDs that don't have data yet
            teams_to_update = set(
                needs_data
                .select("team_id")
                .unique()
                .to_series()
                .to_list()
            )
            
            # Process teams in batches
            logger.info(f"Enriching {len(teams_to_update)} teams with ESPN data")
            
            if teams_to_update:
                team_updates = {}
                
                for count, team_id in enumerate(teams_to_update, 1):
                    if count % 10 == 0:
                        logger.info(f"Processing team {count}/{len(teams_to_update)}")
                        
                    # Fetch and process team data
                    espn_data = self._fetch_team_data_from_espn(team_id)
                    processed_data = self._process_espn_response(team_id, espn_data)
                    
                    if processed_data and processed_data["location"] != "":
                        team_updates[team_id] = processed_data
                        
                    # Save in batches
                    if len(team_updates) >= batch_size:
                        self._update_master_file(df, team_updates)
                        # Reload the data after update
                        df = pl.read_parquet(self.output_file)
                        team_updates = {}
                        
                # Save any remaining updates
                if team_updates:
                    self._update_master_file(df, team_updates)
            
            return True
                
        except Exception as e:
            logger.exception(f"Error enriching team data: {e}")
            return False
    
    def _update_master_file(self, df: pl.DataFrame, team_updates: dict[int, dict[str, Any]]) -> None:
        """
        Update the master file with team data.
        
        Args:
            df: Current master data DataFrame
            team_updates: Dictionary of team_id -> team data updates
        """
        if not team_updates:
            return
        
        # Get the schema from the original DataFrame
        schema = df.schema
        
        # Create a DataFrame with the updated team data
        updates_df = pl.DataFrame(list(team_updates.values()))
        
        # Get the columns from the original DataFrame to ensure consistency
        original_columns = df.columns
        
        team_ids_to_update = updates_df["team_id"].unique().to_list()
        updated_rows = []
        
        for update_team_id in team_ids_to_update:
            # Get the team data from updates_df
            update_team_data = updates_df.filter(pl.col("team_id") == update_team_id)
            if update_team_data.height > 0:
                # Get all seasons for this team from the original dataframe
                seasons = df.filter(
                    pl.col("team_id") == update_team_id
                )["season"].to_list()
                
                # Create a row for each season with the updated team data
                for season in seasons:
                    # Start with a dictionary with empty values (not None)
                    row_data = {
                        "team_id": update_team_id,
                        "season": season,
                        "location": "",
                        "name": ""
                    }
                    
                    # Update with values from the ESPN data
                    for col in updates_df.columns:
                        if col in original_columns and col in update_team_data.columns:
                            value = update_team_data[col][0]
                            # Ensure non-null values for string columns
                            if isinstance(schema[col], pl.Utf8) and value is None:
                                value = ""
                            row_data[col] = value
                    
                    updated_rows.append(row_data)
        
        if updated_rows:
            try:
                # Create DataFrame with same schema as original
                updated_rows_df = pl.DataFrame(updated_rows, schema=schema)
                
                # Remove the rows that will be updated
                filtered_df = df.filter(
                    ~((pl.col("team_id").is_in(team_ids_to_update)) & 
                      (pl.col("location") == ""))
                )
                
                # Combine the filtered original data with the updates
                combined_df = pl.concat([filtered_df, updated_rows_df])
                
                # Save updates
                combined_df.write_parquet(self.output_file)
                logger.info(f"Saved batch of {len(team_updates)} team updates")
                
            except Exception as e:
                logger.error(f"Error updating master file: {e}")
                # Dump problematic data for debugging
                problematic_data = {
                    "original_schema": {k: str(v) for k, v in schema.items()},
                    "update_columns": updates_df.columns,
                    "sample_row": updated_rows[0] if updated_rows else None
                }
                logger.debug(f"Problematic data: {problematic_data}")
                raise
    
    def run(self, batch_size: int = 50) -> bool:
        """
        Run the complete team master data stage.
        
        Args:
            batch_size: Number of teams to process in one batch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, check if we need to create the initial file
            if not self.output_file.exists():
                # Step 1: Extract unique team IDs from raw data
                team_seasons = self._extract_unique_team_ids()
                
                # Step 2: Create master file with placeholder values
                self._create_master_file(team_seasons)
            else:
                logger.info(f"Using existing master file: {self.output_file}")
            
            # Step 3: Enrich with ESPN API data
            return self._enrich_team_data(batch_size=batch_size)
            
        except Exception as e:
            logger.exception(f"Error in team master data population stage: {e}")
            return False
            
            
def run_team_master_stage(config: dict[str, Any], test_team_id: int | None = None, batch_size: int = 50) -> bool:
    """
    Run the team master data population stage.
    
    Args:
        config: Pipeline configuration
        test_team_id: Team ID to use for testing
        batch_size: Number of teams to process in one batch before saving progress.
                    Lower values (e.g., 10) reduce memory usage and save more frequently,
                    while higher values are more efficient but risk more data loss on failure.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        stage = TeamMasterStage(config=config, test_team_id=test_team_id)
        return stage.run(batch_size=batch_size)
    except Exception as e:
        logger.exception(f"Error running team master data stage: {e}")
        return False 