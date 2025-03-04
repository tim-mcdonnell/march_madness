# Exploratory Data Analysis (EDA)

This directory contains Python scripts for exploratory data analysis of the March Madness dataset.

## Structure

- Each analysis task has its own Python script (e.g., `regular_vs_tournament_analysis.py`)
- Scripts should be modular and focus on specific analysis questions
- All scripts should include functions to:
  - Load and prepare data
  - Perform analysis
  - Generate visualizations
  - Export findings to the reports directory

## Best Practices

1. **Documentation**: Include detailed docstrings and comments to explain the analysis approach
2. **Reproducibility**: Make sure analyses can be reproduced by running the scripts
3. **Visualization Output**: Save all visualizations to the `reports/figures` directory
4. **Findings**: Document key findings in markdown files in the `reports/findings` directory

## Running the Analysis

To run any analysis script:

```bash
python -m src.eda.script_name
```

## Example Usage

```python
# Example of how a script should be structured
if __name__ == "__main__":
    # 1. Load and prepare data
    data = load_data()
    
    # 2. Perform analysis
    results = analyze_data(data)
    
    # 3. Generate visualizations
    create_visualizations(results)
    
    # 4. Generate findings report
    generate_report(results)
``` 