# NCAA March Madness Predictor: DuckDB Architecture

## 1. Overview

This document outlines the architecture and implementation strategy for rebuilding the NCAA March Madness Predictor using DuckDB as the central data engine. This approach simplifies the data stack while maintaining high performance for feature calculation and model training.

### 1.1 Goals

- Create a unified, high-performance data architecture
- Simplify feature development and computation
- Maintain the existing feature ID system
- Support both simple and complex feature calculations
- Enable efficient model training and bracket optimization
- Minimize infrastructure requirements (laptop-friendly)

### 1.2 Current Pain Points Addressed

- Inconsistent data quality from hoopR's preprocessed data
- Complex pipeline with multiple data transformation steps
- Slow performance for complex feature calculations
- Technical debt from data cleaning and harmonization

## 2. Architecture

### 2.1 High-Level Architecture

```
┌───────────────────┐     ┌──────────────────────┐     ┌───────────────────┐
│  ESPN API Client  │     │    DuckDB Database   │     │  Feature Registry │
│  ---------------  │     │  ------------------  │     │  --------------   │
│ - Direct API calls│────▶│ - Raw data tables    │────▶│ - Feature ID      │
│ - Data validation │     │ - Feature views      │     │ - SQL definitions │
└───────────────────┘     │ - Materialized views │     │ - Python helpers  │
                          └──────────────────────┘     └────────┬──────────┘
                                                                │
                                                                ▼
                          ┌──────────────────────┐     ┌───────────────────┐
                          │  ML Model Training   │     │  Python Extension │
                          │  ------------------  │◀────│  --------------   │
                          │ - PyTorch models     │     │ - Complex features│
                          │ - Feature extraction │     │ - Algorithms      │
                          └──────────────────────┘     └───────────────────┘
```

### 2.2 Key Components

1. **ESPN API Client**: Direct data acquisition from ESPN's API endpoints
2. **DuckDB Database**: Central data storage and query engine
3. **Feature Registry**: Maintained from existing FEATURES.md organization
4. **Python Extensions**: For complex algorithmic features
5. **ML Model System**: PyTorch models for game predictions
6. **Bracket Optimization**: Generation of optimal brackets

## 3. Tech Stack

### 3.1 Core Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Storage & Query** | DuckDB | Primary database and analytical engine |
| **API Client** | Python + Requests | Data acquisition from ESPN |
| **Data Validation** | Pydantic | Schema validation and type checking |
| **Feature Implementation** | SQL + Python | Feature computation |
| **Machine Learning** | PyTorch | Model training and inference |
| **Data Science** | NumPy, pandas, scikit-learn | Data manipulation and analysis |
| **Visualization** | Matplotlib, Plotly | Data visualization and reporting |
| **Testing** | pytest | Unit and integration testing |

### 3.2 Key Libraries & Versions

```
duckdb>=0.9.0
requests>=2.28.0
pydantic>=2.0.0
torch>=2.0.0
pandas>=2.0.0
numpy>=1.23.0
matplotlib>=3.6.0
plotly>=5.10.0
pytest>=7.0.0
```

## 4. Project Structure

```
march_madness/
├── src/
│   ├── api/                     # ESPN API client
│   │   ├── client.py            # Core HTTP client
│   │   ├── endpoints.py         # API endpoint definitions
│   │   └── validators.py        # Response validation
│   ├── db/                      # Database management
│   │   ├── connection.py        # DuckDB connection management
│   │   ├── schema.py            # Table definitions
│   │   └── migrations/          # Schema migrations
│   ├── features/                # Feature system
│   │   ├── registry.py          # Feature registry
│   │   ├── base.py              # Base feature class
│   │   ├── sql/                 # SQL feature definitions 
│   │   │   ├── team_performance/# SQL for team features
│   │   │   ├── shooting/        # SQL for shooting features
│   │   │   └── ...              # Other feature categories
│   │   └── python/              # Python-based features
│   │       ├── algorithms.py    # Complex algorithms
│   │       └── complex/         # Complex feature implementations
│   ├── models/                  # ML models
│   │   ├── dataset.py           # PyTorch dataset creation
│   │   ├── architectures.py     # Model definitions
│   │   └── training.py          # Model training logic
│   └── visualization/           # Bracket visualization
│       ├── bracket.py           # Bracket generation
│       └── reporting.py         # Analysis reporting
├── scripts/                     # Utility scripts
│   ├── data_import.py           # Import data to DuckDB
│   ├── feature_compute.py       # Feature computation script
│   └── model_train.py           # Model training script
├── tests/                       # Tests
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test fixtures
├── notebooks/                   # Jupyter notebooks
│   ├── exploration/             # Data exploration
│   └── analysis/                # Result analysis
├── data/                        # Data storage
│   ├── basketball.duckdb        # Main DuckDB database
│   └── backup/                  # Database backups
├── .gitignore                   # Git ignore file
├── requirements.txt             # Dependencies
├── FEATURES.md                  # Feature registry
├── ARCHITECTURE.md              # This document
└── run.py                       # Main CLI entry point
```

## 5. Data Model

### 5.1 Core Tables

| Table | Description | Primary Key |
|-------|-------------|------------|
| `teams` | Team reference data | `team_id` |
| `games` | Game schedules and outcomes | `game_id` |
| `team_box` | Team performance statistics | `game_id`, `team_id` |
| `player_box` | Player performance statistics | `game_id`, `player_id` |
| `play_by_play` | Detailed play-by-play events | `game_id`, `sequence_number` |
| `tournaments` | Tournament information | `tournament_id`, `season` |

### 5.2 Feature Views/Tables

| View/Table | Description | Implementation |
|------------|-------------|----------------|
| `feature_T01_win_percentage` | Team win percentages | SQL View |
| `feature_S01_effective_fg_pct` | Effective field goal percentage | SQL View |
| `feature_A02_kill_shots` | 10-0 scoring runs | Python + SQL Table |

### 5.3 Schema Example

```sql
-- Example schema for teams table
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY,
    team_uid VARCHAR,
    team_location VARCHAR,
    team_name VARCHAR,
    team_abbreviation VARCHAR,
    team_display_name VARCHAR,
    team_color VARCHAR,
    team_alternate_color VARCHAR,
    team_logo VARCHAR,
    first_season INTEGER,
    last_season INTEGER
);

-- Example schema for games table
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY,
    season INTEGER,
    season_type INTEGER,
    game_date DATE,
    game_time TIMESTAMP,
    neutral_site BOOLEAN,
    venue_id INTEGER,
    venue_name VARCHAR,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    home_winner BOOLEAN,
    tournament_id INTEGER,
    tournament_round INTEGER
);
```

## 6. Feature Implementation

### 6.1 SQL-Based Features

Simple to moderate complexity features (1-3) will be implemented as SQL views:

```sql
-- T01: Win Percentage (Complexity: 1)
CREATE OR REPLACE VIEW feature_T01_win_percentage AS
SELECT 
    team_id,
    season,
    COUNT(*) AS games_played,
    SUM(CASE WHEN team_winner = true THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN team_winner = true THEN 1 ELSE 0 END) / COUNT(*)::FLOAT AS win_percentage,
    -- Split by location
    SUM(CASE WHEN team_home_away = 'home' AND team_winner = true THEN 1 ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN team_home_away = 'home' THEN 1 ELSE 0 END), 0)::FLOAT AS home_win_percentage,
    SUM(CASE WHEN team_home_away = 'away' AND team_winner = true THEN 1 ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN team_home_away = 'away' THEN 1 ELSE 0 END), 0)::FLOAT AS away_win_percentage,
    SUM(CASE WHEN neutral_site = true AND team_winner = true THEN 1 ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN neutral_site = true THEN 1 ELSE 0 END), 0)::FLOAT AS neutral_win_percentage
FROM team_box
JOIN games ON team_box.game_id = games.game_id
GROUP BY team_id, season;
```

### 6.2 Python-Extended Features

Complex features (4-5) will use Python with DuckDB:

```python
# A02: Kill Shots Per Game (Complexity: 4)
class KillShotsFeature:
    """Calculate 10-0 or better scoring runs."""
    
    id = "A02"
    name = "Kill Shots Per Game"
    category = "advanced_team"
    
    def calculate(self, conn, min_run=10):
        # Get play-by-play data
        play_data = conn.execute("""
            SELECT
                game_id,
                team_id,
                sequence_number,
                score_value,
                period_number,
                home_team_id,
                away_team_id
            FROM play_by_play
            WHERE score_value > 0
            ORDER BY game_id, sequence_number
        """).fetchdf()
        
        # Process with Python algorithm to find scoring runs
        kill_shots = self._identify_scoring_runs(play_data, min_run)
        
        # Aggregate to team level
        team_kill_shots = self._aggregate_to_team_level(kill_shots)
        
        # Store results in DuckDB
        conn.execute("CREATE OR REPLACE TABLE feature_A02_kill_shots AS SELECT * FROM team_kill_shots")
        
        return team_kill_shots
    
    def _identify_scoring_runs(self, play_data, min_run):
        # Algorithm implementation
        # ...
        return kill_shots_df
    
    def _aggregate_to_team_level(self, kill_shots):
        # Aggregate runs to team level
        # ...
        return team_level_df
```

### 6.3 Feature Registry Integration

The feature registry will maintain the existing ID system from FEATURES.md:

```python
# Feature registry example
FEATURES = {
    "T01": {
        "id": "T01",
        "name": "Win Percentage",
        "category": "team_performance",
        "complexity": 1,
        "type": "sql",
        "file": "team_performance/win_percentage.sql",
        "dependencies": []
    },
    "A02": {
        "id": "A02",
        "name": "Kill Shots Per Game",
        "category": "advanced_team",
        "complexity": 4,
        "type": "python",
        "class": "KillShotsFeature",
        "dependencies": []
    },
    # Other features...
}
```

## 7. Development Workflow

### 7.1 Data Acquisition

1. Fetch data from ESPN API
2. Validate and transform responses
3. Load into DuckDB raw tables
4. Apply schema migrations if needed

### 7.2 Feature Development

1. Register feature in `FEATURES.md`
2. Implement SQL view or Python class
3. Test feature calculation
4. Document implementation details

### 7.3 Model Training

1. Query feature data from DuckDB
2. Convert to PyTorch dataset
3. Train and evaluate models
4. Save model artifacts

### 7.4 Bracket Generation

1. Load trained models
2. Generate predictions for tournament matchups
3. Optimize bracket selections
4. Visualize and export brackets

## 8. Migration Strategy

### 8.1 Phase 1: Data Foundation (Weeks 1-2)

1. Create DuckDB schema
2. Implement ESPN API client
3. Import historical data
4. Validate data quality

### 8.2 Phase 2: Feature Migration (Weeks 3-4)

1. Implement core feature framework
2. Port simple features (complexity 1-2)
3. Develop and test complex features (complexity 3-5)
4. Validate against existing feature calculations

### 8.3 Phase 3: Model Integration (Weeks 5-6)

1. Build PyTorch integration
2. Port existing models
3. Validate prediction accuracy
4. Optimize performance

### 8.4 Phase 4: Bracket System (Weeks 7-8)

1. Implement bracket generation
2. Create visualization tools
3. Build evaluation metrics
4. End-to-end testing

## 9. Database Management

### 9.1 Backup Strategy

1. Regular snapshots of the DuckDB file
2. Versioned backups before major changes
3. Export of critical data to Parquet for long-term storage

### 9.2 Performance Optimization

1. Use indexes for frequently queried columns
2. Materialize complex views for repeated access
3. Implement caching for expensive computations
4. Configure appropriate memory settings

## 10. Testing Strategy

### 10.1 Unit Tests

1. API client components
2. Feature calculations
3. Model components

### 10.2 Integration Tests

1. End-to-end data pipeline
2. Feature computation pipeline
3. Model training workflow

### 10.3 Validation Tests

1. Data quality checks
2. Feature calculation accuracy
3. Model performance metrics

## 11. Next Steps

1. Set up initial DuckDB database
2. Create ESPN API client
3. Import historical data
4. Implement first set of features
5. Perform performance benchmarks

## 12. Resources

- [DuckDB Documentation](https://duckdb.org/docs/)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Project GitHub Repository](https://github.com/tim-mcdonnell/march_madness) 