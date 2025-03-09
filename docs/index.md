# NCAA March Madness Predictor Documentation

Welcome to the NCAA March Madness Predictor documentation. This central index helps you navigate the various documentation sections and find the information you need.

## Documentation Structure

```
docs/
├── index.md                    # Main documentation entry point
├── features/                   # Feature system documentation
│   ├── index.md                # Feature system overview
│   ├── reference/              # Feature technical reference
│   │   └── overview.md         # Complete feature catalog
│   ├── team_performance/       # Team performance feature docs
│   └── shooting/               # Shooting feature docs
├── data/                       # Data documentation
│   ├── index.md                # Data system overview
│   ├── processing.md           # Data processing principles
│   └── reference/              # Technical reference for data
│       ├── schema.md           # Data schemas
│       ├── validation.md       # Data validation rules
│       └── directory_structure.md # File/directory organization
├── pipeline/                   # Pipeline documentation
│   ├── index.md                # Pipeline overview
│   └── cli.md                  # Command-line interface
├── developer_guide/            # Developer documentation
│   ├── README.md               # Developer guide overview
│   ├── ai_assistant_guide.md   # Guide for AI assistants
│   └── documentation_guide.md  # Documentation standards
├── templates/                  # Documentation templates
│   ├── feature_doc.md          # Template for feature documentation
│   └── analysis_report.md      # Template for analysis reports
└── research/                   # Reference materials for methodology
```

## Key Documentation Sections

### Feature System (`/docs/features/`)

Documentation for the feature engineering system that powers our prediction model.

- [Feature System Overview](features/index.md) - Structure and usage of the feature system
- [Feature Reference](features/reference/overview.md) - Complete list of features with complexity and status
- [T01 Win Percentage](features/team_performance/T01_win_percentage.md) - Documentation for Win Percentage feature
- [S01 Effective Field Goal Percentage](features/shooting/S01_effective_field_goal_percentage.md) - Documentation for eFG% feature

### Data Documentation (`/docs/data/`)

Information about the data used in the project, its processing, and organization.

- [Data Overview](data/index.md) - Overview of the data documentation
- [Data Processing](data/processing.md) - Data processing principles and methodology
- [Directory Structure](data/reference/directory_structure.md) - How data files are organized
- [Data Schema](data/reference/schema.md) - Detailed data schemas and column definitions

### Pipeline Documentation (`/docs/pipeline/`)

Documentation specific to the processing pipeline.

- [Pipeline Architecture](pipeline/index.md) - Pipeline design and components
- [CLI Reference](pipeline/cli.md) - Command-line interface documentation

### Developer Documentation (`/docs/developer_guide/`)

Guidelines and instructions for developers working on the project.

- [AI Assistant Guide](developer_guide/ai_assistant_guide.md) - Comprehensive guide for AI coding assistants
- [Documentation Guide](developer_guide/documentation_guide.md) - Documentation standards and processes
- [Developer Overview](developer_guide/README.md) - General developer onboarding

## Core Workflows

### Feature Development Workflow

1. Check the [Feature Reference](features/reference/overview.md) for unimplemented features
2. Follow the [Feature Implementation Guide](features/index.md) to implement a new feature
3. Update the feature registry in [Feature Reference](features/reference/overview.md)
4. Create feature documentation following the [Feature Documentation Template](templates/feature_doc.md)

### Data Processing Workflow

1. Review the [Data Processing Guide](data/processing.md) for principles
2. Follow the [Data Loading](pipeline/index.md) guide for adding new data sources
3. Reference the [Pipeline CLI documentation](pipeline/cli.md) for running data processing

### Analysis Workflow

1. Use the [Analysis Template](templates/analysis_report.md) for consistent reporting
2. Store reports in [reports/findings/](../reports/findings/) following conventions

## External Resources

- [Main GitHub Repository](https://github.com/tim-mcdonnell/march_madness)
- [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/) - Primary data source

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