import logging

import yaml

from src.pipeline.data_stage import process_transformations

logging.basicConfig(level=logging.INFO)

with open('config/pipeline_config.yaml') as f:
    config = yaml.safe_load(f)

# Run transformations
result = process_transformations(config)

if result:
    logging.info("Transformations completed successfully")
else:
    logging.error("Transformations failed") 