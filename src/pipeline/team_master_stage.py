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
        
        # Set up file paths
        self.base_output_file = self.master_data_dir / "team_master_base.parquet"
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
    
    def _create_base_master_file(self, team_seasons: dict[int, set[int]]) -> None:
        """
        Create and save a base master data file with team IDs and seasons.
        
        Args:
            team_seasons: Dictionary mapping team IDs to a set of seasons
        """
        logger.info("Creating base master data file...")
        
        # Create rows for team/season combinations
        rows = []
        for team_id, seasons in team_seasons.items():
            for season in seasons:
                rows.append({"team_id": team_id, "season": season})
        
        if rows:
            # Create DataFrame
            df = pl.DataFrame(rows)
            
            # Add placeholder columns
            df = df.with_columns([
                pl.lit(None).alias("location"),
                pl.lit(None).alias("name"),
                pl.lit(None).alias("short_name"),
                pl.lit(None).alias("abbreviation"),
                pl.lit(None).alias("display_name"),
                pl.lit(None).alias("conference_id"),
                pl.lit(None).alias("conference_name"),
                pl.lit(None).alias("logo_url"),
                pl.lit(None).alias("color"),
                pl.lit(None).alias("alternate_color"),
            ])
            
            # Save base master data
            df.write_parquet(self.base_output_file)
            logger.info(f"Base master data saved to {self.base_output_file}")
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
        result = {}
        
        try:
            # Check if there's team data
            if "team" not in data:
                return result
                
            team_data = data["team"]
            
            # Extract basic team info
            result["team_id"] = team_id
            result["location"] = team_data.get("location", "")
            result["name"] = team_data.get("name", "")
            result["short_name"] = team_data.get("shortDisplayName", "")
            result["abbreviation"] = team_data.get("abbreviation", "")
            result["display_name"] = team_data.get("displayName", "")
            result["color"] = team_data.get("color", "")
            result["alternate_color"] = team_data.get("alternateColor", "")
            
            # Extract conference info if available
            if "conference" in team_data:
                result["conference_id"] = team_data["conference"].get("id", "")
                result["conference_name"] = team_data["conference"].get("name", "")
            
            # Extract logo URL if available
            if "logos" in team_data and team_data["logos"]:
                result["logo_url"] = team_data["logos"][0].get("href", "")
                
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
        # Check if base master file exists
        if not self.base_output_file.exists():
            logger.error(f"Base master file not found: {self.base_output_file}")
            return False
            
        logger.info(f"Enriching team master data from {self.base_output_file}")
        
        try:
            # Load base master data
            df = pl.read_parquet(self.base_output_file)
            
            # See if we have an existing enriched file to use as starting point
            if self.output_file.exists():
                logger.info(f"Found existing enriched data: {self.output_file}")
                enriched_df = pl.read_parquet(self.output_file)
                
                # Identify teams that already have data
                # We'll only process teams that don't have a location
                has_data = set(
                    enriched_df
                    .filter(pl.col("location").is_not_null())
                    .select("team_id")
                    .unique()
                    .to_series()
                    .to_list()
                )
                
                logger.info(f"Found {len(has_data)} teams with existing data")
                
                # Create a new dataframe with updates
                team_updates = {}
                
                # Get unique team IDs that don't have data yet
                teams_to_update = set(
                    df.filter(~pl.col("team_id").is_in(has_data))
                    .select("team_id")
                    .unique()
                    .to_series()
                    .to_list()
                )
                
                # Process teams in batches
                logger.info(f"Enriching {len(teams_to_update)} teams with ESPN data")
                
                if teams_to_update:
                    for count, team_id in enumerate(teams_to_update, 1):
                        if count % 10 == 0:
                            logger.info(f"Processing team {count}/{len(teams_to_update)}")
                            
                        # Fetch and process team data
                        espn_data = self._fetch_team_data_from_espn(team_id)
                        processed_data = self._process_espn_response(team_id, espn_data)
                        
                        if processed_data and "location" in processed_data:
                            team_updates[team_id] = processed_data
                            
                        # Save in batches
                        if len(team_updates) >= batch_size:
                            # Create a DataFrame with the updated team data
                            updates_df = pl.DataFrame(list(team_updates.values()))
                            
                            # Filter out the rows in enriched_df that have team_ids in updates_df
                            team_ids_to_update = updates_df["team_id"].unique().to_list()
                            
                            # For each team in updates, get seasons from base file
                            updated_rows = []
                            for update_team_id in team_ids_to_update:
                                # Get the team data from updates_df
                                update_team_data = updates_df.filter(pl.col("team_id") == update_team_id)
                                if update_team_data.height > 0:
                                    # Convert the row to a dictionary
                                    team_data_dict = {}
                                    row = update_team_data.row(0)
                                    for i, col in enumerate(update_team_data.columns):
                                        team_data_dict[col] = row[i]
                                
                                    # Get all seasons for this team from the original dataframe
                                    seasons = enriched_df.filter(
                                        pl.col("team_id") == update_team_id
                                    )["season"].to_list()
                                    
                                    # Create a row for each season with the updated team data
                                    for season in seasons:
                                        row_data = team_data_dict.copy()
                                        row_data["season"] = season
                                        updated_rows.append(row_data)
                            
                            if updated_rows:
                                # Convert to DataFrame
                                updated_rows_df = pl.DataFrame(updated_rows)
                                
                                # Remove the rows that will be updated
                                filtered_df = enriched_df.filter(
                                    ~((pl.col("team_id").is_in(team_ids_to_update)) & 
                                      (pl.col("location").is_null()))
                                )
                                
                                # Combine the filtered original data with the updates
                                enriched_df = pl.concat([filtered_df, updated_rows_df])
                                
                                # Save updates
                                enriched_df.write_parquet(self.output_file)
                                logger.info(f"Saved batch of {len(team_updates)} team updates")
                                
                            team_updates = {}
                            
                    # Save any remaining updates
                    if team_updates:
                        # Create a DataFrame with the updated team data
                        updates_df = pl.DataFrame(list(team_updates.values()))
                        
                        # Filter out the rows in enriched_df that have team_ids in updates_df
                        team_ids_to_update = updates_df["team_id"].unique().to_list()
                        
                        # For each team in updates, get seasons from base file
                        updated_rows = []
                        for update_team_id in team_ids_to_update:
                            # Get the team data from updates_df
                            update_team_data = updates_df.filter(pl.col("team_id") == update_team_id)
                            if update_team_data.height > 0:
                                # Convert the row to a dictionary
                                team_data_dict = {}
                                row = update_team_data.row(0)
                                for i, col in enumerate(update_team_data.columns):
                                    team_data_dict[col] = row[i]
                            
                                # Get all seasons for this team from the original dataframe
                                seasons = enriched_df.filter(
                                    pl.col("team_id") == update_team_id
                                )["season"].to_list()
                                
                                # Create a row for each season with the updated team data
                                for season in seasons:
                                    row_data = team_data_dict.copy()
                                    row_data["season"] = season
                                    updated_rows.append(row_data)
                        
                        if updated_rows:
                            # Convert to DataFrame
                            updated_rows_df = pl.DataFrame(updated_rows)
                            
                            # Remove the rows that will be updated
                            filtered_df = enriched_df.filter(
                                ~((pl.col("team_id").is_in(team_ids_to_update)) & 
                                  (pl.col("location").is_null()))
                            )
                            
                            # Combine the filtered original data with the updates
                            enriched_df = pl.concat([filtered_df, updated_rows_df])
                            
                            # Save updates
                            enriched_df.write_parquet(self.output_file)
                            logger.info(f"Saved final batch of {len(team_updates)} team updates")
                
                return True
                
            # Start fresh - we don't have an existing enriched file
            logger.info("Creating new enriched team master file")
            
            # Get unique team IDs
            unique_team_ids = df.select("team_id").unique().to_series().to_list()
            logger.info(f"Processing {len(unique_team_ids)} unique teams")
            
            # Process teams
            team_data = []
            
            for count, team_id in enumerate(unique_team_ids, 1):
                if count % 10 == 0:
                    logger.info(f"Processing team {count}/{len(unique_team_ids)}")
                    
                # Fetch and process team data
                espn_data = self._fetch_team_data_from_espn(team_id)
                processed_data = self._process_espn_response(team_id, espn_data)
                
                if processed_data:
                    # Get all seasons for this team
                    seasons = df.filter(pl.col("team_id") == team_id).select("season").to_series().to_list()
                    
                    # Add each team/season combo with the team data
                    for season in seasons:
                        row = processed_data.copy()
                        row["season"] = season
                        team_data.append(row)
                        
                # Save in batches
                if len(team_data) >= batch_size:
                    batch_df = pl.DataFrame(team_data)
                    
                    if self.output_file.exists():
                        # Append to existing file
                        existing_df = pl.read_parquet(self.output_file)
                        combined_df = pl.concat([existing_df, batch_df])
                        combined_df.write_parquet(self.output_file)
                    else:
                        # Create new file
                        batch_df.write_parquet(self.output_file)
                        
                    logger.info(f"Saved batch of {len(team_data)} team records")
                    team_data = []
                    
            # Save any remaining data
            if team_data:
                batch_df = pl.DataFrame(team_data)
                
                if self.output_file.exists():
                    # Append to existing file
                    existing_df = pl.read_parquet(self.output_file)
                    combined_df = pl.concat([existing_df, batch_df])
                    combined_df.write_parquet(self.output_file)
                else:
                    # Create new file
                    batch_df.write_parquet(self.output_file)
                    
                logger.info(f"Saved final batch of {len(team_data)} team records")
            
            return True
        
        except Exception as e:
            logger.exception(f"Error enriching team data: {e}")
            return False
            
    def run(self, batch_size: int = 50) -> bool:
        """
        Run the complete team master data stage.
        
        Args:
            batch_size: Number of teams to process in one batch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step 1: Extract unique team IDs from raw data
            team_seasons = self._extract_unique_team_ids()
            
            # Step 2: Create base master file
            self._create_base_master_file(team_seasons)
            
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
        batch_size: Number of teams to process in one batch
        
    Returns:
        True if successful, False otherwise
    """
    try:
        stage = TeamMasterStage(config=config, test_team_id=test_team_id)
        return stage.run(batch_size=batch_size)
    except Exception as e:
        logger.exception(f"Error running team master data stage: {e}")
        return False 