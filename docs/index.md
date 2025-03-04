# NCAA March Madness Predictor Documentation

Welcome to the NCAA March Madness Predictor documentation! This project aims to develop a machine learning model that predicts NCAA March Madness tournament outcomes using historical data.

## Documentation Sections

### User Guide
*Task-oriented guides on how to use the project*

The User Guide provides practical, step-by-step instructions for using the NCAA March Madness Predictor. Start here if you want to install the software, run predictions, or understand how to configure the system for your needs.

- [Installation](user_guide/installation.md)
- [Getting Started](user_guide/getting_started.md)
- [Pipeline Usage](user_guide/pipeline_usage.md)
- [Configuration](user_guide/configuration.md)
- [Working with Data](user_guide/working_with_data.md)

### Technical Reference
*Detailed technical specifications and architecture documentation*

The Technical Reference provides in-depth information about how the system works internally. Consult this section when you need detailed information about data schemas, pipeline architecture, or other technical details.

- **Data**
  - [Data Overview](reference/data/overview.md)
  - [Data Cleaning](reference/data/cleaning.md)
  - [Data Processing](reference/data/processing.md)
  - [Data Validation](reference/data/validation.md)
  - [Data Schema](reference/data/schema.md)
- **Pipeline**
  - [Pipeline Overview](reference/pipeline/overview.md)
  - [Data Stage](reference/pipeline/data_stage.md)
  - [Feature Engineering Stage](reference/pipeline/feature_stage.md)
  - [Model Stage](reference/pipeline/model_stage.md)

### Developer Guide
*Process-oriented guidance for contributors and developers*

The Developer Guide provides information for developers who want to extend or contribute to the NCAA March Madness Predictor. Use this section when you want to add new features, modify existing functionality, or understand the project's architecture from a developer's perspective.

- [Code Standards](developer_guide/code_standards.md)
- [AI Assistant Guide](developer_guide/ai_assistant_guide.md)
- **Extending the Project**
  - [Adding Features](developer_guide/extending.md)
  - [Custom Models](developer_guide/extending/custom_models.md)
  - [Visualization](developer_guide/extending/visualization.md)

## Project Overview

This project develops a data-driven approach to bracket construction for the NCAA March Madness tournament, utilizing 22 years of historical data. By analyzing team statistics, tournament performance, and other relevant factors, we aim to create predictions that outperform traditional methods.

### Key Features

- **Comprehensive Data Integration**: Access to 22+ years of NCAA basketball data
- **Modular Pipeline Framework**: End-to-end workflow from data ingestion to prediction
- **Advanced Analytics**: Statistical models for team performance analysis
- **Tournament Simulation**: Bracket optimization through Monte Carlo simulations
- **Interactive Visualizations**: Explore predictions and insights through interactive dashboards

## Quick Start

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

For more detailed instructions, see the [Getting Started Guide](user_guide/getting_started.md). 