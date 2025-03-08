# NCAA March Madness Predictor - Features Documentation

## Introduction

This section provides documentation on the features used in the NCAA March Madness Predictor. Features are organized into different sets based on complexity and purpose.

## Implementation Plan

Our feature implementation follows a phased approach as outlined in [Feature Overview](../reference/features/overview.md):

### Current Implementation Status

| Phase | Feature Set | Status | Description |
|-------|------------|--------|-------------|
| Phase 1 | [Foundation](foundation.md) | Implemented | Basic performance metrics for teams |
| Phase 2 | Efficiency Metrics | Planned | Advanced efficiency and tempo-adjusted metrics |
| Phase 3 | Advanced Metrics | Planned | Player-based and detailed game analysis metrics |
| Phase 4 | Complex Sequence Analysis | Planned | Detailed play-by-play derived metrics |

## Feature Sets

### [Foundation Features](foundation.md)

The Foundation features provide essential team performance metrics derived from box score data. They include:

- Simple Shooting Metrics (eFG%, TS%, Three-Point Rate, Free Throw Rate)
- Basic Possession Metrics (Rebound Percentages, Assist Rate, Turnover Percentage)
- Win Percentage breakdowns (home, away, neutral)
- Recent Form and Consistency metrics
- Home Court Advantage rating

## Feature Implementation

All features are implemented using a consistent approach:

1. **Feature Builder**: Each feature set has a corresponding builder class in `src/features/builders/`
2. **Base Data**: Features build on the processed data files in `data/processed/`
3. **Output**: Features are saved to `data/features/` as parquet files
4. **Documentation**: All features are documented in this section

## Usage

To generate features, run:

```bash
python -m src.features.generate --feature-set <feature_set> --output-dir data/features --output-filename <output_filename>
```

Where:
- `<feature_set>` is the name of the feature set to generate (e.g., `foundation`)
- `<output_filename>` is the name of the output file (default: `team_performance.parquet`)

## Feature Organization

Feature columns follow a consistent naming convention:

- Simple metrics use straightforward names (e.g., `efg_pct`)
- Related metrics are grouped with common prefixes (e.g., `home_win_pct`)
- Percentage values end with `_pct` or `_rate`
- Counts or raw values have descriptive suffixes (e.g., `_stddev` for standard deviation)

## Data Flow

The feature generation process follows this data flow:

1. Load processed data from `data/processed/`
2. Calculate features using feature builder classes
3. Join features with base team season statistics
4. Save the resulting features to `data/features/`

## Directory Structure

Features are organized in the repository as follows:

```
src/features/
├── __init__.py            - Package initialization
├── base.py                - Base feature builder class
├── factory.py             - Factory for creating feature builders
├── generate.py            - Feature generation script
└── builders/              - Feature builder implementations
    ├── __init__.py
    └── foundation.py      - Foundation feature builder

docs/features/
├── index.md               - This documentation index
└── foundation.md          - Foundation features documentation

data/features/             - Generated feature files
└── team_performance.parquet  - Combined foundation features
```

> **Note:** The foundation features are saved as `team_performance.parquet`. This naming convention reflects the fact that these features represent the core team performance metrics.

## Next Steps

Future feature development will focus on:

1. Implementing Phase 2 (Efficiency Metrics)
2. Enhancing existing features with opponent adjustments
3. Adding conference-specific metrics
4. Developing tournament-specific features 