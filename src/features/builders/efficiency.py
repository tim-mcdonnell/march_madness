"""Efficiency metrics feature builder for March Madness predictor.

This module implements the Phase 2 efficiency metrics:
1. Team Offensive/Defensive Efficiency Ratings
2. True Tempo 
3. Strength of Schedule
4. Tournament Experience metric

Phase 2 builds on the foundation features, adding more complex metrics
that require iteration and opponent-adjusted calculations.
"""

import logging

import polars as pl

from src.features.base import BaseFeatureBuilder

logger = logging.getLogger(__name__)

class EfficiencyFeatureBuilder(BaseFeatureBuilder):
    """Builder for efficiency metrics features."""
    
    def __init__(self, config: dict[str, object] | None = None) -> None:
        """Initialize the efficiency metrics feature builder.
        
        Args:
            config: Configuration parameters including:
                - iterations: Number of iterations for adjusting ratings (default: 10)
                - output_file: Name of the output file (default: team_performance.parquet)
                - min_possessions: Minimum possessions for reliability (default: 100)
                - league_average_oe: League average offensive efficiency (default: 100)
                - league_average_de: League average defensive efficiency (default: 100)
                - league_average_tempo: League average tempo (default: 70)
        """
        super().__init__(config)
        self.name = "efficiency"
        self.iterations = self.config.get("iterations", 10)
        self.output_file = self.config.get("output_file", "team_performance.parquet")
        self.min_possessions = self.config.get("min_possessions", 100)
        self.league_average_oe = self.config.get("league_average_oe", 100)
        self.league_average_de = self.config.get("league_average_de", 100)
        self.league_average_tempo = self.config.get("league_average_tempo", 70)
        
    def build_features(self, 
                      team_performance: pl.DataFrame,
                      team_box: pl.DataFrame,
                      schedules: pl.DataFrame) -> pl.DataFrame:
        """Build efficiency metrics features.
        
        Args:
            team_performance: Team performance foundation features DataFrame
            team_box: Team box scores DataFrame
            schedules: Game schedules DataFrame
            
        Returns:
            DataFrame with efficiency metrics features
        """
        # Start with the team performance dataset from Phase 1
        features = team_performance.clone()
        
        # Calculate raw offensive and defensive efficiency ratings
        raw_efficiency = self._calculate_raw_efficiency(team_box)
        
        # Calculate raw tempo
        raw_tempo = self._calculate_raw_tempo(team_box)
        
        # Calculate opponent-adjusted efficiency and tempo
        adjusted_metrics = self._calculate_adjusted_metrics(
            raw_efficiency, 
            raw_tempo, 
            schedules
        )
        
        # Calculate strength of schedule
        schedule_strength = self._calculate_strength_of_schedule(
            adjusted_metrics, 
            schedules
        )
        
        # Calculate tournament experience
        tournament_exp = self._calculate_tournament_experience(schedules)
        
        # Combine all metrics
        combined = features
        for df in [adjusted_metrics, schedule_strength, tournament_exp]:
            if df is not None:
                combined = combined.join(
                    df, 
                    on=["team_id", "season"], 
                    how="left"
                )
        
        logger.info(f"Built efficiency metrics for {combined.height} team-seasons")
        return combined
    
    def _calculate_raw_efficiency(self, team_box: pl.DataFrame) -> pl.DataFrame:
        """Calculate raw (unadjusted) offensive and defensive efficiency.
        
        Args:
            team_box: Team box scores DataFrame
            
        Returns:
            DataFrame with raw efficiency metrics
        """
        logger.info("Calculating raw efficiency metrics")
        
        # Make sure we have points and estimated possessions
        if "possessions" not in team_box.columns:
            logger.info("Estimating possessions from box score data")
            
            team_box = team_box.with_columns([
                (
                    pl.col("field_goals_attempted") - pl.col("offensive_rebounds") + 
                    pl.col("team_turnovers") + (0.44 * pl.col("free_throws_attempted"))
                ).alias("possessions")
            ])
        
        # Calculate raw offensive and defensive efficiency
        raw_efficiency = (
            team_box
            .filter(pl.col("possessions") > 0)
            .with_columns([
                (pl.col("team_score") / pl.col("possessions") * 100).alias("raw_offensive_efficiency"),
                (pl.col("opponent_team_score") / pl.col("possessions") * 100).alias("raw_defensive_efficiency")
            ])
            .group_by(["team_id", "season"])
            .agg([
                pl.sum("team_score").alias("total_points"),
                pl.sum("opponent_team_score").alias("total_opp_points"), 
                pl.sum("possessions").alias("total_possessions"),
                pl.mean("raw_offensive_efficiency").alias("avg_offensive_efficiency"),
                pl.mean("raw_defensive_efficiency").alias("avg_defensive_efficiency"),
                pl.count("game_id").alias("games_played")
            ])
            .with_columns([
                (pl.col("total_points") / pl.col("total_possessions") * 100)
                .alias("raw_offensive_efficiency"),
                
                (pl.col("total_opp_points") / pl.col("total_possessions") * 100)
                .alias("raw_defensive_efficiency")
            ])
            .filter(pl.col("total_possessions") >= self.min_possessions)
        )
        
        logger.info(f"Calculated raw efficiency metrics for {raw_efficiency.height} teams")
        return raw_efficiency
    
    def _calculate_raw_tempo(self, team_box: pl.DataFrame) -> pl.DataFrame:
        """Calculate raw (unadjusted) tempo as possessions per 40 minutes.
        
        Args:
            team_box: Team box scores DataFrame
            
        Returns:
            DataFrame with raw tempo metrics
        """
        logger.info("Calculating raw tempo metrics")
        
        # Make sure we have possessions
        if "possessions" not in team_box.columns:
            logger.info("Estimating possessions from box score data")
            
            team_box = team_box.with_columns([
                (
                    pl.col("field_goals_attempted") - pl.col("offensive_rebounds") + 
                    pl.col("team_turnovers") + (0.44 * pl.col("free_throws_attempted"))
                ).alias("possessions")
            ])
        
        # Make sure we have possessions and minutes
        has_minutes = "minutes" in team_box.columns
        
        if not has_minutes:
            logger.info("Using default 40 minutes per game for tempo calculation")
            
            raw_tempo = (
                team_box
                .filter(pl.col("possessions") > 0)
                .with_columns([
                    (pl.col("possessions") * (40 / 40)).alias("tempo_40")
                ])
                .group_by(["team_id", "season"])
                .agg([
                    pl.mean("tempo_40").alias("raw_tempo"),
                    pl.std("tempo_40").alias("tempo_stddev"),
                    pl.count("game_id").alias("games_played")
                ])
            )
        else:
            # If we have minutes, adjust to possessions per 40 minutes
            raw_tempo = (
                team_box
                .filter(pl.col("possessions") > 0)
                .filter(pl.col("minutes") > 0)
                .with_columns([
                    (pl.col("possessions") * (40 / pl.col("minutes"))).alias("tempo_40")
                ])
                .group_by(["team_id", "season"])
                .agg([
                    pl.mean("tempo_40").alias("raw_tempo"),
                    pl.std("tempo_40").alias("tempo_stddev"),
                    pl.count("game_id").alias("games_played")
                ])
            )
                
        logger.info(f"Calculated raw tempo metrics for {raw_tempo.height} teams")
        return raw_tempo
    
    def _calculate_adjusted_metrics(self, 
                                  raw_efficiency: pl.DataFrame,
                                  raw_tempo: pl.DataFrame,
                                  schedules: pl.DataFrame) -> pl.DataFrame:
        """Calculate opponent-adjusted efficiency and tempo metrics.
        
        Uses an iterative approach to adjust raw metrics based on opponent strength.
        
        Args:
            raw_efficiency: Raw efficiency metrics DataFrame
            raw_tempo: Raw tempo metrics DataFrame
            schedules: Game schedules DataFrame
            
        Returns:
            DataFrame with adjusted metrics
        """
        logger.info(f"Calculating adjusted metrics with {self.iterations} iterations")
        
        # Prepare a combined dataframe with raw metrics
        combined_metrics = (
            raw_efficiency
            .join(
                raw_tempo,
                on=["team_id", "season"],
                how="inner"
            )
        )
        
        # Maps from team_id to index and vice versa for faster lookups
        teams_by_season = {}
        for season in combined_metrics.select("season").unique().to_series().to_list():
            season_teams = combined_metrics.filter(pl.col("season") == season)
            team_ids = season_teams.select("team_id").to_series().to_list()
            teams_by_season[season] = {team_id: idx for idx, team_id in enumerate(team_ids)}
        
        # Get initial values
        seasons = combined_metrics.select("season").unique().to_series().to_list()
        
        offensive_ratings = {}
        defensive_ratings = {}
        tempo_ratings = {}
        
        # Initialize with raw values
        for season in seasons:
            season_teams = combined_metrics.filter(pl.col("season") == season)
            team_ids = season_teams.select("team_id").to_series().to_list()
            
            offensive_ratings[season] = {
                team_id: float(o_rtg)
                for team_id, o_rtg in zip(
                    season_teams.select("team_id").to_series().to_list(),
                    season_teams.select("raw_offensive_efficiency").to_series().to_list(),
                    strict=True
                )
            }
            
            defensive_ratings[season] = {
                team_id: float(d_rtg)
                for team_id, d_rtg in zip(
                    season_teams.select("team_id").to_series().to_list(),
                    season_teams.select("raw_defensive_efficiency").to_series().to_list(),
                    strict=True
                )
            }
            
            tempo_ratings[season] = {
                team_id: float(tempo)
                for team_id, tempo in zip(
                    season_teams.select("team_id").to_series().to_list(),
                    season_teams.select("raw_tempo").to_series().to_list(),
                    strict=True
                )
            }
        
        # Prepare schedules: only consider games between teams with ratings
        valid_games = (
            schedules
            .join(
                combined_metrics.select("team_id", "season"),
                left_on=["home_id", "season"],
                right_on=["team_id", "season"],
                how="inner"
            )
            .join(
                combined_metrics.select("team_id", "season"),
                left_on=["away_id", "season"],
                right_on=["team_id", "season"],
                how="inner"
            )
            .select("game_id", "season", "home_id", "away_id")
        )
        
        logger.info(f"Using {valid_games.height} games for adjusting ratings")
        
        # Perform iterative adjustment
        for i in range(self.iterations):
            # Calculate average ratings for each season
            avg_o_rtg = {season: sum(offensive_ratings[season].values()) / len(offensive_ratings[season]) 
                        for season in seasons}
            avg_d_rtg = {season: sum(defensive_ratings[season].values()) / len(defensive_ratings[season]) 
                        for season in seasons}
            avg_tempo = {season: sum(tempo_ratings[season].values()) / len(tempo_ratings[season]) 
                        for season in seasons}
            
            # Create new dictionaries for the next iteration
            new_offensive_ratings = {season: {} for season in seasons}
            new_defensive_ratings = {season: {} for season in seasons}
            new_tempo_ratings = {season: {} for season in seasons}
            
            # Process each game to create opponent-adjusted ratings
            for season in seasons:
                season_games = valid_games.filter(pl.col("season") == season)
                
                # Create dictionaries to accumulate opponent-adjusted values
                o_adj_values = {team_id: [] for team_id in offensive_ratings[season]}
                d_adj_values = {team_id: [] for team_id in defensive_ratings[season]}
                tempo_adj_values = {team_id: [] for team_id in tempo_ratings[season]}
                
                # Process each game
                for game in season_games.to_dicts():
                    home_id = game["home_id"]
                    away_id = game["away_id"]
                    
                    # Skip if either team is missing from our ratings
                    if (home_id not in offensive_ratings[season] or 
                        away_id not in offensive_ratings[season]):
                        continue
                    
                    # Calculate opponent-adjusted offensive efficiency
                    home_opp_adj = (offensive_ratings[season][home_id] * 
                                    avg_d_rtg[season] / defensive_ratings[season][away_id])
                    away_opp_adj = (offensive_ratings[season][away_id] * 
                                    avg_d_rtg[season] / defensive_ratings[season][home_id])
                    
                    o_adj_values[home_id].append(home_opp_adj)
                    o_adj_values[away_id].append(away_opp_adj)
                    
                    # Calculate opponent-adjusted defensive efficiency
                    home_def_adj = (defensive_ratings[season][home_id] * 
                                    avg_o_rtg[season] / offensive_ratings[season][away_id])
                    away_def_adj = (defensive_ratings[season][away_id] * 
                                    avg_o_rtg[season] / offensive_ratings[season][home_id])
                    
                    d_adj_values[home_id].append(home_def_adj)
                    d_adj_values[away_id].append(away_def_adj)
                    
                    # Calculate opponent-adjusted tempo
                    home_tempo_adj = (tempo_ratings[season][home_id] * 
                                    avg_tempo[season] / tempo_ratings[season][away_id])
                    away_tempo_adj = (tempo_ratings[season][away_id] * 
                                    avg_tempo[season] / tempo_ratings[season][home_id])
                    
                    tempo_adj_values[home_id].append(home_tempo_adj)
                    tempo_adj_values[away_id].append(away_tempo_adj)
                
                # Calculate new ratings based on opponent adjustments
                for team_id in offensive_ratings[season]:
                    if team_id in o_adj_values and o_adj_values[team_id]:
                        new_offensive_ratings[season][team_id] = sum(o_adj_values[team_id]) / len(o_adj_values[team_id])
                    else:
                        # Keep old value if no games to adjust from
                        new_offensive_ratings[season][team_id] = offensive_ratings[season][team_id]
                        
                    if team_id in d_adj_values and d_adj_values[team_id]:
                        new_defensive_ratings[season][team_id] = sum(d_adj_values[team_id]) / len(d_adj_values[team_id])
                    else:
                        new_defensive_ratings[season][team_id] = defensive_ratings[season][team_id]
                        
                    if team_id in tempo_adj_values and tempo_adj_values[team_id]:
                        new_tempo_ratings[season][team_id] = (
                            sum(tempo_adj_values[team_id]) / len(tempo_adj_values[team_id])
                        )
                    else:
                        new_tempo_ratings[season][team_id] = tempo_ratings[season][team_id]
            
            # Update the ratings dictionaries for the next iteration
            offensive_ratings = new_offensive_ratings
            defensive_ratings = new_defensive_ratings
            tempo_ratings = new_tempo_ratings
            
            logger.info(f"Completed iteration {i+1} of rating adjustments")
        
        # Convert adjusted ratings back to a DataFrame
        adjusted_ratings_data = []
        for season in seasons:
            for team_id in offensive_ratings[season]:
                adjusted_ratings_data.append({
                    "team_id": team_id,
                    "season": season,
                    "adjusted_offensive_efficiency": offensive_ratings[season][team_id],
                    "adjusted_defensive_efficiency": defensive_ratings[season][team_id],
                    "adjusted_tempo": tempo_ratings[season][team_id],
                    "net_rating": offensive_ratings[season][team_id] - defensive_ratings[season][team_id]
                })
        
        adjusted_ratings_df = pl.DataFrame(adjusted_ratings_data)
        
        logger.info(f"Calculated adjusted metrics for {adjusted_ratings_df.height} teams")
        return adjusted_ratings_df
    
    def _calculate_strength_of_schedule(self, 
                                      adjusted_metrics: pl.DataFrame,
                                      schedules: pl.DataFrame) -> pl.DataFrame:
        """Calculate strength of schedule based on opponent adjusted ratings.
        
        Args:
            adjusted_metrics: Adjusted team metrics DataFrame
            schedules: Game schedules DataFrame
            
        Returns:
            DataFrame with strength of schedule metrics
        """
        logger.info("Calculating strength of schedule metrics")
        
        # Create mappings for efficient lookups
        team_metrics = {}
        for row in adjusted_metrics.to_dicts():
            season = row["season"]
            team_id = row["team_id"]
            
            if season not in team_metrics:
                team_metrics[season] = {}
                
            team_metrics[season][team_id] = {
                "offensive": row["adjusted_offensive_efficiency"],
                "defensive": row["adjusted_defensive_efficiency"],
                "tempo": row["adjusted_tempo"],
                "net": row["net_rating"]
            }
        
        # Group games by team and season
        team_schedules = []
        
        for team_id in adjusted_metrics.select("team_id").unique().to_series().to_list():
            seasons = (adjusted_metrics
                      .filter(pl.col("team_id") == team_id)
                      .select("season")
                      .unique()
                      .to_series()
                      .to_list())
            
            for season in seasons:
                # Get all games for this team in this season
                # For home games, the away team is the opponent
                home_games = schedules.filter(
                    (pl.col("season") == season) & 
                    (pl.col("home_id") == team_id)
                ).select(
                    "game_id", 
                    "away_id", 
                    "neutral_site"
                ).rename(
                    {"away_id": "opponent_id"}
                ).with_columns(
                    pl.lit(team_id).alias("team_id")
                )
                
                # For away games, the home team is the opponent
                away_games = schedules.filter(
                    (pl.col("season") == season) & 
                    (pl.col("away_id") == team_id)
                ).select(
                    "game_id", 
                    "home_id", 
                    "neutral_site"
                ).rename(
                    {"home_id": "opponent_id"}
                ).with_columns(
                    pl.lit(team_id).alias("team_id")
                )
                
                # Add season column and combine
                all_games = pl.concat([home_games, away_games]).with_columns(
                    pl.lit(season).alias("season")
                )
                
                team_schedules.append(all_games)
        
        if team_schedules:
            all_team_schedules = pl.concat(team_schedules)
            
            # Calculate SOS metrics
            sos_records = []
            
            for team_id in adjusted_metrics.select("team_id").unique().to_series().to_list():
                seasons = (adjusted_metrics
                          .filter(pl.col("team_id") == team_id)
                          .select("season")
                          .unique()
                          .to_series()
                          .to_list())
                
                for season in seasons:
                    # Get all opponents for this team in this season
                    team_games = all_team_schedules.filter(
                        (pl.col("team_id") == team_id) & 
                        (pl.col("season") == season)
                    )
                    
                    # Skip if no games found
                    if team_games.height == 0:
                        continue
                    
                    # Get opponent metrics
                    opponent_metrics = []
                    for opponent_id in team_games.select("opponent_id").to_series().to_list():
                        if season in team_metrics and opponent_id in team_metrics[season]:
                            opponent_metrics.append(team_metrics[season][opponent_id])
                    
                    # Skip if no opponent metrics found
                    if not opponent_metrics:
                        continue
                    
                    # Calculate average opponent metrics
                    avg_opp_offensive = sum(m["offensive"] for m in opponent_metrics) / len(opponent_metrics)
                    avg_opp_defensive = sum(m["defensive"] for m in opponent_metrics) / len(opponent_metrics)
                    avg_opp_tempo = sum(m["tempo"] for m in opponent_metrics) / len(opponent_metrics)
                    avg_opp_net = sum(m["net"] for m in opponent_metrics) / len(opponent_metrics)
                    
                    sos_records.append({
                        "team_id": team_id,
                        "season": season,
                        "sos_offensive": avg_opp_offensive,
                        "sos_defensive": avg_opp_defensive,
                        "sos_tempo": avg_opp_tempo, 
                        "strength_of_schedule": avg_opp_net,
                        "num_opponents": len(opponent_metrics)
                    })
            
            sos_df = pl.DataFrame(sos_records)
            logger.info(f"Calculated strength of schedule for {sos_df.height} teams")
            return sos_df
        
        logger.warning("No valid schedules found for SOS calculation")
        return None
    
    def _calculate_tournament_experience(self, schedules: pl.DataFrame) -> pl.DataFrame:
        """Calculate tournament experience metrics.
        
        Args:
            schedules: Game schedules DataFrame
            
        Returns:
            DataFrame with tournament experience metrics
        """
        logger.info("Calculating tournament experience metrics")
        
        # First, check column types
        schema = schedules.schema
        
        # Identify NCAA tournament games (this depends on how they're marked in the data)
        tournament_games = None
        
        # Try different approaches to identify tournament games
        if "tournament" in schedules.columns and isinstance(schema["tournament"], pl.String):
            logger.info("Using 'tournament' column to identify NCAA tournament games")
            tournament_games = (
                schedules
                .filter(pl.col("tournament").str.contains("NCAA"))
                .select("game_id", "season", "home_id", "away_id")
            )
        elif "tourney_type" in schedules.columns and isinstance(schema["tourney_type"], pl.String):
            logger.info("Using 'tourney_type' column to identify NCAA tournament games")
            tournament_games = (
                schedules
                .filter(pl.col("tourney_type").str.contains("NCAA"))
                .select("game_id", "season", "home_id", "away_id")
            )
        elif "tournament_type" in schedules.columns and isinstance(schema["tournament_type"], pl.String):
            logger.info("Using 'tournament_type' column to identify NCAA tournament games")
            tournament_games = (
                schedules
                .filter(pl.col("tournament_type").str.contains("NCAA"))
                .select("game_id", "season", "home_id", "away_id")
            )  
        elif "season_type" in schedules.columns:
            if isinstance(schema["season_type"], pl.String):
                logger.info("Using 'season_type' column (string) to identify NCAA tournament games")
                tournament_games = (
                    schedules
                    .filter(pl.col("season_type").str.contains("(?i)postseason|(?i)NCAA|(?i)tournament"))
                    .select("game_id", "season", "home_id", "away_id")
                )
            elif isinstance(schema["season_type"], 
                          pl.Int8 | pl.Int16 | pl.Int32 | pl.Int64 | 
                          pl.UInt8 | pl.UInt16 | pl.UInt32 | pl.UInt64):
                logger.info("'season_type' column is integer, assuming 3 = postseason")
                # Some datasets use numeric codes for season types, often 3 = postseason
                tournament_games = (
                    schedules
                    .filter(pl.col("season_type") == 3)
                    .select("game_id", "season", "home_id", "away_id")
                )
        
        # If we couldn't identify tournament games, create a minimal experience dataset
        if tournament_games is None or tournament_games.height == 0:
            logger.warning("Could not identify NCAA tournament games. Creating minimal experience metrics.")
            
            # Create minimal tournament experience data based just on seasons played
            seasons_by_team = {}
            
            # Group games by team and count seasons
            for season in schedules.select("season").unique().to_series().to_list():
                for game in schedules.filter(pl.col("season") == season).select("home_id", "away_id").to_dicts():
                    home_id = game["home_id"]
                    away_id = game["away_id"]
                    
                    if home_id not in seasons_by_team:
                        seasons_by_team[home_id] = set()
                    if away_id not in seasons_by_team:
                        seasons_by_team[away_id] = set()
                        
                    seasons_by_team[home_id].add(season)
                    seasons_by_team[away_id].add(season)
            
            # Create tournament experience records for all teams in each season
            tournament_exp_data = []
            for season in schedules.select("season").unique().to_series().to_list():
                home_teams = (schedules
                            .filter(pl.col("season") == season)
                            .select("home_id")
                            .unique()
                            .to_series()
                            .to_list())
                
                for team_id in home_teams:
                    prev_seasons = [s for s in seasons_by_team.get(team_id, set()) if s < season]
                    tournament_exp_data.append({
                        "team_id": team_id,
                        "season": season,
                        # Use number of previous seasons as a proxy for experience
                        "seasons_experience": len(prev_seasons),
                        "tournament_appearances": 0,  # Not available
                        "tournament_games": 0,  # Not available
                    })
                    
            tournament_exp_df = pl.DataFrame(tournament_exp_data)
            logger.info(f"Created minimal experience metrics for {tournament_exp_df.height} teams")
            return tournament_exp_df
            
        logger.info(f"Found {tournament_games.height} tournament games for experience calculation")
            
        # Calculate tournament appearances and games by team
        tournament_exp_data = []
        
        for season in schedules.select("season").unique().to_series().to_list():
            # Get all teams from previous seasons' tournaments
            prev_seasons = [s for s in schedules.select("season").unique().to_series().to_list() if s < season]
            
            # Skip if no previous seasons
            if not prev_seasons:
                continue
                
            # Get tournament games from previous seasons
            prev_tournament_games = tournament_games.filter(pl.col("season").is_in(prev_seasons))
            
            # Get teams in tournament games
            teams_in_tourney = set()
            for game in prev_tournament_games.to_dicts():
                teams_in_tourney.add(game["home_id"])
                teams_in_tourney.add(game["away_id"])
            
            # Count appearances and games for each team
            team_appearances = {}
            team_games = {}
            
            for prev_season in prev_seasons:
                season_tourney_games = tournament_games.filter(pl.col("season") == prev_season)
                
                # Track which teams appeared in this season's tournament
                season_teams = set()
                for game in season_tourney_games.to_dicts():
                    home_id = game["home_id"]
                    away_id = game["away_id"]
                    
                    season_teams.add(home_id)
                    season_teams.add(away_id)
                    
                    # Count games
                    team_games[home_id] = team_games.get(home_id, 0) + 1
                    team_games[away_id] = team_games.get(away_id, 0) + 1
                
                # Count appearances
                for team_id in season_teams:
                    team_appearances[team_id] = team_appearances.get(team_id, 0) + 1
            
            # Get all teams in this season
            current_teams = set()
            for game in schedules.filter(pl.col("season") == season).select("home_id", "away_id").to_dicts():
                current_teams.add(game["home_id"])
                current_teams.add(game["away_id"])
            
            # Create tournament experience records for all teams in this season
            for team_id in current_teams:
                tournament_exp_data.append({
                    "team_id": team_id,
                    "season": season,
                    "tournament_appearances": team_appearances.get(team_id, 0),
                    "tournament_games": team_games.get(team_id, 0)
                })
        
        tournament_exp_df = pl.DataFrame(tournament_exp_data)
        logger.info(f"Calculated tournament experience for {tournament_exp_df.height} teams")
        return tournament_exp_df 