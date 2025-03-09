# NCAA March Madness Data Validation Framework

## Overview

The data validation framework ensures the quality and consistency of NCAA basketball data used in the March Madness prediction pipeline. It provides mechanisms to validate data against predefined schemas, check for consistency across different data categories, and generate comprehensive validation reports.

## Schema Structure

The schema validation framework is designed to handle the variability observed in the NCAA basketball data across different years. Based on comprehensive analysis of historical data files, the schemas are structured to accommodate:

### Core vs. Optional Columns

Each schema is divided into two categories:

- **Core Columns**: Essential columns that must be present in all data files. These columns have been identified as consistently present across all historical data and are critical for the pipeline's functionality.

- **Optional Columns**: Columns that may be present in some files but not others. The validation framework can be configured to either require these columns (strict validation) or allow their absence (flexible validation).

### Example Schema Structure

```python
PLAY_BY_PLAY_SCHEMA = {
    SchemaType.CORE: {
        'game_id': pl.Utf8,
        'sequence_number': pl.Int32,
        'period_number': pl.Int32,
        # ... more core columns
    },
    SchemaType.OPTIONAL: {
        'athlete_id_2': pl.Utf8,
        'away_timeout_called': pl.Boolean,
        # ... more optional columns
    }
}
```

## Type Flexibility

The framework supports type flexibility to handle inconsistencies in data types observed across files:

- The validation logic includes type compatibility checking, which allows for numeric types to be interchangeable when appropriate (e.g., Int32 can be validated against Int64).

- String columns can be validated against any polars string type.

## Validation Functions

### Schema Validation

```python
validate_schema(df: pl.DataFrame, category: str, strict_optional: bool = False) -> Tuple[bool, List[str]]
```

Validates a dataframe against the schema for a given category:
- `df`: The dataframe to validate
- `category`: The data category (e.g., 'play_by_play', 'team_box')
- `strict_optional`: If True, treats optional columns as required

Returns a tuple containing:
- Boolean indicating if validation passed
- List of error messages if validation failed

### File Validation

```python
validate_file(file_path: Union[str, Path], category: str, strict_optional: bool = False) -> Tuple[bool, List[str]]
```

Validates a parquet file against the schema for a given category:
- `file_path`: Path to the parquet file
- `category`: The data category
- `strict_optional`: If True, treats optional columns as required

Returns a tuple containing:
- Boolean indicating if validation passed
- List of error messages if validation failed

### Batch Validation

```python
validate_raw_data(data_dir: Union[str, Path], categories: List[str] = None, years: List[int] = None, strict: bool = False, strict_optional: bool = False) -> Dict[str, Dict[str, Any]]
```

Validates all data files for specified categories and years:
- `data_dir`: Directory containing raw data files
- `categories`: List of data categories to validate
- `years`: List of years to validate
- `strict`: If True, raises an exception if any validation fails
- `strict_optional`: If True, treats optional columns as required

Returns a dictionary with validation results for each file.

### Consistency Validation

```python
validate_data_consistency(data_dir: Union[str, Path], categories: List[str] = None, years: List[int] = None, strict: bool = False) -> Dict[str, Dict[str, Any]]
```

Validates consistency across different data categories:
- `data_dir`: Directory containing raw data files
- `categories`: List of categories to validate
- `years`: List of years to validate
- `strict`: If True, raises an exception if any consistency check fails

Returns a dictionary with consistency validation results.

## Integration with Pipeline

The validation framework is integrated into the data stage of the pipeline through the `validate_downloaded_data` function in `src/pipeline/data_stage.py`. This function:

1. Reads validation configuration from the pipeline configuration
2. Validates schemas for all downloaded files
3. Checks data consistency across categories if enabled
4. Generates a validation report

## Command-Line Usage

The validation framework can be used directly from the command line using the `validate_data.py` script:

```bash
python validate_data.py --data-dir data/raw --years 2023 2024 --strict-optional --report validation_report.md
```

Options:
- `--data-dir`: Directory containing raw data files
- `--categories`: Data categories to validate
- `--years`: Years to validate
- `--strict`: Enable strict validation
- `--strict-optional`: Treat optional columns as required
- `--no-consistency`: Skip data consistency checks
- `--report`: Path for validation report output
- `--show-schema`: Display schema information and exit

## Configuration

Validation settings can be configured in the pipeline configuration file (`config/pipeline_config.yaml`):

```yaml
data:
  validation:
    enabled: true
    strict: false
    strict_optional: false
    check_consistency: true
    categories:
      - play_by_play
      - player_box
      - schedules
      - team_box
    years: null
    report_path: "validation_reports/latest_validation_report.md"
```

## Best Practices

1. **Run validation early**: Validate data immediately after download to identify issues before they propagate through the pipeline.

2. **Configure validation for your needs**: Use `strict_optional=False` for exploratory analysis where missing columns are acceptable, and `strict_optional=True` for production pipelines where data completeness is critical.

3. **Generate reports**: Always generate validation reports to document the state of the data.

4. **Check consistency**: Enable cross-category consistency checks to ensure data integrity across different aspects of the same games.

5. **Version your schemas**: As data sources evolve, maintain versioned schemas to track changes over time.

## Handling Schema Evolution

As new data becomes available or data sources change, follow these steps to update schemas:

1. Use the `temp_schema_analysis.py` script to analyze new data files and identify changes.

2. Update the schema definitions in `src/data/schema.py` based on the analysis.

3. Run tests to ensure the updated schemas work correctly with both new and existing data.

4. Update documentation to reflect schema changes.

## Data Schema

The framework defines schemas for four main data categories:

| Category | Description | Columns |
|----------|-------------|---------|
| `play_by_play` | Detailed event-by-event data for each game | 57 columns |
| `player_box` | Player statistics for each game | 55 columns |
| `schedules` | Game scheduling information | 86 columns |
| `team_box` | Team-level statistics for each game | 54 columns |

Each schema specifies the expected column names and data types, which are defined in `src/data/schema.py`.

## Reporting

- `generate_validation_report(validation_results, output_path)`: Generates a human-readable validation report

## Testing

The validation framework includes unit tests in `tests/data/test_schema_validation.py` to ensure the validation functions work correctly.

## Extending the Framework

The framework can be extended by:

1. Adding new schema definitions for additional data categories
2. Implementing additional consistency checks
3. Creating custom validation functions for specific requirements
4. Integrating with other data quality tools 