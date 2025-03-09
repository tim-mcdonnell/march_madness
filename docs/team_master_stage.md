# Team Master Data Stage

## Overview

The Team Master Data stage is a specialized pipeline stage that creates a foundational team master data file. This file serves as a reference for all team information across the project, helping to address duplicate rows and inconsistent data in joins.

## Purpose

The primary purposes of this stage are:

1. Extract all unique team IDs from raw data files
2. For each team ID, fetch metadata from the ESPN API
3. Create a comprehensive master data file that contains:
   - Team ID
   - Team Location
   - Team Name
   - Seasons in which the team appears

This master data becomes the foundation for subsequent data processing, feature engineering, and model training, ensuring consistency in team information across all data operations.

## Usage

The Team Master stage is designed to be run explicitly when needed, rather than as part of the normal pipeline flow. To run this stage:

```bash
python run_pipeline.py --stages team_master
```

For better control and performance, you can adjust the batch size for API calls:

```bash
python run_pipeline.py --stages team_master --batch-size 10
```

Or test with a single team ID:

```bash
python run_pipeline.py --stages team_master --test-team-id 91
```

**Note**: This stage is NOT included when running the full pipeline with `python run_pipeline.py --stages all` since it's designed to be run only when needed to establish or update the master data.

## Output

The stage produces two master data files:

```
data/master/team_master_base.parquet  # Base file with team IDs and seasons
data/master/team_master.parquet       # Enriched file with team locations and names
```

The final master data file (`team_master.parquet`) contains the following columns:

- `team_id` (Int): The unique identifier for the team
- `team_location` (String): The location/city of the team (e.g., "Duke")
- `team_name` (String): The name/mascot of the team (e.g., "Blue Devils")
- `season` (Int): The season year in which the team appears in the data

## Data Source

This stage retrieves team metadata from the ESPN API:

```
http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{team_id}
```

Where `{team_id}` is replaced with the actual team ID found in the raw data files.

## Implementation Details

### Team ID Extraction

The stage scans all raw data files in the following categories to extract team IDs:
- team_box
- player_box
- schedules

It looks for columns that contain team identification information, such as:
- team_id
- home_id
- away_id

### Error Handling

The stage includes robust error handling for:
- Missing raw data files
- Invalid or corrupt Parquet files
- Failed API requests
- Malformed API responses

If the ESPN API request fails for a team ID, a record is still created with just the team ID and season, with null values for team location and name.

## Integration

This master data can be used in downstream processes by joining on the `team_id` and `season` columns, which will provide consistent team information across all data operations.

**IMPORTANT**: Always join with team master data **ONLY on `team_id` and `season`**. Team locations and names can vary from year to year in NCAA data. Using `team_location` or `team_name` in joins can lead to data inconsistencies, duplicate rows, and incorrect results.

Example usage in a data processing script:

```python
import polars as pl
from pathlib import Path

# Load team master data
team_master = pl.read_parquet(Path("data/master/team_master.parquet"))

# Load some other dataset
game_data = pl.read_parquet(Path("data/processed/team_box/2023.parquet"))

# CORRECT: Join only on team_id and season
enriched_data = game_data.join(
    team_master,
    on=["team_id", "season"],
    how="left"
)

# INCORRECT: Do not join on team_location or team_name
# enriched_data = game_data.join(
#     team_master,
#     on=["team_id", "team_location", "season"],
#     how="left"
# )
```

### Use in Feature Engineering and Models

When creating features or training models, use this master data as the canonical source of team information. All processed, feature, and model files should use consistent team IDs and seasons from this master data. 