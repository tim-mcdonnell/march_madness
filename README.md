# NCAA March Madness Predictor

A data science approach to building optimal March Madness brackets using historical NCAA men's basketball data.

## 📋 Project Overview

This project aims to develop a machine learning model that predicts NCAA March Madness tournament outcomes using 22 years of historical data. By analyzing team statistics, tournament performance, and other relevant factors, we'll create a data-driven approach to bracket construction that outperforms traditional methods.

### Key Objectives
- Process and analyze 22 years of NCAA men's basketball data
- Identify key statistical features that predict tournament success
- Develop a neural network model for game outcome prediction
- Create visualizations to communicate insights and model performance
- Generate optimized bracket recommendations

## 📊 Data Sources

This project exclusively uses data from the sportsdataverse's hoopR-mbb-data GitHub repository, which provides comprehensive NCAA men's basketball data:

- **Repository**: [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/)

The data is organized as parquet files in four main categories:

1. **Play-by-Play Data**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/pbp/parquet/play_by_play_{YEAR}.parquet`
   - Contains detailed event-level data for each game

2. **Player Box Scores**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/player_box/parquet/player_box_{YEAR}.parquet`
   - Contains individual player statistics for each game

3. **Game Schedules**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/schedules/parquet/mbb_schedule_{YEAR}.parquet`
   - Contains game scheduling information including date, time, location, etc.

4. **Team Box Scores**
   - URL pattern: `https://github.com/sportsdataverse/hoopR-mbb-data/raw/refs/heads/main/mbb/team_box/parquet/team_box_{YEAR}.parquet`
   - Contains team-level statistics for each game

These files are available for seasons 2003 through 2025, providing us with 22+ years of historical data.

## 🏗️ Project Structure

```
ncaa-march-madness-predictor/
├── README.md               # Project overview and documentation
├── requirements.txt        # Python dependencies
├── .gitignore              # Files to exclude from git
├── data/                   # Data directory
│   ├── raw/                # Original unmodified data
│   ├── processed/          # Cleaned and transformed data
│   └── README.md           # Data documentation
├── notebooks/              # Jupyter notebooks
│   ├── 01_data_cleaning.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_model_development.ipynb
│   └── 05_evaluation.ipynb
├── src/                    # Source code
│   ├── __init__.py
│   ├── data/               # Data processing modules
│   │   ├── __init__.py
│   │   ├── loader.py       # Data loading functions
│   │   └── cleaner.py      # Data cleaning functions
│   ├── features/           # Feature engineering
│   │   ├── __init__.py
│   │   └── builders.py     # Feature creation functions
│   ├── models/             # Model code
│   │   ├── __init__.py
│   │   ├── train.py        # Training functions
│   │   └── predict.py      # Prediction functions
│   └── visualization/      # Visualization code
│       ├── __init__.py
│       └── plots.py        # Plotting functions
├── models/                 # Saved model files
│   └── README.md           # Model documentation
├── visualizations/         # Output visualization files
│   └── README.md           # Visualization documentation
├── tests/                  # Test code
│   ├── __init__.py
│   ├── test_data.py
│   └── test_models.py
└── docs/                   # Additional documentation
    └── methodology.md      # Detailed methodology documentation
```

## 🔧 Technology Stack

This project uses a modern Python-based data science stack:

- **Python 3.11+**: Core programming language
- **uv**: Fast Python package manager and virtual environment tool
- **Polars**: High-performance DataFrame library for data manipulation
- **PyTorch**: Deep learning framework for neural network models
- **Plotly Dash**: Interactive visualization framework
- **Parquet/PyArrow**: Efficient columnar storage format for data
- **ruff**: Fast Python linter and formatter

This stack was chosen for its performance, particularly when working with large datasets like our 22 years of NCAA basketball data.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Git
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tim-mcdonnell/march_madness.git
cd ncaa-march-madness
```

2. Create a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Set up data ingestion pipeline (see detailed instructions in the data README)

## 🔍 Code Standards

This project uses [ruff](https://github.com/astral-sh/ruff) for maintaining code quality and consistency:

- **Linting**: Ruff provides fast Python linting to catch errors and enforce style
- **Formatting**: Consistent code formatting across the entire codebase
- **Style Guide**: We follow PEP 8 conventions with adjustments specified in `pyproject.toml`

### Configuration

Our ruff configuration is defined in `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 88
indent-width = 4
select = ["E", "F", "B", "I", "N", "UP", "ANN", "S", "A", "C4", "T10", "RET"]
ignore = ["ANN101"]  # Missing type annotation for `self`

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

[tool.ruff.isort]
known-first-party = ["src"]
```

### Development Workflow with Ruff

1. Run linting before committing:
   ```bash
   ruff check .
   ```

2. Apply automatic fixes:
   ```bash
   ruff check --fix .
   ```

3. Format code:
   ```bash
   ruff format .
   ```

Our CI/CD pipeline will enforce these standards, so please ensure your code passes ruff checks before submitting pull requests.

## 📅 Data Refresh Workflow

Our project requires daily updates during the active NCAA basketball season:

1. **Daily Data Pull**: Every day at 8:00 AM CST, we pull the refreshed 2025 season files after they've been recalculated by sportsdataverse
2. **Model Refresh**: After new data is ingested, our models are retrained or updated to incorporate the latest game results
3. **Prediction Update**: Tournament predictions and bracket recommendations are regenerated based on the updated models

This automated workflow ensures our predictions remain current with the latest available data throughout the season.

## 🧠 Development Workflow

This project uses a structured workflow optimized for collaboration with AI tools like GitHub Copilot and Cursor AI.

### Issue Management

We use a two-level approach to GitHub issues:

1. **Milestone Issues**: High-level phases of the project
   - Data Collection and Cleaning
   - Exploratory Data Analysis
   - Feature Engineering
   - Model Development
   - Evaluation and Visualization
   - Documentation

2. **Task Issues**: Specific, well-defined tasks linked to milestone issues
   - Each task includes clear objectives, context, inputs/outputs, and acceptance criteria
   - Optimized for AI collaboration

### Task Structure Example

```
Title: Implement Team Efficiency Rating Function

Context:
We're analyzing NCAA basketball data to predict March Madness outcomes.
The team_stats.csv contains season-level statistics for all teams.

Task:
Create a function that calculates a composite efficiency rating for each team.

Input: DataFrame with columns [team_id, points_pg, rebounds_pg, assists_pg, turnovers_pg]
Output: DataFrame with original columns plus [offensive_rating, defensive_rating, overall_efficiency]

Acceptance Criteria:
- Function is well-documented with docstrings
- Includes unit tests
- Handles missing values appropriately
- Returns normalized ratings between 0-1

Related Files:
- /src/features/team_metrics.py (add function here)
- /data/team_stats.csv (sample data)
```

### Branching Strategy

We follow a simplified git branching strategy:

- `main` - Always contains stable, working code
- `dev` - Primary development branch
- Feature branches - For specific features or tasks (e.g., `feature/data-cleaning`)

### Workflow Example

1. Select an issue to work on
2. Create a new branch from `dev`: `git checkout -b feature/your-feature-name`
3. Write code to address the issue
4. Commit changes with meaningful messages referencing issue numbers
5. Push branch to GitHub: `git push origin feature/your-feature-name`
6. Create a pull request to merge into `dev`
7. Review code (self-review or AI-assisted review)
8. Merge into `dev` and close the issue
9. Periodically merge `dev` into `main` when stable milestones are reached

## 🧪 Testing Strategy

We use a multi-level testing approach:

1. **Unit Tests**: For core functions in the `src` directory
   - Test data processing functions
   - Test model utility functions
   - Test visualization helpers

2. **Notebook Validation**: For analysis notebooks
   - Use [nbval](https://github.com/computationalmodelling/nbval) to validate notebooks
   - Ensure notebooks run end-to-end without errors

3. **Model Evaluation**: For predictive models
   - Cross-validation performance metrics
   - Backtesting on historical tournaments
   - Out-of-sample testing

## 📝 Documentation Standards

1. **Code Documentation**
   - All functions should have docstrings (NumPy or Google style)
   - Complex algorithms should include inline comments
   - Include type hints where appropriate

2. **Notebook Documentation**
   - Each notebook should begin with a markdown cell explaining its purpose
   - Use markdown cells to explain the thought process and conclusions
   - Include visualizations with interpretations

3. **Project Documentation**
   - README files in each directory explaining its purpose
   - Methodology document explaining the overall approach
   - Model cards for trained models describing their performance

## 👥 Contributing

[PLACEHOLDER: Add contribution guidelines]

## 📜 License

[PLACEHOLDER: Add license information]

## 🔗 Resources

- [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/) - Our primary data source
- [hoopR R Package](https://hoopr.sportsdataverse.org/) - R package for accessing NCAA basketball data
- [Kaggle March Madness Competitions](https://www.kaggle.com/c/mens-march-mania-2022) - Previous competitions on predicting March Madness
- [NCAA Tournament History](https://www.ncaa.com/news/basketball-men/article/2023-02-22/march-madness-brackets-how-do-seeds-perform-ncaa-tournament) - Historical performance of tournament seeds
