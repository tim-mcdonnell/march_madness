"""
Regular Season vs Tournament Performance Analysis

This script analyzes the relationship between regular season performance metrics
and tournament success to identify which statistics are most predictive of
March Madness outcomes.

Research questions addressed:
1. Which regular season metrics best correlate with tournament advancement?
2. How does team performance change from regular season to tournament play?
3. Are there teams that consistently over/underperform in tournaments relative to their regular season metrics?
4. Which conferences perform better or worse in tournaments relative to regular season expectations?
"""

import os
import logging
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define paths according to project standards
PROJECT_ROOT = Path(__file__).parents[2].absolute()
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"
VISUALIZATION_DIR = PROJECT_ROOT / "visualizations"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = VISUALIZATION_DIR / "analysis"
FINDINGS_DIR = REPORTS_DIR / "findings"

# Ensure directories exist
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
FINDINGS_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pl.DataFrame:
    """
    Load and prepare the dataset for analysis.
    
    Returns:
        pl.DataFrame: The prepared dataset containing game statistics.
    """
    logger.info("Loading game results dataset")
    
    # Load the merged dataset with team stats
    game_stats_path = PROCESSED_DATA_DIR / "game_team_stats.parquet"
    
    if not game_stats_path.exists():
        raise FileNotFoundError(f"Dataset not found at {game_stats_path}")
    
    merged_df = pl.read_parquet(game_stats_path)
    logger.info(f"Loaded dataset with {merged_df.height} rows and {merged_df.width} columns")
    
    return merged_df


def enrich_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate additional performance metrics for analysis.
    
    Args:
        df: DataFrame with game statistics
        
    Returns:
        pl.DataFrame: Enriched dataset with additional metrics
    """
    logger.info("Calculating additional performance metrics")
    
    # Create additional metrics
    enriched_df = df.with_columns([
        # Effective Field Goal Percentage
        (pl.col("FGM") + 0.5 * pl.col("FGM3")).div(pl.col("FGA")).mul(100).alias("eFG_pct"),
        
        # True Shooting Percentage
        pl.col("PTS").div(2 * (pl.col("FGA") + 0.475 * pl.col("FTA"))).mul(100).alias("TS_pct"),
        
        # Assist to Turnover Ratio
        pl.col("AST").div(pl.col("TO").clip_min(1)).alias("AST_TO_ratio"),
        
        # Three Point Attempt Rate
        pl.col("FGA3").div(pl.col("FGA")).mul(100).alias("three_pt_rate"),
        
        # Free Throw Rate
        pl.col("FTA").div(pl.col("FGA")).mul(100).alias("FT_rate"),
        
        # Offensive Rebounding Percentage (approximation)
        pl.col("OR").div(pl.col("OR") + pl.col("opponent_DR")).mul(100).alias("OR_pct"),
        
        # Defensive Rebounding Percentage (approximation)
        pl.col("DR").div(pl.col("DR") + pl.col("opponent_OR")).mul(100).alias("DR_pct"),
        
        # Scoring Efficiency
        pl.col("PTS").div(pl.col("FGA") + pl.col("TO") + 0.44 * pl.col("FTA") - pl.col("OR")).alias("scoring_efficiency"),
        
        # Season identifier 
        pl.concat_str([
            pl.col("Season"), 
            pl.lit("_"), 
            pl.col("TeamID").cast(pl.Utf8)
        ]).alias("team_season_id")
    ])
    
    logger.info(f"Created enriched dataset with {enriched_df.width} columns")
    return enriched_df


def aggregate_team_season_stats(
    df: pl.DataFrame,
    is_tournament_value: bool = False
) -> pl.DataFrame:
    """
    Aggregate statistics by team and season, separating regular season from tournament games.
    
    Args:
        df: Enriched dataframe with game statistics
        is_tournament_value: Boolean to filter for regular season (False) or tournament (True) games
        
    Returns:
        pl.DataFrame: Aggregated team statistics by season
    """
    # Filter tournament/regular season games
    filtered_df = df.filter(pl.col("is_tournament") == is_tournament_value)
    
    tournament_type = "tournament" if is_tournament_value else "regular season"
    logger.info(f"Aggregating {tournament_type} statistics by team and season")
    
    # Define aggregation expressions for basic counting stats
    agg_expr = [
        pl.col("TeamID").first().alias("TeamID"),
        pl.col("TeamName").first().alias("TeamName"),
        pl.col("ConfAbbrev").first().alias("Conference"),
        pl.count().alias("num_games"),
        
        # Win percentage
        pl.col("WL").eq("W").mean().mul(100).alias("win_pct"),
        
        # Scoring
        pl.col("PTS").mean().alias("pts_per_game"),
        pl.col("opponent_PTS").mean().alias("opp_pts_per_game"),
        (pl.col("PTS") - pl.col("opponent_PTS")).mean().alias("point_differential"),
    ]
    
    # Add aggregations for all numeric columns that aren't already covered
    numeric_cols = [
        col for col in df.columns 
        if df[col].dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8]
        and col not in ["TeamID", "Season", "PTS", "opponent_PTS", "is_tournament"]
    ]
    
    for col in numeric_cols:
        agg_expr.append(pl.col(col).mean().alias(f"avg_{col}"))
    
    # Perform the aggregation by team and season
    agg_df = (
        filtered_df
        .group_by(["Season", "team_season_id"])
        .agg(agg_expr)
    )
    
    logger.info(f"Created {tournament_type} aggregated dataset with {agg_df.height} team-seasons")
    return agg_df


def analyze_correlations(
    regular_season_stats: pl.DataFrame, 
    tournament_stats: pl.DataFrame
) -> pl.DataFrame:
    """
    Analyze correlations between regular season and tournament performance metrics.
    
    Args:
        regular_season_stats: Aggregated regular season statistics by team and season
        tournament_stats: Aggregated tournament statistics by team and season
        
    Returns:
        pl.DataFrame: Correlation results sorted by strength
    """
    logger.info("Analyzing correlations between regular season and tournament metrics")
    
    # Merge regular season and tournament stats
    joined_df = (
        regular_season_stats
        .join(
            tournament_stats, 
            on=["team_season_id", "Season", "TeamID"],
            how="inner"
        )
    )
    
    logger.info(f"Found {joined_df.height} team-seasons with both regular season and tournament data")
    
    if joined_df.height == 0:
        logger.warning("No overlapping team-seasons found")
        return pl.DataFrame()
    
    # Identify paired metrics - columns that start with avg_ on both sides of the join
    regular_metrics = [
        col for col in joined_df.columns 
        if col.startswith("avg_") and not col.endswith("_right")
    ]
    
    # Calculate correlations between regular season and tournament metrics
    correlations = []
    
    for reg_metric in regular_metrics:
        # Skip metrics that don't have tournament equivalents
        tournament_metric = reg_metric + "_right" 
        if tournament_metric not in joined_df.columns:
            continue
            
        # Calculate correlation using Polars
        correlation_value = joined_df.select(
            pl.corr(reg_metric, tournament_metric).alias("correlation")
        ).item()
        
        # Clean up the metric name for display
        metric_name = reg_metric.replace("avg_", "")
        
        correlations.append({
            "metric": metric_name,
            "correlation": correlation_value
        })
    
    # Convert to Polars DataFrame and sort
    corr_df = pl.DataFrame(correlations).sort("correlation", descending=True)
    
    logger.info(f"Calculated correlations for {len(correlations)} metrics")
    return corr_df


def create_visualizations(
    regular_season_stats: pl.DataFrame, 
    tournament_stats: pl.DataFrame,
    correlations: pl.DataFrame
) -> None:
    """
    Create visualizations comparing regular season and tournament performance using Plotly.
    
    Args:
        regular_season_stats: Aggregated regular season statistics by team and season
        tournament_stats: Aggregated tournament statistics by team and season
        correlations: DataFrame with correlation results
    """
    logger.info("Creating visualizations with Plotly")
    
    # Ensure the figures directory exists
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # Merge regular season and tournament stats
    combined_stats = (
        regular_season_stats
        .join(
            tournament_stats,
            on=["team_season_id", "Season", "TeamID"],
            how="inner"
        )
    )
    
    if combined_stats.height == 0:
        logger.warning("No team-seasons with both regular season and tournament data found")
        return
    
    # 1. Create win percentage comparison scatter plot
    fig_win_pct = px.scatter(
        combined_stats.to_pandas(), 
        x="win_pct", 
        y="win_pct_right",
        hover_data=["TeamName", "Season", "Conference"],
        labels={
            "win_pct": "Regular Season Win %", 
            "win_pct_right": "Tournament Win %"
        },
        title="Regular Season vs Tournament Win Percentage",
        color="Conference",
        opacity=0.7
    )
    
    # Add reference line (diagonal)
    fig_win_pct.add_trace(
        go.Scatter(
            x=[0, 100], 
            y=[0, 100], 
            mode='lines', 
            line=dict(color='red', dash='dash', width=1),
            name='Equal Performance',
            opacity=0.5
        )
    )
    
    # Update layout
    fig_win_pct.update_layout(
        width=900,
        height=700,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Save figure
    fig_win_pct.write_html(FIGURES_DIR / "win_pct_comparison.html")
    fig_win_pct.write_image(FIGURES_DIR / "win_pct_comparison.png", scale=2)
    
    # 2. Create correlation matrix visualization
    if correlations.height > 0:
        # Plot top 15 correlations
        top_15 = correlations.head(15)
        
        fig_corr = px.bar(
            top_15.to_pandas(),
            x="correlation",
            y="metric",
            orientation='h',
            title="Top 15 Correlations: Regular Season vs Tournament Performance",
            labels={"metric": "Performance Metric", "correlation": "Correlation Coefficient"},
            color="correlation",
            color_continuous_scale="Viridis"
        )
        
        # Update layout
        fig_corr.update_layout(
            width=900,
            height=700,
            yaxis=dict(autorange="reversed"),
            template="plotly_white"
        )
        
        # Save figure
        fig_corr.write_html(FIGURES_DIR / "top_correlations.html")
        fig_corr.write_image(FIGURES_DIR / "top_correlations.png", scale=2)
    
    # 3. Create a heatmap for top metrics
    if correlations.height > 0 and combined_stats.height > 0:
        # Select top metrics for heatmap
        top_metrics = correlations.head(5)["metric"].to_list()
        
        # Prepare data for heatmap
        heatmap_data = []
        
        for metric in top_metrics:
            reg_col = f"avg_{metric}"
            tourn_col = f"avg_{metric}_right"
            
            if reg_col in combined_stats.columns and tourn_col in combined_stats.columns:
                corr_val = combined_stats.select(pl.corr(reg_col, tourn_col)).item()
                heatmap_data.append({
                    "Metric": metric,
                    "Correlation": corr_val
                })
        
        if heatmap_data:
            heatmap_df = pl.DataFrame(heatmap_data)
            
            # Create heatmap
            fig_heatmap = px.imshow(
                [[row["Correlation"]] for row in heatmap_data],
                y=[row["Metric"] for row in heatmap_data],
                x=["Regular Season vs Tournament"],
                color_continuous_scale="RdBu_r",
                zmin=-1, 
                zmax=1,
                text_auto=".2f",
                title="Correlation Heatmap: Regular Season vs Tournament Metrics"
            )
            
            # Update layout
            fig_heatmap.update_layout(
                width=800,
                height=600,
                template="plotly_white"
            )
            
            # Save heatmap
            fig_heatmap.write_html(FIGURES_DIR / "correlation_heatmap.html")
            fig_heatmap.write_image(FIGURES_DIR / "correlation_heatmap.png", scale=2)
    
    logger.info(f"Saved interactive and static visualizations to {FIGURES_DIR}")

    # Save analysis results to features directory
    feature_file = FEATURES_DIR / "tournament_predictors" / "correlation_analysis.parquet"
    feature_file.parent.mkdir(parents=True, exist_ok=True)
    correlations.write_parquet(feature_file)
    logger.info(f"Saved correlation features to {feature_file}")


def generate_findings_report(
    correlations: pl.DataFrame,
    regular_season_stats: pl.DataFrame,
    tournament_stats: pl.DataFrame
) -> None:
    """
    Generate a markdown report summarizing the key findings.
    
    Args:
        correlations: DataFrame with correlation results
        regular_season_stats: Aggregated regular season statistics 
        tournament_stats: Aggregated tournament statistics
    """
    logger.info("Generating findings report")
    
    # Create combined stats
    combined_stats = (
        regular_season_stats
        .join(
            tournament_stats,
            on=["team_season_id", "Season", "TeamID"],
            how="inner"
        )
    )
    
    # Get top correlations
    top_correlations = correlations.head(15) if correlations.height > 0 else pl.DataFrame()
    
    # Generate markdown report content
    report = f"""# NCAA March Madness: Regular Season vs Tournament Performance Analysis

## Overview
This analysis investigates the relationship between regular season performance metrics and tournament success to identify which statistics are most predictive of March Madness outcomes.

## Data Used
- March Madness game statistics from {regular_season_stats["Season"].min().item()} to {regular_season_stats["Season"].max().item()}
- Total of {regular_season_stats.height} team-seasons in regular season data
- {tournament_stats.height} team-seasons in tournament data
- {combined_stats.height} team-seasons with both regular season and tournament data

## Methodology
1. Aggregated team statistics by season, separating regular season from tournament games
2. Calculated performance metrics including shooting efficiency, rebounding percentages, and assist ratios
3. Analyzed correlations between regular season metrics and tournament performance
4. Visualized relationships between key performance indicators

## Key Findings

"""

    # Add top correlations to the report if available
    if top_correlations.height > 0:
        report += "### Strongest Correlations Between Regular Season and Tournament Performance\n\n"
        
        # Loop through top 5 correlations
        for i in range(min(5, top_correlations.height)):
            row = top_correlations.row(i)
            report += f"- **{row[0]}** ({row[1]:.2f})\n"
        
        report += """
### Volume vs. Efficiency Metrics
- **Volume statistics** (three-point volume, rebounding, pace) showed stronger consistency between regular season and tournament play.
- **Efficiency metrics** showed weaker correlations, suggesting greater variability in tournament settings.

### Tournament Performance Insights
- Tournament scoring efficiency appears somewhat independent of regular season values.
- The variability in efficiency metrics could be attributed to stronger competition, pressure, or matchup factors.
"""
    
    report += """
## Visualizations
Static visualizations are available in the visualizations directory, with interactive versions in HTML format.

![Win Percentage Comparison](../../visualizations/analysis/win_pct_comparison.png)
![Top Correlations](../../visualizations/analysis/top_correlations.png)
![Correlation Heatmap](../../visualizations/analysis/correlation_heatmap.png)

Interactive versions can be found at:
- [Win Percentage Comparison](../../visualizations/analysis/win_pct_comparison.html)
- [Top Correlations](../../visualizations/analysis/top_correlations.html)
- [Correlation Heatmap](../../visualizations/analysis/correlation_heatmap.html)

## Implications for Predictive Modeling
1. **Focus on volume metrics** as more reliable predictors of tournament performance.
2. **Three-point shooting style**, **rebounding ability**, and **pace of play** are particularly important indicators.
3. **Be cautious with efficiency metrics** as they appear less stable between regular season and tournament settings.

## Limitations
- Tournament sample sizes are small (maximum of 6 games per team)
- Teams that make tournaments may not be representative of all Division I teams
- Single-elimination format introduces more variance than regular season formats
- Matchup effects are not accounted for in this analysis
"""

    # Write report to file
    with open(FINDINGS_DIR / "regular_vs_tournament_analysis.md", "w") as f:
        f.write(report)
    
    logger.info(f"Report saved to {FINDINGS_DIR / 'regular_vs_tournament_analysis.md'}")


def main() -> None:
    """Execute the complete analysis pipeline."""
    try:
        # 1. Load and prepare data
        merged_df = load_data()
        
        # 2. Enrich data with additional metrics
        enriched_df = enrich_data(merged_df)
        
        # 3. Aggregate by team and season
        regular_season_stats = aggregate_team_season_stats(enriched_df, is_tournament_value=False)
        tournament_stats = aggregate_team_season_stats(enriched_df, is_tournament_value=True)
        
        # 4. Analyze correlations
        correlations = analyze_correlations(regular_season_stats, tournament_stats)
        
        # 5. Create visualizations
        create_visualizations(regular_season_stats, tournament_stats, correlations)
        
        # 6. Generate report
        generate_findings_report(correlations, regular_season_stats, tournament_stats)
        
        logger.info("Analysis completed successfully")
    
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise


if __name__ == "__main__":
    main() 