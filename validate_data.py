#!/usr/bin/env python3
"""
Command-line script for validating NCAA basketball data.

This script provides a command-line interface for validating NCAA basketball data
against the defined schemas and consistency rules.
"""

import argparse
import logging
import sys
from pathlib import Path

from src.data.schema import get_schema_summary
from src.data.validation import (
    DataValidationError,
    generate_validation_report,
    validate_data_consistency,
    validate_raw_data,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('validation.log')
    ]
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Validate NCAA basketball data against schemas and check for consistency'
    )
    
    parser.add_argument(
        '-d', '--data-dir',
        type=str,
        default='data/raw',
        help='Directory containing raw data files (default: data/raw)'
    )
    
    parser.add_argument(
        '-c', '--categories',
        type=str,
        nargs='+',
        choices=['play_by_play', 'player_box', 'schedules', 'team_box'],
        help='Data categories to validate (default: all categories)'
    )
    
    parser.add_argument(
        '-y', '--years',
        type=int,
        nargs='+',
        help='Years to validate (default: all available years)'
    )
    
    parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help='Enable strict validation (fails on any validation error)'
    )
    
    parser.add_argument(
        '--strict-optional',
        action='store_true',
        help='Treat optional columns as required (strict schema checking)'
    )
    
    parser.add_argument(
        '--no-consistency',
        action='store_true',
        help='Skip data consistency checks'
    )
    
    parser.add_argument(
        '-r', '--report',
        type=str,
        default='validation_report.md',
        help='Path for validation report output (default: validation_report.md)'
    )
    
    parser.add_argument(
        '--show-schema',
        action='store_true',
        help='Display schema information and exit'
    )
    
    return parser.parse_args()


def main() -> int:
    """Main function for the validation script."""
    args = parse_args()
    
    # Show schema information if requested
    if args.show_schema:
        for _category, _info in get_schema_summary().items():
            pass
        return 0
    
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return 1
    
    try:
        # Validate raw data files
        validation_results = validate_raw_data(
            data_dir=data_dir,
            categories=args.categories,
            years=args.years,
            strict=args.strict,
            strict_optional=args.strict_optional
        )
        
        # Run consistency checks if enabled
        if not args.no_consistency:
            logger.info("Running data consistency checks")
            consistency_results = validate_data_consistency(
                data_dir=data_dir,
                categories=args.categories,
                years=args.years,
                strict=args.strict
            )
            
            # Merge consistency results into validation results
            for key, result in consistency_results.items():
                validation_results[f"consistency_{key}"] = result
        
        # Generate validation report
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        generate_validation_report(validation_results, report_path)
        logger.info(f"Validation report generated: {report_path}")
        
        # Check if validation passed
        validation_passed = all(
            result.get('valid', False) 
            for result in validation_results.values() 
            if isinstance(result, dict) and 'valid' in result
        )
        
        if validation_passed:
            logger.info("Validation completed successfully")
            return 0
        logger.error("Validation found issues - see report for details")
        return 1
            
    except DataValidationError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 