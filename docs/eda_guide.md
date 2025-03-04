# EDA Guide for AI Assistants - NCAA March Madness Predictor

This guide provides specific instructions for AI assistants on how to approach Exploratory Data Analysis (EDA) tasks for the NCAA March Madness Predictor project. It supplements the main AI Assistant Guide (`ai_assistant_guide.md`) and should be used when implementing EDA-related requests.

## 1. EDA Purpose & Approach

Exploratory Data Analysis in this project serves to:

1. Uncover patterns in NCAA basketball data that correlate with tournament success
2. Identify key features for predictive modeling
3. Generate visualizations that communicate insights effectively
4. Document findings in structured, reproducible reports

### Core EDA Principles

- **Iterative Exploration**: Start with broad questions, then focus on specific insights
- **Visual Confirmation**: Support numerical findings with appropriate visualizations
- **Statistical Rigor**: Apply appropriate statistical tests to validate observations
- **Reproducibility**: Create scripts that can be rerun with the same results
- **Clear Documentation**: Produce comprehensive reports following the project template

## 2. EDA Script Structure

All EDA scripts should follow this modular structure:

```python
#!/usr/bin/env python3
"""
[Script Title]

This EDA script [one-sentence description of purpose]

Analysis objectives:
1. [Objective 1]
2. [Objective 2]
...

Output:
- [Output 1]
- [Output 2]
...
"""

import os
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger('[script_name_logger]')

# Define output directories
REPORTS_DIR = os.path.join('reports', 'findings')
FIGURES_DIR = os.path.join('reports', 'figures')
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def load_data():
    """
    Load and prepare the necessary datasets for analysis.
    
    Returns:
        tuple: Datasets needed for the analysis
    """
    # Implementation
    pass

def [analysis_function_1](data):
    """
    [Description of analysis function]
    
    Args:
        data: Data to analyze
        
    Returns:
        dict: Results of the analysis
    """
    # Implementation
    pass

def [analysis_function_2](data):
    """
    [Description of analysis function]
    
    Args:
        data: Data to analyze
        
    Returns:
        dict: Results of the analysis
    """
    # Implementation
    pass

def generate_visualizations(analysis_results):
    """
    Generate visualizations based on analysis results.
    
    Args:
        analysis_results: Results from analysis functions
        
    Returns:
        dict: Paths to generated visualizations
    """
    # Implementation
    pass

def generate_report(analysis_results, vis_paths):
    """
    Generate a comprehensive markdown report of findings.
    
    Args:
        analysis_results: Results from analysis functions
        vis_paths: Paths to visualization files
        
    Returns:
        str: Path to the generated report
    """
    # Implementation
    pass

def main():
    """Main execution function."""
    logger.info("Starting [analysis name]")
    
    # Load data
    logger.info("Loading data...")
    data = load_data()
    
    # Conduct analysis
    logger.info("Analyzing...")
    analysis_results = [analysis_function](data)
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    vis_paths = generate_visualizations(analysis_results)
    
    # Generate report
    logger.info("Generating analysis report...")
    report_path = generate_report(analysis_results, vis_paths)
    
    logger.info(f"Analysis completed successfully. Report available at: {report_path}")

if __name__ == "__main__":
    main()
```

## 3. Implementing EDA Requests

When you receive an EDA request, follow these steps:

### 3.1 Clarify Requirements & Scope

1. **Identify the core question**: What specific insight is the EDA trying to uncover?
2. **Define acceptance criteria**: What outputs are expected (visualizations, metrics, reports)?
3. **Determine data sources**: Which datasets from `data/processed/` are needed?
4. **Scope the analysis**: What level of detail is appropriate?

### 3.2 Implementation Approach

1. **Progressive Development**:
   - Start with data loading and basic exploration
   - Implement core analysis functions one by one
   - Generate visualizations after analysis is complete
   - Finalize with report generation

2. **Modular Design**:
   - Create separate functions for each analysis component
   - Use descriptive function names that indicate purpose
   - Document each function with clear docstrings
   - Return structured results from analysis functions

3. **Error Handling & Validation**:
   - Add data validation in the load_data function
   - Include robust error handling with informative messages
   - Check for edge cases (missing data, small sample sizes)
   - Add logging at appropriate points

## 4. Data Loading Best Practices

Always use Polars for data manipulation:

```python
def load_data():
    """
    Load and prepare the necessary datasets for analysis.
    
    Returns:
        tuple: Processed datasets ready for analysis
    """
    logger.info("Loading data...")
    
    # Load schedules data
    schedules_df = pl.read_parquet('data/processed/schedules.parquet')
    logger.info(f"Loaded schedules data with {schedules_df.shape[0]} rows")
    
    # Load team statistics data
    team_stats_df = pl.read_parquet('data/processed/team_season_statistics.parquet')
    logger.info(f"Loaded team stats with {team_stats_df.shape[0]} rows")
    
    # Additional data processing if needed
    # ...
    
    return schedules_df, team_stats_df
```

Key principles:
- Always check data shapes and log them
- Handle missing data explicitly
- Include data validation to catch issues early
- Return clearly named variables

## 5. Analysis Functions

Design analysis functions to be focused on a single aspect:

```python
def analyze_conference_performance(tournament_games, team_stats_df):
    """
    Analyze NCAA tournament performance by conference.
    
    Args:
        tournament_games (pl.DataFrame): DataFrame of tournament games
        team_stats_df (pl.DataFrame): DataFrame of team statistics
        
    Returns:
        dict: Conference performance metrics
    """
    logger.info("Analyzing conference performance...")
    
    # Create results dictionary
    conference_results = {}
    
    # Analysis implementation
    # ...
    
    logger.info(f"Analyzed performance for {len(conference_results)} conferences")
    return conference_results
```

### Analysis Function Guidelines:

1. **Focus on one analysis aspect per function**
2. **Use consistent return structures** (dictionaries are preferred)
3. **Log progress, especially for long-running operations**
4. **Include count information in logs** (e.g., "Analyzed X conferences")
5. **Track metrics consistently** (win rates, point differentials, etc.)

## 6. Visualization Best Practices

Generate clear, informative visualizations:

```python
def generate_visualizations(conference_results, team_results):
    """
    Generate visualizations for the analysis.
    
    Args:
        conference_results (dict): Conference performance results
        team_results (dict): Team performance results
        
    Returns:
        dict: Paths to generated visualizations
    """
    logger.info("Generating visualizations...")
    vis_paths = {}
    
    # Generate conference win rates visualization
    conf_win_rates = [
        {'Conference': conf_name, 'Win Rate': data['win_rate'], 'Games': data['total_games']} 
        for conf_name, data in conference_results.items()
        if data['total_games'] >= 10  # Only include conferences with enough games
    ]
    conf_win_rates_df = pl.DataFrame(conf_win_rates).sort('Win Rate', descending=True)
    
    fig = px.bar(
        conf_win_rates_df.to_pandas(), 
        x='Conference', 
        y='Win Rate',
        title='NCAA Tournament Win Rates by Conference (Min. 10 Games)',
        color='Games',
        color_continuous_scale='Viridis',
        height=600
    )
    fig.update_layout(xaxis_tickangle=-45)
    
    # Save visualization
    png_path = os.path.join(FIGURES_DIR, 'conference_win_rates.png')
    fig.write_image(png_path)
    vis_paths['conference_win_rates'] = png_path
    
    logger.info(f"Generated {len(vis_paths)} visualizations")
    return vis_paths
```

### Visualization Guidelines:

1. **Generate PNG files** for embedding in markdown reports
2. **Use meaningful titles and axis labels**
3. **Include filters for data quality** (minimum sample sizes)
4. **Use consistent color schemes**
5. **Save visualizations with descriptive names**
6. **Return paths to all generated visualizations**

## 7. Report Generation

Create comprehensive markdown reports:

```python
def generate_report(conference_results, team_results, vis_paths):
    """
    Generate a comprehensive markdown report of findings.
    
    Args:
        conference_results (dict): Conference performance results
        team_results (dict): Team performance results
        vis_paths (dict): Paths to generated visualizations
        
    Returns:
        str: Path to the generated report
    """
    logger.info("Generating analysis report...")
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(REPORTS_DIR, f"conference_tournament_analysis_{timestamp}.md")
    
    # Prepare top conferences for report
    top_conferences = [
        (conf, data['win_rate'], data['total_games'], data['avg_point_differential'])
        for conf, data in sorted(
            conference_results.items(),
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )
        if data['total_games'] >= 10
    ][:5]  # Top 5 conferences
    
    # Write the report
    with open(report_file, 'w') as f:
        f.write(f"# NCAA Tournament Performance Analysis by Conference and Team\n\n")
        f.write(f"*Analysis Date: {timestamp}*\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write("This analysis examines historical NCAA tournament performance patterns across conferences and teams. ")
        f.write("It identifies winning trends, consistent performers, and notable matchups in tournament play.\n\n")
        
        f.write("## Key Findings\n\n")
        
        # Conference performance
        f.write("### Conference Performance\n\n")
        if top_conferences:
            f.write("Top performing conferences by win rate (minimum 10 tournament games):\n\n")
            f.write("| Conference | Win Rate | Games Played | Avg Point Differential |\n")
            f.write("|------------|----------|-------------|----------------------|\n")
            for conf, win_rate, games, point_diff in top_conferences:
                f.write(f"| {conf} | {win_rate:.3f} | {games} | {point_diff:.1f} |\n")
            f.write("\n")
        
        if 'conference_win_rates' in vis_paths:
            f.write(f"![Conference Win Rates](../figures/{os.path.basename(vis_paths['conference_win_rates'])})\n\n")
        
        # Include methodology and limitations sections
        f.write("## Methodology\n\n")
        f.write("This analysis uses historical NCAA tournament game data to calculate win rates ")
        f.write("and performance metrics for conferences and teams. It considers all available ")
        f.write("tournament games in the dataset and includes:\n\n")
        f.write("- Win rates for conferences and teams\n")
        f.write("- Point differentials to assess dominance\n- Historical performance trends\n\n")
        
        f.write("### Limitations\n\n")
        f.write("- The analysis is based on available data and may not include all historical tournaments\n")
        f.write("- Conference realignment over time can affect historical trend analysis\n")
        f.write("- Sample sizes vary by conference and team, affecting statistical significance\n\n")
    
    logger.info(f"Generated report at {report_file}")
    return report_file
```

### Report Guidelines:

1. **Follow the template** from `reports/findings/README.md`
2. **Include an executive summary** with key takeaways
3. **Present findings in clear sections** with headings
4. **Use tables and visualizations** to support findings
5. **Document methodology and limitations**
6. **Ensure visualizations are correctly referenced** in the markdown

## 8. Common EDA Tasks

### 8.1 Win Rate Analysis

```python
def analyze_win_rates(tournament_games, entity_id_col, entity_name_col):
    """Calculate win rates for entities (teams, conferences, etc.)."""
    # Identify unique entities
    unique_entities = set(tournament_games[entity_id_col].unique().to_list())
    
    results = {}
    for entity_id in unique_entities:
        # Filter games for this entity
        entity_games = tournament_games.filter(
            (pl.col('home_id') == entity_id) | 
            (pl.col('away_id') == entity_id)
        )
        
        # Get entity name
        entity_name_rows = entity_games.filter(pl.col(entity_id_col) == entity_id).select(entity_name_col)
        if entity_name_rows.shape[0] > 0:
            entity_name = entity_name_rows[0, 0]
        else:
            entity_name = f"Unknown ({entity_id})"
        
        # Count games and wins
        total_games = entity_games.shape[0]
        
        # Home wins
        home_wins = entity_games.filter(
            (pl.col('home_id') == entity_id) & 
            (pl.col('home_score') > pl.col('away_score'))
        ).shape[0]
        
        # Away wins
        away_wins = entity_games.filter(
            (pl.col('away_id') == entity_id) & 
            (pl.col('away_score') > pl.col('home_score'))
        ).shape[0]
        
        total_wins = home_wins + away_wins
        win_rate = total_wins / total_games if total_games > 0 else 0
        
        # Store results
        results[entity_name] = {
            'entity_id': entity_id,
            'total_games': total_games,
            'total_wins': total_wins,
            'win_rate': win_rate,
            'home_wins': home_wins,
            'away_wins': away_wins
        }
    
    return results
```

### 8.2 Performance Metrics

```python
def calculate_performance_metrics(tournament_games, entity_id, is_home_col, is_away_col):
    """Calculate detailed performance metrics for an entity."""
    # Filter games for this entity
    entity_games = tournament_games.filter(
        (pl.col(is_home_col) == entity_id) | 
        (pl.col(is_away_col) == entity_id)
    )
    
    # Calculate point differentials
    home_games = entity_games.filter(pl.col(is_home_col) == entity_id)
    away_games = entity_games.filter(pl.col(is_away_col) == entity_id)
    
    home_point_diff = home_games.select(
        (pl.col('home_score') - pl.col('away_score')).alias('point_diff')
    )
    
    away_point_diff = away_games.select(
        (pl.col('away_score') - pl.col('home_score')).alias('point_diff')
    )
    
    all_point_diffs = pl.concat([home_point_diff, away_point_diff], how='vertical')
    avg_point_diff = all_point_diffs['point_diff'].mean() if all_point_diffs.shape[0] > 0 else 0
    
    return {
        'avg_point_differential': avg_point_diff,
        # Add more metrics as needed
    }
```

### 8.3 Historical Trends

```python
def analyze_historical_trends(tournament_games, entity_results, entity_id_col, time_period_col='season'):
    """Analyze performance trends over time."""
    # Get unique time periods (e.g., seasons)
    time_periods = sorted(tournament_games[time_period_col].unique().to_list())
    
    # Initialize results
    historical_trends = {}
    
    # For each entity, calculate performance by time period
    for entity_name, data in entity_results.items():
        entity_id = data['entity_id']
        
        entity_trends = {'seasons': [], 'win_rates': []}
        
        for period in time_periods:
            # Filter games for this entity and time period
            period_games = tournament_games.filter(
                ((pl.col(entity_id_col) == entity_id) | 
                 (pl.col(entity_id_col) == entity_id)) &
                (pl.col(time_period_col) == period)
            )
            
            if period_games.shape[0] > 0:
                # Calculate win rate for this period
                total_games = period_games.shape[0]
                
                wins = period_games.filter(
                    ((pl.col('home_id') == entity_id) & 
                     (pl.col('home_score') > pl.col('away_score'))) |
                    ((pl.col('away_id') == entity_id) & 
                     (pl.col('away_score') > pl.col('home_score')))
                ).shape[0]
                
                win_rate = wins / total_games
                
                entity_trends['seasons'].append(period)
                entity_trends['win_rates'].append(win_rate)
        
        # Only store entities with sufficient historical data
        if len(entity_trends['seasons']) > 3:
            historical_trends[entity_name] = entity_trends
    
    return historical_trends
```

## 9. Example Implementation of an EDA Request

### Request Example:

> "I need an EDA script that analyzes how teams perform in their conference tournaments versus the NCAA tournament. I want to see if success in conference tournaments is predictive of NCAA tournament success."

### Implementation Approach:

1. **Identify required data sources**:
   - `schedules.parquet`: For tournament identification
   - `team_season_statistics.parquet`: For team performance metrics

2. **Define analysis objectives**:
   - Compare team win rates in conference tournaments vs NCAA tournament
   - Analyze point differentials in both tournament types
   - Examine historical trends in the relationship

3. **Create appropriate visualizations**:
   - Scatter plot of conference tournament win rate vs NCAA tournament win rate
   - Bar chart of performance difference by conference
   - Time series of correlation strength over years

4. **Generate comprehensive report**:
   - Executive summary of key findings
   - Detailed analysis with visualization references
   - Statistical validity assessment
   - Implications for predictive modeling

Following these guidelines will help ensure your EDA script is well-structured, informative, and meets the project's quality standards.

## 10. Troubleshooting & Common Issues

### Data Access Issues

If you encounter problems with data access:
- Ensure you're using the correct file paths (`data/processed/`)
- Verify file existence before attempting to read
- Check for permission issues

### Analysis Edge Cases

Watch for these common analysis challenges:
- **Small sample sizes**: Filter for minimum games (e.g., ≥5 games)
- **Missing data**: Handle null values explicitly
- **Outliers**: Consider their impact on results
- **Temporal changes**: Account for rule changes or conference realignment

### Code Performance

For large datasets:
- Use Polars lazy execution when appropriate
- Consider filtering data early in the pipeline
- Implement progress logging for long-running operations

## 11. EDA Request Completion Checklist

Before finalizing an EDA implementation, ensure:

- [ ] Script follows the standard modular structure
- [ ] Data is loaded and validated appropriately
- [ ] Analysis functions are focused and well-documented
- [ ] Visualizations are clear and informative
- [ ] Report is comprehensive and follows the template
- [ ] Error handling is robust
- [ ] Logging provides appropriate progress information
- [ ] Code is efficient and well-organized
- [ ] Output meets the specified acceptance criteria

By following this guide, you'll create high-quality, consistent EDA implementations that provide valuable insights for the NCAA March Madness Predictor project. 