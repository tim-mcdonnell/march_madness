# NCAA March Madness Predictor

Welcome to the NCAA March Madness Predictor documentation!

## Overview

This project aims to develop a machine learning model that predicts NCAA March Madness tournament outcomes using 22 years of historical data. By analyzing team statistics, tournament performance, and other relevant factors, we create a data-driven approach to bracket construction that outperforms traditional methods.

## Key Features

- **Comprehensive Data Integration**: Access to 22+ years of NCAA basketball data
- **Modular Pipeline Framework**: End-to-end workflow from data ingestion to prediction
- **Advanced Analytics**: Statistical models for team performance analysis
- **Tournament Simulation**: Bracket optimization through Monte Carlo simulations
- **Interactive Visualizations**: Explore predictions and insights through interactive dashboards

## Getting Started

To get started with the NCAA March Madness Predictor:

```bash
# Clone the repository
git clone https://github.com/tim-mcdonnell/march_madness.git
cd march_madness

# Create a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Run the pipeline
python run_pipeline.py --create-config
python run_pipeline.py
```

Check out the [Installation](installation.md) guide for more detailed instructions.

## Pipeline Framework

The project is organized around a modular pipeline framework that includes:

1. **Data Collection and Cleaning**: Downloading and preprocessing raw basketball data
2. **Exploratory Data Analysis**: Understanding patterns and relationships in the data
3. **Feature Engineering**: Transforming raw data into predictive features
4. **Model Development**: Training and tuning predictive models
5. **Evaluation and Visualization**: Assessing model performance and generating insights

Learn more in the [Pipeline Overview](pipeline/overview.md) section.

## Examples

Explore working examples to understand how to use the NCAA March Madness Predictor:

- [Data Download Example](examples/data-download.md): How to download and access NCAA basketball data
- [Pipeline Usage Example](examples/pipeline-usage.md): How to run the full prediction pipeline

## Contributing

We welcome contributions to the NCAA March Madness Predictor! Check out our [Contributing Guide](contributing.md) to learn how you can help improve the project. 