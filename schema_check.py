import logging
from pathlib import Path

import polars as pl

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

data_dir = Path('./data/raw')
logger.info('Checking schemas of raw data files...')

for category in ['play_by_play', 'player_box', 'schedules', 'team_box']:
    files = list(data_dir.glob(f'{category}/*.parquet'))
    if files:
        logger.info(f'\n=== {category.upper()} SCHEMA ===')
        df = pl.read_parquet(files[0])
        logger.info(f"Number of columns: {len(df.columns)}")
        logger.info(df.schema)
    else:
        logger.info(f'\n=== {category.upper()} - No files found ===') 