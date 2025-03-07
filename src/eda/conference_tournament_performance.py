#!/usr/bin/env python3
"""
Conference and Team Tournament Performance Analysis

This EDA script analyzes historical NCAA basketball tournament performance 
by conferences and teams. It examines patterns in tournament success,
conference strength over time, team consistency, and matchup trends.

Analysis objectives:
1. Conference performance: Win rates, round advancement, and championships
2. Conference strength over time: Historical trends in conference performance
3. Consistent performers: Teams with reliable tournament success
4. Matchup patterns: Performance across conference matchups
5. Historical program strength: Long-term success indicators
6. Coach impact: Performance under specific coaches
7. Visualizations: Visual representations of key findings

Output:
- Data visualizations using Plotly
- Markdown report of key findings
"""

import logging
import os
from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
import polars as pl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger('conference_tournament_analysis')

# Define the output directories for reports and figures
REPORTS_DIR = os.path.join('reports', 'findings')
FIGURES_DIR = os.path.join('reports', 'figures')
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def load_data() -> tuple[pl.DataFrame, pl.DataFrame]:
    """
    Load and prepare the necessary datasets for analysis.
    
    Returns:
        tuple: schedules_df, team_stats_df with tournament and team data
    """
    logger.info("Loading data...")
    
    try:
        # Load schedules data
        schedules_df = pl.read_parquet('data/processed/schedules.parquet')
        
        # Load team season statistics
        team_stats_df = pl.read_parquet('data/processed/team_season_statistics.parquet')
        
        logger.info(
            f"Loaded schedules data with {schedules_df.shape[0]} rows "
            f"and team stats with {team_stats_df.shape[0]} rows"
        )
        return schedules_df, team_stats_df
    
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def identify_tournament_games(schedules_df) -> pl.DataFrame:
    """
    Identify and filter NCAA tournament games from the schedules dataset.
    
    Args:
        schedules_df (pl.DataFrame): The schedules dataset
        
    Returns:
        pl.DataFrame: Dataset containing only tournament games
    """
    logger.info("Identifying tournament games...")
    
    # Tournament games have season_type=3 or non-null tournament_id
    tournament_games = schedules_df.filter(
        (pl.col('season_type') == 3) | 
        (pl.col('tournament_id').is_not_null())
    )
    
    # Add a column to identify the tournament round (if possible)
    # This might need to be refined based on actual data structure
    
    logger.info(f"Identified {tournament_games.shape[0]} tournament games")
    return tournament_games

def analyze_conference_performance(tournament_games, team_stats_df) -> dict:
    """
    Analyze tournament performance by conference.
    
    Args:
        tournament_games (pl.DataFrame): Tournament games dataset
        team_stats_df (pl.DataFrame): Team statistics dataset
        
    Returns:
        dict: Conference performance metrics and statistics
    """
    logger.info("Analyzing conference performance...")
    
    # Initialize results dictionary
    conference_results = {}
    
    # Get conference IDs and create a mapping from conference names
    # Extract unique conference IDs from the tournament games
    home_conf_ids = tournament_games.select('home_conference_id').rename({'home_conference_id': 'conference_id'}).unique()
    away_conf_ids = tournament_games.select('away_conference_id').rename({'away_conference_id': 'conference_id'}).unique()
    
    unique_conf_ids = pl.concat([home_conf_ids, away_conf_ids]).unique()
    
    # Create dictionary to map conference IDs to names
    # We'll use groups_name from the dataset for this, and if that doesn't work, try other columns
    conference_names = {}
    
    # Since we saw a "None" conference in our output, let's try to get better conference names
    for conf_id in unique_conf_ids.to_series():
        if conf_id is None:
            continue
            
        # First try using the groups_name column (conference name)
        conf_name_rows = tournament_games.filter(
            (pl.col('home_conference_id') == conf_id) & 
            (pl.col('groups_name').is_not_null())
        ).select('groups_name')
        
        if conf_name_rows.shape[0] > 0 and conf_name_rows[0, 0] is not None:
            conference_names[conf_id] = conf_name_rows[0, 0]
            continue
            
        # Next try looking at away games
        conf_name_rows = tournament_games.filter(
            (pl.col('away_conference_id') == conf_id) & 
            (pl.col('groups_name').is_not_null())
        ).select('groups_name')
        
        if conf_name_rows.shape[0] > 0 and conf_name_rows[0, 0] is not None:
            conference_names[conf_id] = conf_name_rows[0, 0]
            continue
            
        # If no proper name found, use a placeholder with the ID
        conference_names[conf_id] = f"Conference ID {conf_id}"
    
    # Analyze conference wins and performance
    for conf_id, conf_name in conference_names.items():
        # Count home wins for the conference
        home_wins = tournament_games.filter(
            (pl.col('home_conference_id') == conf_id) & 
            pl.col('home_winner')
        ).shape[0]
        
        # Count away wins for the conference
        away_wins = tournament_games.filter(
            (pl.col('away_conference_id') == conf_id) & 
            pl.col('away_winner')
        ).shape[0]
        
        # Count total games played by the conference
        home_games = tournament_games.filter(pl.col('home_conference_id') == conf_id).shape[0]
        away_games = tournament_games.filter(pl.col('away_conference_id') == conf_id).shape[0]
        
        total_games = home_games + away_games
        total_wins = home_wins + away_wins
        
        win_rate = total_wins / total_games if total_games > 0 else 0
            
        # Calculate point differential metrics
        home_points = tournament_games.filter(pl.col('home_conference_id') == conf_id).select('home_score').sum()[0, 0]
        home_opponent_points = tournament_games.filter(pl.col('home_conference_id') == conf_id).select('away_score').sum()[0, 0]
        
        away_points = tournament_games.filter(pl.col('away_conference_id') == conf_id).select('away_score').sum()[0, 0]
        away_opponent_points = tournament_games.filter(pl.col('away_conference_id') == conf_id).select('home_score').sum()[0, 0]
        
        total_points = home_points + away_points
        total_opponent_points = home_opponent_points + away_opponent_points
        
        if total_games > 0:
            avg_point_differential = (total_points - total_opponent_points) / total_games
            avg_points_scored = total_points / total_games
            avg_points_allowed = total_opponent_points / total_games
        else:
            avg_point_differential = 0
            avg_points_scored = 0
            avg_points_allowed = 0
        
        # Store conference results
        conference_results[conf_name] = {
            'conf_id': conf_id,
            'total_games': total_games,
            'total_wins': total_wins,
            'win_rate': win_rate,
            'home_wins': home_wins,
            'away_wins': away_wins,
            'avg_point_differential': avg_point_differential,
            'avg_points_scored': avg_points_scored,
            'avg_points_allowed': avg_points_allowed
        }
    
    logger.info(f"Analyzed performance for {len(conference_results)} conferences")
    return conference_results

def analyze_team_performance(tournament_games, team_stats_df) -> dict:
    """
    Analyze tournament performance by individual teams.
    
    Args:
        tournament_games (pl.DataFrame): Tournament games dataset
        team_stats_df (pl.DataFrame): Team statistics dataset
        
    Returns:
        dict: Team performance metrics and statistics
    """
    logger.info("Analyzing team performance...")
    
    # Initialize results dictionary
    team_results = {}
    
    # Extract unique team IDs from tournament games
    home_team_ids = tournament_games.select('home_id').rename({'home_id': 'team_id'}).unique()
    away_team_ids = tournament_games.select('away_id').rename({'away_id': 'team_id'}).unique()
    
    all_team_ids = pl.concat([home_team_ids, away_team_ids]).unique()
    
    # Create dictionary to map team IDs to names
    team_names = {}
    for team_id in all_team_ids.to_series():
        # Get a team name for this ID
        home_name_rows = tournament_games.filter(pl.col('home_id') == team_id).select('home_name')
        if home_name_rows.shape[0] > 0:
            team_names[team_id] = home_name_rows[0, 0]
        else:
            away_name_rows = tournament_games.filter(pl.col('away_id') == team_id).select('away_name')
            if away_name_rows.shape[0] > 0:
                team_names[team_id] = away_name_rows[0, 0]
            else:
                team_names[team_id] = f"Team ID {team_id}"
    
    # Check if seed information is available in the dataset
    has_seed_info = 'home_seed' in tournament_games.columns and 'away_seed' in tournament_games.columns
    
    # Analyze team performance in tournament games
    for team_id, team_name in team_names.items():
        # Home wins
        home_wins = tournament_games.filter(
            (pl.col('home_id') == team_id) & 
            pl.col('home_winner')
        ).shape[0]
        
        # Away wins
        away_wins = tournament_games.filter(
            (pl.col('away_id') == team_id) & 
            pl.col('away_winner')
        ).shape[0]
        
        # Total games
        home_games = tournament_games.filter(pl.col('home_id') == team_id).shape[0]
        away_games = tournament_games.filter(pl.col('away_id') == team_id).shape[0]
        
        total_games = home_games + away_games
        total_wins = home_wins + away_wins
        
        win_rate = total_wins / total_games if total_games > 0 else 0
            
        # Calculate point differential metrics
        home_points = tournament_games.filter(pl.col('home_id') == team_id).select('home_score').sum()[0, 0]
        home_opponent_points = tournament_games.filter(pl.col('home_id') == team_id).select('away_score').sum()[0, 0]
        
        away_points = tournament_games.filter(pl.col('away_id') == team_id).select('away_score').sum()[0, 0]
        away_opponent_points = tournament_games.filter(pl.col('away_id') == team_id).select('home_score').sum()[0, 0]
        
        total_points = home_points + away_points
        total_opponent_points = home_opponent_points + away_opponent_points
        
        if total_games > 0:
            avg_point_differential = (total_points - total_opponent_points) / total_games
            avg_points_scored = total_points / total_games
            avg_points_allowed = total_opponent_points / total_games
        else:
            avg_point_differential = 0
            avg_points_scored = 0
            avg_points_allowed = 0
        
        # Get conference information for this team
        conf_rows = tournament_games.filter(pl.col('home_id') == team_id).select('home_conference_id')
        conf_id = conf_rows[0, 0] if conf_rows.shape[0] > 0 else None
        
        # Initialize avg_seed as None
        avg_seed = None
                
        # If seed information is available, calculate average seed for the team
        if has_seed_info:
            try:
                # Try to get seed information for the team
                home_seed_rows = tournament_games.filter(
                    (pl.col('home_id') == team_id) & 
                    (pl.col('home_seed').is_not_null())
                ).select('home_seed')
                
                away_seed_rows = tournament_games.filter(
                    (pl.col('away_id') == team_id) & 
                    (pl.col('away_seed').is_not_null())
                ).select('away_seed')
                
                all_seeds = []
                if home_seed_rows.shape[0] > 0:
                    all_seeds.extend(home_seed_rows.to_series().cast(pl.Int64, strict=False).to_list())
                
                if away_seed_rows.shape[0] > 0:
                    all_seeds.extend(away_seed_rows.to_series().cast(pl.Int64, strict=False).to_list())
                
                if all_seeds:
                    avg_seed = sum(all_seeds) / len(all_seeds)
            except Exception as e:
                logger.warning(f"Could not calculate seed info for {team_name}: {e}")
                avg_seed = None
        
        # Store team results
        team_results[team_name] = {
            'team_id': team_id,
            'conf_id': conf_id,
            'total_games': total_games,
            'total_wins': total_wins,
            'win_rate': win_rate,
            'home_wins': home_wins,
            'away_wins': away_wins,
            'avg_point_differential': avg_point_differential,
            'avg_points_scored': avg_points_scored,
            'avg_points_allowed': avg_points_allowed,
            'avg_seed': avg_seed
        }
    
    logger.info(f"Analyzed performance for {len(team_results)} teams")
    return team_results

def analyze_historical_trends(tournament_games, conference_results) -> dict:
    """
    Analyze historical trends in conference performance over time.
    
    Args:
        tournament_games (pl.DataFrame): Tournament games dataset
        conference_results (dict): Conference performance metrics
        
    Returns:
        dict: Conference performance trends over seasons
    """
    logger.info("Analyzing historical trends...")
    
    # Initialize results dictionary
    historical_trends = {}
    
    # Get all unique seasons
    seasons = tournament_games.select('season').unique().sort('season')
    
    # For each conference, calculate performance by season
    for conf_name, conf_data in conference_results.items():
        conf_id = conf_data['conf_id']
        historical_trends[conf_name] = {'seasons': [], 'win_rates': []}
        
        for season in seasons.to_series():
            # Filter tournament games for this season and conference
            season_games = tournament_games.filter(pl.col('season') == season)
            
            # Count home wins for the conference in this season
            home_wins = season_games.filter(
                (pl.col('home_conference_id') == conf_id) & 
                pl.col('home_winner')
            ).shape[0]
            
            # Count away wins for the conference in this season
            away_wins = season_games.filter(
                (pl.col('away_conference_id') == conf_id) & 
                pl.col('away_winner')
            ).shape[0]
            
            # Count total games played by the conference in this season
            home_games = season_games.filter(pl.col('home_conference_id') == conf_id).shape[0]
            away_games = season_games.filter(pl.col('away_conference_id') == conf_id).shape[0]
            
            total_games = home_games + away_games
            total_wins = home_wins + away_wins
            
            if total_games > 0:
                season_win_rate = total_wins / total_games
                historical_trends[conf_name]['seasons'].append(season)
                historical_trends[conf_name]['win_rates'].append(season_win_rate)
    
    logger.info(f"Analyzed historical trends for {len(historical_trends)} conferences")
    return historical_trends

def analyze_matchup_patterns(tournament_games, conference_results) -> pl.DataFrame:
    """
    Analyze patterns in conference matchups during tournaments.
    
    Args:
        tournament_games (pl.DataFrame): Tournament games dataset
        conference_results (dict): Conference performance metrics
        
    Returns:
        pl.DataFrame: Conference matchup performance
    """
    logger.info("Analyzing matchup patterns...")
    
    # Initialize a list to store matchup results
    matchup_results = []
    
    # For each pair of conferences, analyze their matchups
    for conf1_name, conf1_data in conference_results.items():
        conf1_id = conf1_data['conf_id']
        
        for conf2_name, conf2_data in conference_results.items():
            conf2_id = conf2_data['conf_id']
            
            if conf1_id == conf2_id:
                continue  # Skip same conference matchups
            
            # Conf1 as home, Conf2 as away
            matchups_1_vs_2 = tournament_games.filter(
                (pl.col('home_conference_id') == conf1_id) & 
                (pl.col('away_conference_id') == conf2_id)
            )
            
            # Conf2 as home, Conf1 as away
            matchups_2_vs_1 = tournament_games.filter(
                (pl.col('home_conference_id') == conf2_id) & 
                (pl.col('away_conference_id') == conf1_id)
            )
            
            # Calculate conf1 wins
            conf1_wins = (
                matchups_1_vs_2.filter(pl.col('home_winner')).shape[0] + 
                matchups_2_vs_1.filter(pl.col('away_winner')).shape[0]
            )
            
            # Calculate total matchups
            total_matchups = matchups_1_vs_2.shape[0] + matchups_2_vs_1.shape[0]
            
            if total_matchups > 0:
                conf1_win_rate = conf1_wins / total_matchups
                conf2_win_rate = 1 - conf1_win_rate
                
                matchup_results.append({
                    'conf1_name': conf1_name,
                    'conf2_name': conf2_name,
                    'total_matchups': total_matchups,
                    'conf1_wins': conf1_wins,
                    'conf2_wins': total_matchups - conf1_wins,
                    'conf1_win_rate': conf1_win_rate,
                    'conf2_win_rate': conf2_win_rate
                })
    
    # Convert to DataFrame
    matchup_df = pl.DataFrame(matchup_results)
    
    logger.info(f"Analyzed {len(matchup_results)} conference matchup patterns")
    return matchup_df

def generate_visualizations(conference_results, team_results, historical_trends, matchup_df) -> dict:
    """
    Generate visualizations for the analysis.
    
    Args:
        conference_results (dict): Conference performance results.
        team_results (dict): Team performance results.
        historical_trends (dict): Historical trends data.
        matchup_df (pl.DataFrame): Conference matchup data.
        
    Returns:
        dict: Paths to generated visualizations.
    """
    logger.info("Generating visualizations...")
    vis_paths = {}
    
    # 1. Conference Win Rates
    conf_win_rates = [
        {'Conference': conf_name, 'Win Rate': data['win_rate'], 'Games': data['total_games'], 
         'Point Differential': data['avg_point_differential']} 
        for conf_name, data in conference_results.items()
        if data['total_games'] >= 10  # Only include conferences with enough games
    ]
    conf_win_rates_df = pl.DataFrame(conf_win_rates).sort('Win Rate', descending=True)
    
    fig1 = px.bar(
        conf_win_rates_df.to_pandas(), 
        x='Conference', 
        y='Win Rate',
        title='NCAA Tournament Win Rates by Conference (Min. 10 Games)',
        color='Games',
        color_continuous_scale='Viridis',
        height=600
    )
    fig1.update_layout(xaxis_tickangle=-45)
    
    # Save as PNG only
    png_path = os.path.join(FIGURES_DIR, 'conference_win_rates.png')
    fig1.write_image(png_path)
    vis_paths['conference_win_rates'] = png_path
    
    # 2. Top Teams by Win Rate
    top_teams = [
        {'Team': team_name, 'Win Rate': data['win_rate'], 'Games': data['total_games']} 
        for team_name, data in team_results.items()
        if data['total_games'] >= 5  # Only include teams with enough games
    ]
    top_teams_df = pl.DataFrame(top_teams).sort('Win Rate', descending=True).head(20)
    
    fig2 = px.bar(
        top_teams_df.to_pandas(), 
        x='Team', 
        y='Win Rate',
        title='Top 20 Teams by NCAA Tournament Win Rate (Min. 5 Games)',
        color='Games',
        color_continuous_scale='Viridis',
        height=600
    )
    fig2.update_layout(xaxis_tickangle=-45)
    
    # Save as PNG only
    png_path = os.path.join(FIGURES_DIR, 'top_teams_win_rates.png')
    fig2.write_image(png_path)
    vis_paths['top_teams_win_rates'] = png_path
    
    # 3. Historical Conference Performance
    # Filter to top conferences by games played
    top_confs = sorted(
        [(conf_name, len(data['seasons'])) for conf_name, data in historical_trends.items()],
        key=lambda x: x[1], 
        reverse=True
    )[:6]  # Top 6 conferences
    
    fig3 = go.Figure()
    for conf_name, _ in top_confs:
        if conf_name in historical_trends and len(historical_trends[conf_name]['seasons']) > 0:
            fig3.add_trace(go.Scatter(
                x=historical_trends[conf_name]['seasons'],
                y=historical_trends[conf_name]['win_rates'],
                mode='lines+markers',
                name=conf_name
            ))
            
    fig3.update_layout(
        title='Historical NCAA Tournament Win Rates for Top Conferences',
        xaxis_title='Season',
        yaxis_title='Win Rate',
        yaxis_range=[0, 1],
        height=600
    )
    
    # Save as PNG only
    png_path = os.path.join(FIGURES_DIR, 'conference_historical_trends.png')
    fig3.write_image(png_path)
    vis_paths['conference_historical_trends'] = png_path
    
    # 4. Conference Matchup Heatmap
    # Only create this visualization if we have matchup data
    if matchup_df.shape[0] > 0:
        # Filter to significant matchups
        significant_matchups = matchup_df.filter(pl.col('total_matchups') >= 3)
        
        if significant_matchups.shape[0] > 0:
            # Get unique conferences
            unique_confs = set()
            for row in significant_matchups.rows(named=True):
                unique_confs.add(row['conf1_name'])
                unique_confs.add(row['conf2_name'])
            unique_confs = sorted(unique_confs)
            
            # Create matchup matrix
            matchup_matrix = []
            for conf1 in unique_confs:
                row = []
                for conf2 in unique_confs:
                    if conf1 == conf2:
                        row.append(0.5)  # Default for same conference
                    else:
                        # Find matchup
                        matchup = significant_matchups.filter(
                            (pl.col('conf1_name') == conf1) & (pl.col('conf2_name') == conf2)
                        )
                        if matchup.shape[0] > 0:
                            row.append(matchup[0, 'conf1_win_rate'])
                        else:
                            # Check reverse matchup
                            matchup = significant_matchups.filter(
                                (pl.col('conf1_name') == conf2) & (pl.col('conf2_name') == conf1)
                            )
                            if matchup.shape[0] > 0:
                                row.append(1 - matchup[0, 'conf1_win_rate'])
                            else:
                                row.append(None)  # No matchup data
                matchup_matrix.append(row)
            
            fig4 = go.Figure(data=go.Heatmap(
                z=matchup_matrix,
                x=unique_confs,
                y=unique_confs,
                colorscale='RdBu',
                zmid=0.5,
                text=matchup_matrix,
                hoverinfo='text+x+y',
                colorbar={'title': 'Win Rate'}
            ))
            
            fig4.update_layout(
                title='Conference vs Conference NCAA Tournament Win Rates',
                xaxis_title='',
                yaxis_title='',
                height=800,
                width=800
            )
            
            # Save as PNG only
            png_path = os.path.join(FIGURES_DIR, 'conference_matchup_heatmap.png')
            fig4.write_image(png_path)
            vis_paths['conference_matchup_heatmap'] = png_path
    
    logger.info(f"Generated {len(vis_paths)} visualizations (PNG only)")
    return vis_paths

def generate_report(conference_results, team_results, historical_trends, matchup_df, vis_paths) -> str:
    """
    Generate a comprehensive markdown report of findings.
    
    Args:
        conference_results (dict): Conference performance results.
        team_results (dict): Team performance results.
        historical_trends (dict): Historical trends data.
        matchup_df (pl.DataFrame): Conference matchup data.
        vis_paths (dict): Paths to generated visualizations.
        
    Returns:
        str: Path to the generated report.
    """
    logger.info("Generating analysis report...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(REPORTS_DIR, f'conference_tournament_analysis_{timestamp}.md')
    
    # Find top conferences by win rate
    top_conferences = sorted(
        [(conf, data['win_rate'], data['total_games'], data.get('avg_point_differential', 0)) 
         for conf, data in conference_results.items() 
         if data['total_games'] >= 10],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    # Find top teams by win rate
    top_teams = sorted(
        [(team, data['win_rate'], data['total_games'], data.get('avg_point_differential', 0), data.get('avg_seed', None)) 
         for team, data in team_results.items() 
         if data['total_games'] >= 5],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Check if we have seed information for any teams
    has_seed_info = any(data.get('avg_seed') is not None for data in team_results.values())
    
    # Only compute overperformers if we have seed information
    top_overperformers = []
    if has_seed_info:
        overperformers = []
        for team, data in team_results.items():
            if data['total_games'] >= 5 and data.get('avg_seed') is not None:
                # Expected win rate based on seed (higher seeds expected to have lower win rates)
                # This is a simple approximation - a more sophisticated approach would use historical seed performance
                expected_win_rate = 1 - (data.get('avg_seed', 16) / 16)
                actual_win_rate = data['win_rate']
                overperformance = actual_win_rate - expected_win_rate
                
                overperformers.append((team, actual_win_rate, data['total_games'], data.get('avg_seed'), overperformance))
        
        top_overperformers = sorted(overperformers, key=lambda x: x[4], reverse=True)[:10]
    
    # Write the report
    with open(report_file, 'w') as f:
        f.write("# NCAA Tournament Performance Analysis by Conference and Team\n\n")
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
        else:
            f.write("No conferences with at least 10 tournament games found in the data.\n\n")
        
        if 'conference_win_rates' in vis_paths:
            f.write(f"![Conference Win Rates]({vis_paths['conference_win_rates'].replace('reports/', '../')})\n\n")
        
        # Team performance
        f.write("### Team Performance\n\n")
        if top_teams:
            f.write("Top performing teams by win rate (minimum 5 tournament games):\n\n")
            if has_seed_info:
                f.write("| Team | Win Rate | Games Played | Avg Point Differential | Avg Seed |\n")
                f.write("|------|----------|-------------|----------------------|----------|\n")
                for team, win_rate, games, point_diff, avg_seed in top_teams:
                    seed_str = f"{avg_seed:.1f}" if avg_seed is not None else "N/A"
                    f.write(f"| {team} | {win_rate:.3f} | {games} | {point_diff:.1f} | {seed_str} |\n")
            else:
                f.write("| Team | Win Rate | Games Played | Avg Point Differential |\n")
                f.write("|------|----------|-------------|----------------------|\n")
                for team, win_rate, games, point_diff, _ in top_teams:
                    f.write(f"| {team} | {win_rate:.3f} | {games} | {point_diff:.1f} |\n")
            f.write("\n")
        else:
            f.write("No teams with at least 5 tournament games found in the data.\n\n")
        
        if 'top_teams_win_rates' in vis_paths:
            f.write(f"![Top Teams Win Rates]({vis_paths['top_teams_win_rates'].replace('reports/', '../')})\n\n")
            
        # Seed overperformance - only if we have seed data
        if has_seed_info and top_overperformers:
            f.write("### Teams Outperforming Their Seed\n\n")
            f.write("Teams with the largest positive difference between actual win rate and expected win rate based on seed:\n\n")
            f.write("| Team | Win Rate | Games Played | Avg Seed | Overperformance |\n")
            f.write("|------|----------|-------------|----------|----------------|\n")
            for team, win_rate, games, avg_seed, overperformance in top_overperformers:
                seed_str = f"{avg_seed:.1f}" if avg_seed is not None else "N/A"
                f.write(f"| {team} | {win_rate:.3f} | {games} | {seed_str} | {overperformance:.3f} |\n")
            f.write("\n")
        
        # Historical trends
        f.write("### Historical Conference Performance\n\n")
        if 'conference_historical_trends' in vis_paths:
            f.write("The following visualization shows tournament win rates over time for top conferences:\n\n")
            f.write(f"![Historical Conference Trends]({vis_paths['conference_historical_trends'].replace('reports/', '../')})\n\n")
        else:
            f.write("Insufficient data to generate historical conference performance trends.\n\n")
        
        # Conference matchups
        f.write("### Conference Matchup Analysis\n\n")
        if 'conference_matchup_heatmap' in vis_paths:
            f.write("This heatmap shows head-to-head win rates between conferences in tournament play:\n\n")
            f.write(f"![Conference Matchup Heatmap]({vis_paths['conference_matchup_heatmap'].replace('reports/', '../')})\n\n")
            
            # Notable matchups
            f.write("#### Notable Conference Matchups\n\n")
            f.write("Matchups with significant performance differences (minimum 3 games):\n\n")
            f.write("| Conference 1 | Conference 2 | Games | Conf 1 Win Rate |\n")
            f.write("|--------------|--------------|-------|----------------|\n")
            
            # Find notable matchups (win rate far from 50%)
            if matchup_df.shape[0] > 0:
                notable_matchups = matchup_df.filter(
                    (pl.col('total_matchups') >= 3) & 
                    ((pl.col('conf1_win_rate') >= 0.7) | (pl.col('conf1_win_rate') <= 0.3))
                ).sort('conf1_win_rate', descending=True).head(10)
                
                for row in notable_matchups.rows(named=True):
                    f.write(f"| {row['conf1_name']} | {row['conf2_name']} | {row['total_matchups']} | {row['conf1_win_rate']:.3f} |\n")
            else:
                f.write("No notable matchups with at least 3 games found in the data.\n")
        else:
            f.write("Insufficient data to analyze conference matchups.\n\n")
        
        f.write("\n## Methodology\n\n")
        f.write("This analysis uses historical NCAA tournament game data to calculate win rates and performance metrics ")
        f.write("for conferences and teams. It considers all available tournament games in the dataset and includes:\n\n")
        f.write("- Win rates for conferences and teams\n")
        f.write("- Point differentials to assess dominance\n")
        if has_seed_info:
            f.write("- Seed-based performance evaluation\n")
        f.write("- Historical performance trends\n\n")
        
        f.write("### Limitations\n\n")
        f.write("- The analysis is based on available data and may not include all historical tournaments\n")
        f.write("- Conference realignment over time can affect historical trend analysis\n")
        f.write("- Sample sizes vary by conference and team, affecting statistical significance\n")
        if has_seed_info:
            f.write("- Seeding data may be incomplete for some tournaments\n")
    
    logger.info(f"Generated report at {report_file}")
    return report_file

def main() -> None:
    """
    Main function to execute the tournament performance analysis.
    """
    logger.info("Starting conference and team tournament performance analysis")
    
    try:
        # Load data
        schedules_df, team_stats_df = load_data()
        
        # Identify tournament games
        tournament_games = identify_tournament_games(schedules_df)
        
        # Analyze conference performance
        conference_results = analyze_conference_performance(tournament_games, team_stats_df)
        
        # Analyze team performance
        team_results = analyze_team_performance(tournament_games, team_stats_df)
        
        # Analyze historical trends
        historical_trends = analyze_historical_trends(tournament_games, conference_results)
        
        # Analyze matchup patterns
        matchup_df = analyze_matchup_patterns(tournament_games, conference_results)
        
        # Generate visualizations
        vis_paths = generate_visualizations(conference_results, team_results, historical_trends, matchup_df)
        
        # Generate report
        report_path = generate_report(conference_results, team_results, historical_trends, matchup_df, vis_paths)
        
        logger.info(f"Analysis completed successfully. Report available at: {report_path}")
        
    except Exception as e:
        logger.error(f"Error in conference tournament performance analysis: {e}")
        raise
    
if __name__ == "__main__":
    main() 