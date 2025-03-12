# *This is now depreciated.  Go check out https://github.com/tim-mcdonnell/ncaa-prediction-model for my current work.  I know.  I'm disorganized. My Bad.*




# NCAA March Madness Predictor

A data science approach to building optimal March Madness brackets using historical NCAA men's basketball data.

[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/yourusername/yourgistid/raw/coverage.json)](https://github.com/tim-mcdonnell/march_madness/actions/workflows/badges.yml)
[![Pipeline Status](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/yourusername/yourgistid/raw/pipeline-status.json)](https://github.com/tim-mcdonnell/march_madness/actions/workflows/run_pipeline.yml)

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
march_madness/
├── README.md               # Project overview and documentation
├── requirements.txt        # Python dependencies
├── .gitignore              # Files to exclude from git
├── run_pipeline.py         # Main pipeline execution script
├── config/                 # Configuration files
│   └── pipeline_config.yaml # Pipeline configuration
├── data/                   # Data directory
│   ├── raw/                # Original unmodified data
│   ├── processed/          # Cleaned and transformed data
│   └── README.md           # Data documentation
├── reports/                # Analysis reports and visualizations 
│   ├── findings/           # Markdown reports of analysis findings
│   └── figures/            # Visualizations generated from analysis
├── src/                    # Source code
│   ├── __init__.py
│   ├── data/               # Data processing modules
│   │   ├── __init__.py
│   │   ├── loader.py       # Data loading functions
│   │   └── cleaner.py      # Data cleaning functions
│   ├── eda/                # Exploratory data analysis scripts
│   │   ├── __init__.py
│   │   └── README.md       # EDA documentation and guidelines
│   ├── pipeline/           # Pipeline framework
│   │   ├── __init__.py     # Pipeline package definition
│   │   ├── cli.py          # Command-line interface
│   │   ├── config.py       # Configuration management
│   │   ├── data_management.py # Data cleaning/purging utilities
│   │   ├── data_stage.py   # Data stage implementation
│   │   └── feature_stage.py # Feature calculation stage
│   ├── features/           # Feature engineering
│   │   ├── __init__.py
│   │   ├── core/           # Core feature system components
│   │   │   ├── base.py     # BaseFeature abstract class
│   │   │   ├── registry.py # Feature registry system
│   │   │   ├── loader.py   # Feature loading utilities
│   │   │   └── data_manager.py # Feature data management
│   │   ├── team_performance/ # Team Performance features (T*)
│   │   ├── shooting/       # Shooting features (S*)
│   │   └── ... (other feature categories)
│   ├── models/             # Model code
│   │   ├── __init__.py
│   │   ├── train.py        # Training functions
│   │   └── predict.py      # Prediction functions
│   └── visualization/      # Visualization code
│       ├── __init__.py
│       └── plots.py        # Plotting functions
├── models/                 # Saved model files
│   └── README.md           # Model documentation
├── tests/                  # Test code
│   ├── __init__.py
│   ├── test_data.py
│   └── test_models.py
├── .github/                # GitHub configurations
│   └── workflows/          # GitHub Actions workflow files
│       ├── test.yml        # Testing workflow
│       ├── run_pipeline.yml # Pipeline execution workflow 
│       ├── badges.yml      # Status badges workflow
│       └── docs.yml        # Documentation workflow
└── docs/                   # Project documentation
    ├── index.md            # Documentation index
    ├── features/           # Feature system documentation
    │   ├── index.md        # Feature system overview
    │   ├── team_performance/ # Team performance features
    │   └── shooting/       # Shooting features
    ├── developer_guide/    # Developer guidance
    │   └── ai_assistant_guide.md # Guide for AI assistants
    ├── reference/          # Technical reference
    │   └── features/       # Feature reference
    └── pipeline/           # Pipeline documentation
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
- Python 3.11
- Git
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tim-mcdonnell/march_madness.git
cd march_madness
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

4. Run the pipeline:
```bash
# Run the full pipeline (automatically creates default config if needed)
python run_pipeline.py

# Run only the data collection stage
python run_pipeline.py --stages data

# Create a custom config without running the pipeline (optional)
python run_pipeline.py --create-config --no-run
```

## 🚚 Pipeline Framework

This project includes a modular pipeline framework that manages the end-to-end workflow, from data ingestion to model evaluation.

### Pipeline Components

- **Configuration Management**: YAML-based configuration with validation
- **Data Management**: Utilities for organizing, cleaning, and purging data
- **Modular Stages**: Separate pipeline stages that can run independently
- **Logging**: Comprehensive logging for debugging and tracking progress

### Pipeline Stages

The pipeline is organized into distinct stages with clear responsibilities:

1. **Data Collection**: 
   - Fetches data from sportsdataverse repository 
   - Stores raw files in `data/raw/` directory
   - Does not modify the original data

2. **Data Processing**:
   - Cleans and standardizes raw data (fixing data types, standardizing column names)
   - Combines data across seasons into consistent formats
   - Only includes metrics directly derivable from raw data
   - Does NOT add synthetic values, placeholder data, or calculated metrics
   - Outputs to `data/processed/` directory

3. **Feature Engineering**:
   - Creates derived metrics (efficiency ratings, factors, etc.)
   - Applies transformations (normalization, encoding, etc.)
   - Generates model-ready features
   - Outputs to `data/features/` directory

4. **Model Training**:
   - Trains predictive models using engineered features
   - Tunes hyperparameters
   - Evaluates model performance
   - Saves models to `models/` directory

5. **Bracket Generation**:
   - Applies trained models to create optimized brackets
   - Generates visualizations
   - Outputs to `visualizations/` directory

### Pipeline CLI Options

The pipeline can be run with various options:

```bash
# Run the full pipeline
python run_pipeline.py

# Run only specific stages
python run_pipeline.py --stages data features

# Process specific years
python run_pipeline.py --years 2023 2024 2025

# Process specific data categories
python run_pipeline.py --categories team_box player_box

# Clean data before running
python run_pipeline.py --clean-raw      # Clean raw data
python run_pipeline.py --clean-processed # Clean processed data
python run_pipeline.py --clean-features  # Clean feature data
python run_pipeline.py --clean-models    # Clean model data
python run_pipeline.py --clean-master    # Clean team master data (use with caution)
python run_pipeline.py --clean-all      # Clean all data (except team master)

# Use a custom configuration
python run_pipeline.py --config custom_config.yaml

# Create a config without running the pipeline
python run_pipeline.py --create-config --no-run
```

### Configuration

The pipeline is configured using a YAML file (`config/pipeline_config.yaml`):

```yaml
# Data paths and selections
data:
  raw_dir: "data/raw"
  processed_dir: "data/processed"
  feature_dir: "data/features"
  model_dir: "models"
  results_dir: "results"
  years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
  categories: ["play_by_play", "player_box", "schedules", "team_box"]

# Feature settings
features:
  # Configuration for feature engineering

# Model settings
model:
  # Configuration for model training and evaluation
```

## 📚 Data Dictionary

This section provides a comprehensive reference for all processed data files available in the `data/processed/` directory. These files contain cleaned, standardized data ready for feature engineering and analysis.

### team_season_statistics.parquet

Season-level aggregated statistics for each team across all games played.

| Column | Type | Description |
|--------|------|-------------|
| team_id | integer | Unique identifier for the team |
| team_name | string | Name of the team |
| team_display_name | string | Display name of the team |
| season | integer | Season year (e.g., 2023) |
| games_played | integer | Total number of games played in the season |
| total_points | integer | Total points scored across all games |
| points_per_game | float | Average points per game |
| opponent_points | integer | Total points allowed to opponents |
| opponent_points_per_game | float | Average points allowed per game |
| home_games | integer | Number of home games played |
| away_games | integer | Number of away games played |
| wins | integer | Total number of wins |
| losses | integer | Total number of losses |
| home_wins | integer | Number of wins at home |
| away_wins | integer | Number of wins away |
| avg_point_differential | float | Average point difference (team score - opponent score) |
| win_percentage | float | Percentage of games won (0-1) |
| home_win_pct | float | Percentage of home games won (0-1) |
| away_win_pct | float | Percentage of away games won (0-1) |

**Shape**: 14,080 rows × 19 columns

### team_box.parquet

Game-level team statistics for each team in each game played.

| Column | Type | Description |
|--------|------|-------------|
| assists | integer | Number of assists |
| blocks | integer | Number of blocked shots |
| defensive_rebounds | integer | Number of defensive rebounds |
| fast_break_points | string | Number of points scored on fast breaks |
| field_goal_pct | float | Field goal percentage (made/attempted) |
| field_goals_attempted | integer | Number of field goals attempted |
| field_goals_made | integer | Number of field goals made |
| flagrant_fouls | integer | Number of flagrant fouls committed |
| fouls | integer | Number of fouls committed |
| free_throw_pct | float | Free throw percentage (made/attempted) |
| free_throws_attempted | integer | Number of free throws attempted |
| free_throws_made | integer | Number of free throws made |
| game_date | date | Date of the game |
| game_date_time | datetime | Date and time of the game |
| game_id | integer | Unique identifier for the game |
| largest_lead | integer | Largest lead achieved during the game |
| offensive_rebounds | integer | Number of offensive rebounds |
| team_id | integer | Unique identifier for the team |
| team_name | string | Name of the team |
| team_display_name | string | Display name of the team |
| team_score | integer | Total points scored by the team |
| team_home_away | string | Whether team was home or away ("home"/"away") |
| opponent_team_id | integer | Unique identifier for the opposing team |
| opponent_team_name | string | Name of the opposing team |
| opponent_team_score | integer | Total points scored by the opponent |
| season | integer | Season year (e.g., 2023) |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| steals | integer | Number of steals |
| team_turnovers | integer | Number of team turnovers |
| technical_fouls | integer | Number of technical fouls |
| three_point_field_goal_pct | float | Three-point field goal percentage |
| three_point_field_goals_attempted | integer | Number of three-point field goals attempted |
| three_point_field_goals_made | integer | Number of three-point field goals made |
| total_rebounds | integer | Total number of rebounds |
| total_technical_fouls | integer | Total number of technical fouls |
| total_turnovers | integer | Total number of turnovers (team + individual) |
| turnover_points | string | Points scored off turnovers |
| turnovers | integer | Number of individual player turnovers |

**Shape**: 236,522 rows × 57 columns

### schedules.parquet

Comprehensive game scheduling information for all games played.

| Column | Type | Description |
|--------|------|-------------|
| game_id | integer | Unique identifier for the game |
| season | integer | Season year (e.g., 2023) |
| date | date | Date of the game |
| game_date | date | Game date |
| game_date_time | datetime | Game date and time |
| neutral_site | boolean | Whether game was played at a neutral site |
| home_id | integer | Unique identifier for home team |
| home_name | string | Name of home team |
| home_display_name | string | Display name of home team |
| home_abbreviation | string | Abbreviation of home team |
| home_score | integer | Score of home team |
| away_id | integer | Unique identifier for away team |
| away_name | string | Name of away team |
| away_display_name | string | Display name of away team |
| away_abbreviation | string | Abbreviation of away team |
| away_score | integer | Score of away team |
| home_winner | boolean | Whether home team won |
| away_winner | boolean | Whether away team won |
| conference_competition | boolean | Whether game was between conference opponents |
| attendance | float | Number of spectators at the game |
| venue_id | integer | Unique identifier for the venue |
| venue_full_name | string | Full name of the venue |
| venue_address_city | string | City where venue is located |
| venue_address_state | string | State where venue is located |
| venue_capacity | float | Seating capacity of venue |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| notes_headline | string | Additional game notes |
| notes_type | string | Type of notes (e.g., "NCAA Tournament") |

**Shape**: 130,089 rows × 87 columns

### player_box.parquet

Game-level statistics for individual players in each game.

| Column | Type | Description |
|--------|------|-------------|
| athlete_id | integer | Unique identifier for the player |
| athlete_display_name | string | Full display name of the player |
| athlete_position_name | string | Position of the player |
| athlete_position_abbreviation | string | Abbreviated position of the player |
| athlete_jersey | string | Jersey number of the player |
| team_id | integer | Unique identifier for the player's team |
| team_name | string | Name of the player's team |
| team_display_name | string | Display name of the player's team |
| team_abbreviation | string | Abbreviation of the player's team |
| game_id | integer | Unique identifier for the game |
| game_date | date | Date of the game |
| game_date_time | datetime | Date and time of the game |
| season | integer | Season year (e.g., 2023) |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| home_away | string | Whether the player's team was home or away |
| starter | boolean | Whether the player was a starter |
| active | boolean | Whether the player was active for the game |
| did_not_play | boolean | Whether the player did not play |
| minutes | string | Minutes played |
| points | integer | Total points scored |
| field_goals_made | integer | Number of field goals made |
| field_goals_attempted | integer | Number of field goals attempted |
| three_point_field_goals_made | integer | Number of three-point field goals made |
| three_point_field_goals_attempted | integer | Number of three-point field goals attempted |
| free_throws_made | integer | Number of free throws made |
| free_throws_attempted | integer | Number of free throws attempted |
| rebounds | integer | Total number of rebounds |
| offensive_rebounds | integer | Number of offensive rebounds |
| defensive_rebounds | integer | Number of defensive rebounds |
| assists | integer | Number of assists |
| steals | integer | Number of steals |
| blocks | integer | Number of blocked shots |
| turnovers | integer | Number of turnovers |
| fouls | integer | Number of fouls committed |
| ejected | boolean | Whether the player was ejected |
| team_score | integer | Score of the player's team |
| opponent_team_id | integer | Unique identifier for the opposing team |
| opponent_team_name | string | Name of the opposing team |
| opponent_team_score | integer | Score of the opposing team |
| team_winner | boolean | Whether the player's team won |

**Shape**: 3,452,347 rows × 55 columns

### play_by_play.parquet

Detailed event-level data for each play in each game.

| Column | Type | Description |
|--------|------|-------------|
| game_id | integer | Unique identifier for the game |
| game_play_number | integer | Sequential play number within the game |
| sequence_number | integer | Sequence number of the play |
| period | integer | Period of the game (1=1st half, 2=2nd half, etc.) |
| period_number | integer | Numerical period indicator |
| period_display_value | string | Display text for the period (e.g., "1st") |
| home_score | integer | Home team score at this point in the game |
| away_score | integer | Away team score at this point in the game |
| clock_display_value | string | Display of the game clock |
| clock_minutes | integer | Minutes on game clock |
| clock_seconds | integer | Seconds on game clock |
| team_id | integer | ID of the team involved in the play |
| home_team_id | integer | ID of the home team |
| home_team_name | string | Name of the home team |
| home_team_mascot | string | Mascot of the home team |
| away_team_id | integer | ID of the away team |
| away_team_name | string | Name of the away team |
| away_team_mascot | string | Mascot of the away team |
| type_id | integer | ID of the play type |
| type_text | string | Description of the play type (e.g., "JumpShot", "Rebound") |
| text | string | Full text description of the play |
| score_value | integer | Point value of the play if scoring play |
| scoring_play | boolean | Whether the play resulted in points |
| shooting_play | boolean | Whether the play was a shot attempt |
| athlete_id_1 | integer | ID of the primary player involved |
| athlete_id_2 | integer | ID of the secondary player involved (if applicable) |
| coordinate_x | float | X-coordinate location of the play |
| coordinate_y | float | Y-coordinate location of the play |
| home_timeout_called | boolean | Whether home team called timeout |
| away_timeout_called | boolean | Whether away team called timeout |
| season | integer | Season year (e.g., 2023) |
| season_type | integer | Type of season (1=preseason, 2=regular, 3=postseason) |
| start_game_seconds_remaining | integer | Seconds remaining in the game at start of play |
| end_game_seconds_remaining | integer | Seconds remaining in the game at end of play |
| start_period_seconds_remaining | integer | Seconds remaining in the period at start of play |
| end_period_seconds_remaining | integer | Seconds remaining in the period at end of play |

**Shape**: 28,830,165 rows × 67 columns

## 🔄 CI/CD Workflow

This project uses GitHub Actions for continuous integration and deployment, ensuring code quality and automating routine tasks.

### Automated Workflows

- **Testing**: Automatically runs tests on all pull requests and pushes to main branches
- **Pipeline Execution**: Daily scheduled runs to update data during the basketball season
- **Documentation**: Automatically builds and publishes documentation to GitHub Pages
- **Status Badges**: Generates coverage and status badges for the repository

### GitHub Actions Configuration

Our CI/CD workflows are defined in the `.github/workflows` directory:

```
.github/workflows/
├── test.yml           # Runs tests on PRs and pushes
├── run_pipeline.yml   # Scheduled pipeline execution
├── badges.yml         # Generates status badges
└── docs.yml           # Builds and deploys documentation
```

### Manual Workflow Triggers

Most workflows can also be triggered manually through the GitHub Actions interface:

1. Navigate to the Actions tab in the GitHub repository
2. Select the workflow you want to run
3. Click "Run workflow"
4. Configure any input parameters
5. Start the workflow

### Pipeline Status Dashboard

During basketball season, a status dashboard is automatically updated daily showing:
- Last successful data ingestion
- Current data coverage
- Model performance metrics
- Prediction confidence scores

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

## 💻 Development Best Practices

To maintain consistency across the project, please follow these key practices:

### Data Processing

1. **Use Polars, not Pandas**
   ```python
   import polars as pl
   data = pl.read_parquet(file_path)  # ✓
   # import pandas as pd  # ✗
   ```

2. **Use pathlib for file paths**
   ```python
   from pathlib import Path
   file_path = Path(config.data.raw_dir) / category / f"{year}.parquet"  # ✓
   # file_path = config.data.raw_dir + "/" + category + "/" + str(year) + ".parquet"  # ✗
   ```

3. **Follow data storage conventions**
   - Raw data: `data/raw/{category}/{year}.parquet`
   - Processed data: `data/processed/{category}/{year}.parquet`
   - Features: `data/features/{feature_set}/{year}.parquet`

4. **Use explicit schemas**
   ```python
   schema = {"field": pl.Int64, "name": pl.Utf8}
   df = pl.read_parquet(path, schema=schema)  # ✓
   # df = pl.read_parquet(path)  # No schema ✗
   ```

5. **Proper error handling**
   ```python
   try:
       data = pl.read_parquet(file_path)
   except pl.exceptions.NoDataError:
       logger.error(f"File contains no data: {file_path}")
       return None
   except Exception as e:
       logger.exception(f"Error loading data from {file_path}: {e}")
       raise
   ```

### Common Pitfalls to Avoid

- ❌ Using pandas instead of polars
- ❌ Hardcoding file paths or using string concatenation
- ❌ Writing data to incorrect locations
- ❌ Not following the modular pipeline architecture
- ❌ Using print instead of proper logging
- ❌ Ignoring configuration values
- ❌ Not handling errors properly
- ❌ Not including type hints

For a more comprehensive guide on working with this codebase, please refer to our [AI Assistant Guide](docs/ai_assistant_guide.md).

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
   - Test EDA script functions

2. **EDA Script Validation**: For analysis scripts
   - Validate that EDA scripts run end-to-end without errors
   - Check that output files (reports and figures) are generated correctly
   - Ensure consistency in reporting format

3. **Model Evaluation**: For predictive models
   - Cross-validation performance metrics
   - Backtesting on historical tournaments
   - Out-of-sample testing

## 📝 Documentation Standards

1. **Code Documentation**
   - All functions should have docstrings (NumPy or Google style)
   - Complex algorithms should include inline comments
   - Include type hints where appropriate

2. **EDA Documentation**
   - Each EDA script should have detailed docstrings explaining its purpose
   - Scripts should generate structured markdown reports in `reports/findings/`
   - All visualizations should be saved to `reports/figures/` with clear naming
   - Reports should follow the template structure in `reports/findings/README.md`

3. **Project Documentation**
   - README files in each directory explaining its purpose
   - Methodology document explaining the overall approach
   - Model cards for trained models describing their performance
   - [AI Assistant Guide](docs/ai_assistant_guide.md): Essential guide for AI coding assistants
   - [Pipeline Documentation](docs/pipeline/README.md): Details on the pipeline architecture and usage
   - [Data Processing](docs/data_processing.md): Information on data processing principles

The documentation is organized by topic and includes both high-level overviews and detailed technical references.

## 🔗 Resources

- [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data/) - Our primary data source
- [hoopR R Package](https://hoopr.sportsdataverse.org/) - R package for accessing NCAA basketball data
- [Kaggle March Madness Competitions](https://www.kaggle.com/c/mens-march-mania-2022) - Previous competitions on predicting March Madness
- [NCAA Tournament History](https://www.ncaa.com/news/basketball-men/article/2023-02-22/march-madness-brackets-how-do-seeds-perform-ncaa-tournament) - Historical performance of tournament seeds

## 📚 Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- [Documentation Index](docs/index.md): Main documentation entry point with navigation to all sections
- [Feature System](docs/features/index.md): The feature engineering system
- [Data Documentation](docs/data/index.md): Information about data organization and processing
- [Pipeline Documentation](docs/pipeline/index.md): The pipeline architecture and CLI
- [Developer Guide](docs/developer_guide/README.md): Information for developers

Visit the [Documentation Index](docs/index.md) for a complete overview of all available documentation.
