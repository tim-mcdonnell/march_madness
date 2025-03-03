import logging
from collections import defaultdict
from pathlib import Path

import polars as pl

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define directories
data_dir = 'data/raw'
categories = ['play_by_play', 'player_box', 'schedules', 'team_box']

for category in categories:
    category_dir = Path(data_dir) / category
    files = list(category_dir.glob('*.parquet'))
    
    if not files:
        continue
    
    
    # Store schemas for comparison
    all_schemas = {}
    column_presence = defaultdict(int)
    column_types = defaultdict(lambda: defaultdict(int))
    total_files = len(files)
    
    # Track the most recent file for detailed display
    most_recent_file = max(files, key=lambda f: f.name)
    most_recent_df = None
    
    # Analyze each file
    for file_path in sorted(files):
        try:
            df = pl.read_parquet(file_path)
            
            # Store schema for this file
            schema = df.schema
            all_schemas[file_path.name] = schema
            
            # If this is the most recent file, keep the dataframe for detailed display
            if file_path == most_recent_file:
                most_recent_df = df
            
            # Track column presence and types
            for col_name, col_type in schema.items():
                column_presence[col_name] += 1
                type_name = str(col_type).split('.')[-1]  # Extract type name
                column_types[col_name][type_name] += 1
            
        except Exception as e:
            logger.error(f"Error analyzing schema for {file_path}: {str(e)}")
    
    # Analyze schema consistency
    
    # Check if all files have the same columns
    all_columns = set(column_presence.keys())
    consistent_columns = [col for col, count in column_presence.items() if count == total_files]
    missing_in_some = [col for col, count in column_presence.items() if 0 < count < total_files]
    
    
    if missing_in_some:
        for col in sorted(missing_in_some):
            presence_pct = column_presence[col] / total_files * 100
    
    # Check for type inconsistencies
    type_inconsistencies = [col for col in all_columns if len(column_types[col]) > 1]
    
    if type_inconsistencies:
        for _col in sorted(type_inconsistencies):
            pass
    
    # Display detailed information about the most recent file
    if most_recent_df is not None:
        
        # Check for null values
        null_counts = most_recent_df.null_count()
        columns_with_nulls = [
            col for col, count in zip(
                null_counts.columns, null_counts.row(0), strict=False
            ) if count > 0
        ]
        
        if columns_with_nulls:
            for col in sorted(columns_with_nulls):
                null_count = most_recent_df[col].null_count()
                null_pct = null_count / len(most_recent_df) * 100
        
    
    # Recommended schema approach
    
    # Generate schema recommendation for this category
    
    # Sort columns by presence percentage (descending)
    sorted_columns = sorted(all_columns, key=lambda col: (-column_presence[col], col))
    
    for col in sorted_columns:
        presence_pct = column_presence[col] / total_files * 100
        
        # Determine recommended type
        if len(column_types[col]) == 1:
            # Only one type found, use it
            recommended_type = next(iter(column_types[col].keys()))
        else:
            # Multiple types, use the most common
            recommended_type = max(column_types[col].items(), key=lambda x: x[1])[0]
        
        # Add a comment for columns not present in all files
        comment = ""
        if presence_pct < 100:
            comment = f"  # Present in {presence_pct:.1f}% of files"
        
    
