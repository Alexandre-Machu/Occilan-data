"""
Edition Processor - Orchestrates the complete data pipeline
Handles all 6 steps from team input to final statistics
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from pathlib import Path

from src.core.data_manager import EditionDataManager
from src.core.riot_client import RiotAPIClient
from src.core.stats_calculator import StatsCalculator
from src.parsers.opgg_parser import OPGGParser

logger = logging.getLogger(__name__)


class EditionProcessor:
    """
    Orchestrates the complete data processing pipeline for an edition
    
    Pipeline steps:
    1. Parse teams (manual or CSV) → teams.json
    2. Fetch PUUIDs (Account-V1) → teams_with_puuid.json
    3. Fetch ranks (League-V4) → teams_with_puuid.json (updated)
    4. Fetch match IDs (Match-V5) → tournament_matches.json
    5. Fetch match details (Match-V5) → match_details.json
    6. Calculate stats → general_stats.json
    """
    
    def __init__(self, edition_id: int, api_key: str, 
                 progress_callback: Optional[Callable[[str, float], None]] = None):
        """
        Initialize processor
        
        Args:
            edition_id: Edition number
            api_key: Riot API key
            progress_callback: Optional callback function(message, progress) for UI updates
        """
        self.edition_id = edition_id
        self.data_manager = EditionDataManager(edition_id)
        self.riot_client = RiotAPIClient(api_key)
        self.stats_calculator = StatsCalculator()
        self.opgg_parser = OPGGParser()
        self.progress_callback = progress_callback
        
        self.errors = []
        self.warnings = []
    
    def _update_progress(self, message: str, progress: float):
        """Update progress via callback"""
        logger.info(f"[{progress:.1f}%] {message}")
        if self.progress_callback:
            self.progress_callback(message, progress)
    
    def _log_error(self, message: str):
        """Log and store error"""
        logger.error(message)
        self.errors.append(message)
    
    def _log_warning(self, message: str):
        """Log and store warning"""
        logger.warning(message)
        self.warnings.append(message)
    
    # ========================================
    # STEP 1: Parse teams
    # ========================================
    
    def step1_parse_teams_manual(self, team_name: str, opgg_link: str, 
                                 roles: List[str] = None) -> bool:
        """
        Step 1: Parse a single team from OP.GG link
        
        Args:
            team_name: Team name
            opgg_link: OP.GG multisearch URL
            roles: List of roles (default: TOP, JGL, MID, ADC, SUP)
        
        Returns:
            True if successful
        """
        self._update_progress(f"Parsing team: {team_name}", 0)
        
        try:
            if not self.opgg_parser.validate_opgg_link(opgg_link):
                self._log_error(f"Invalid OP.GG link for {team_name}")
                return False
            
            if roles is None:
                roles = ["TOP", "JGL", "MID", "ADC", "SUP"]
            
            team_data = self.opgg_parser.parse_team_opgg(team_name, opgg_link, roles)
            
            if len(team_data["players"]) != 5:
                self._log_error(f"Expected 5 players, got {len(team_data['players'])} for {team_name}")
                return False
            
            self.data_manager.add_team(team_data)
            self._update_progress(f"Team {team_name} added successfully", 100)
            
            return True
            
        except Exception as e:
            self._log_error(f"Error parsing team {team_name}: {str(e)}")
            return False
    
    # ========================================
    # STEP 2: Fetch PUUIDs
    # ========================================
    
    def step2_fetch_puuids(self) -> Dict[str, Any]:
        """
        Step 2: Fetch PUUIDs for all players using Account-V1
        
        Returns:
            Updated teams_with_puuid data
        """
        self._update_progress("Fetching PUUIDs from Riot API...", 0)
        
        teams = self.data_manager.load_teams()
        
        if not teams:
            self._log_error("No teams found. Run step 1 first.")
            return {}
        
        teams_with_puuid = {}
        # teams is a dict, not a list
        total_players = sum(len(team_data["players"]) for team_data in teams.values())
        processed_players = 0
        
        for team_name, team_data in teams.items():
            teams_with_puuid[team_name] = {
                "name": team_name,
                "opgg_link": team_data.get("opgg_link", ""),
                "players": []
            }
            
            for player in team_data["players"]:
                game_name = player["gameName"]
                tag_line = player["tagLine"]
                role = player["role"]
                
                self._update_progress(
                    f"Fetching PUUID for {game_name}#{tag_line}...",
                    (processed_players / total_players) * 100
                )
                
                try:
                    # Fetch account info
                    account_info = self.riot_client.get_account_by_riot_id(game_name, tag_line)
                    
                    if account_info:
                        puuid = account_info["puuid"]
                        
                        # Fetch summoner info (for level)
                        summoner_info = self.riot_client.get_summoner_by_puuid(puuid)
                        
                        player_data = {
                            "gameName": game_name,
                            "tagLine": tag_line,
                            "role": role,
                            "puuid": puuid,
                            "summonerLevel": summoner_info.get("summonerLevel", 0) if summoner_info else 0,
                            "profileIconId": summoner_info.get("profileIconId", 0) if summoner_info else 0
                        }
                        
                        teams_with_puuid[team_name]["players"].append(player_data)
                        
                    else:
                        self._log_warning(f"Could not fetch PUUID for {game_name}#{tag_line}")
                        
                except Exception as e:
                    self._log_error(f"Error fetching PUUID for {game_name}#{tag_line}: {str(e)}")
                
                processed_players += 1
        
        # Save
        self.data_manager.save_teams_with_puuid(teams_with_puuid)
        self._update_progress(f"PUUIDs fetched: {processed_players} players", 100)
        
        return teams_with_puuid
    
    # ========================================
    # STEP 3: Fetch ranks
    # ========================================
    
    def step3_fetch_ranks(self) -> Dict[str, Any]:
        """
        Step 3: Fetch ranked info for all players using League-V4
        
        Returns:
            Updated teams_with_puuid data with ranks
        """
        self._update_progress("Fetching ranks from Riot API...", 0)
        
        teams_with_puuid = self.data_manager.load_teams_with_puuid()
        
        if not teams_with_puuid:
            self._log_error("No teams with PUUID found. Run step 2 first.")
            return {}
        
        total_players = sum(len(team["players"]) for team in teams_with_puuid.values())
        processed_players = 0
        
        for team_name, team_data in teams_with_puuid.items():
            for player in team_data["players"]:
                puuid = player.get("puuid")
                game_name = player.get("gameName")
                tag_line = player.get("tagLine")
                
                if not puuid:
                    self._log_warning(f"No PUUID for {game_name}#{tag_line}, skipping rank fetch")
                    processed_players += 1
                    continue
                
                self._update_progress(
                    f"Fetching rank for {game_name}#{tag_line}...",
                    (processed_players / total_players) * 100
                )
                
                try:
                    ranked_info = self.riot_client.get_ranked_info(puuid)
                    
                    if ranked_info:
                        player["tier"] = ranked_info.get("tier", "UNRANKED")
                        player["rank"] = ranked_info.get("rank", "")
                        player["leaguePoints"] = ranked_info.get("leaguePoints", 0)
                        player["wins"] = ranked_info.get("wins", 0)
                        player["losses"] = ranked_info.get("losses", 0)
                        
                        total_games = player["wins"] + player["losses"]
                        player["winrate"] = round((player["wins"] / total_games * 100), 2) if total_games > 0 else 0
                    else:
                        player["tier"] = "UNRANKED"
                        player["rank"] = ""
                        player["leaguePoints"] = 0
                        player["wins"] = 0
                        player["losses"] = 0
                        player["winrate"] = 0
                        
                except Exception as e:
                    self._log_error(f"Error fetching rank for {game_name}#{tag_line}: {str(e)}")
                
                processed_players += 1
        
        # Save
        self.data_manager.save_teams_with_puuid(teams_with_puuid)
        self._update_progress(f"Ranks fetched: {processed_players} players", 100)
        
        return teams_with_puuid
    
    # ========================================
    # STEP 4: Fetch match IDs
    # ========================================
    
    def step4_fetch_match_ids(self, start_timestamp: int = None, 
                              end_timestamp: int = None,
                              use_tourney_filter: bool = True) -> Dict[str, Any]:
        """
        Step 4: Fetch match IDs for all teams using Match-V5
        
        OPTIMISATION: Utilise type="tourney" et 1 seul joueur par équipe
        (tous les joueurs d'une équipe jouent les mêmes matchs de tournoi)
        
        Args:
            start_timestamp: Start date timestamp (epoch seconds)
            end_timestamp: End date timestamp (epoch seconds)
            use_tourney_filter: Si True, utilise type="tourney" (recommandé)
        
        Returns:
            Tournament matches data: {"team_name": ["match_id1", ...]}
        """
        self._update_progress("Fetching match IDs from Riot API...", 0)
        
        teams_with_puuid = self.data_manager.load_teams_with_puuid()
        
        if not teams_with_puuid:
            self._log_error("No teams with PUUID found. Run step 2 first.")
            return {}
        
        # Get dates from config if not provided
        if start_timestamp is None or end_timestamp is None:
            config = self.data_manager.load_config()
            if config:
                # Convert date strings to timestamps
                from datetime import datetime
                start_date = datetime.strptime(config.get("start_date", "2025-01-01"), "%Y-%m-%d")
                end_date = datetime.strptime(config.get("end_date", "2025-12-31"), "%Y-%m-%d")
                start_timestamp = int(start_date.timestamp())
                end_timestamp = int(end_date.timestamp())
        
        tournament_matches = {}
        total_teams = len(teams_with_puuid)
        processed_teams = 0
        
        for team_name, team_data in teams_with_puuid.items():
            self._update_progress(
                f"Fetching matches for team: {team_name}...",
                (processed_teams / total_teams) * 100
            )
            
            # OPTIMISATION: Prendre seulement le premier joueur
            # (tous jouent les mêmes matchs de tournoi)
            if not team_data.get("players"):
                logger.warning(f"No players found for team {team_name}")
                processed_teams += 1
                continue
            
            first_player = team_data["players"][0]
            puuid = first_player.get("puuid")
            game_name = first_player.get("gameName", "Unknown")
            
            if not puuid:
                logger.warning(f"No PUUID for {game_name} in {team_name}")
                processed_teams += 1
                continue
            
            try:
                # Vérifier si l'édition a un queue_id spécifique (ex: 3130 pour ARURF)
                config = self.data_manager.load_config()
                custom_queue_id = config.get("queue_id") if config else None
                
                if custom_queue_id:
                    # Mode spécial avec queue ID custom (ex: ARURF 3130)
                    match_ids = self.riot_client.get_match_ids_by_puuid(
                        puuid=puuid,
                        start_time=start_timestamp,
                        end_time=end_timestamp,
                        queue_id=custom_queue_id,  # 🎯 Queue spécifique (ARURF, etc.)
                        count=50
                    )
                    logger.info(f"Using custom queue {custom_queue_id} for {team_name}")
                elif use_tourney_filter:
                    # Méthode optimale: type="tourney"
                    match_ids = self.riot_client.get_match_ids_by_puuid(
                        puuid=puuid,
                        start_time=start_timestamp,
                        end_time=end_timestamp,
                        match_type="tourney",  # 🎯 Filtre tournois !
                        count=50
                    )
                else:
                    # Ancienne méthode: queue_id=0 (custom games)
                    match_ids = self.riot_client.get_match_ids_by_puuid(
                        puuid=puuid,
                        start_time=start_timestamp,
                        end_time=end_timestamp,
                        queue_id=0,
                        count=100
                    )
                
                if match_ids:
                    tournament_matches[team_name] = match_ids
                    logger.info(f"{team_name} ({game_name}): {len(match_ids)} matches found")
                else:
                    logger.warning(f"{team_name} ({game_name}): No matches found")
                    
            except Exception as e:
                self._log_error(f"Error fetching matches for {team_name}: {str(e)}")
            
            processed_teams += 1
        
        # Sauvegarder dans tournament_matches.json
        self.data_manager.save_tournament_matches(tournament_matches)
        
        self._update_progress(f"✅ Match IDs fetched for {len(tournament_matches)} teams", 100)
        
        return tournament_matches
    
    # ========================================
    # STEP 5: Fetch match details
    # ========================================
    
    def step5_fetch_match_details(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Step 5: Fetch detailed match data using Match-V5
        
        Args:
            use_cache: Whether to use cached matches
        
        Returns:
            Match details data
        """
        self._update_progress("Fetching match details from Riot API...", 0)
        
        tournament_matches = self.data_manager.load_tournament_matches()
        
        if not tournament_matches:
            self._log_error("No match IDs found. Run step 4 first.")
            return {}
        
        # Collect all unique match IDs - tournament_matches is Dict[str, List[str]]
        all_match_ids = set()
        for match_ids_list in tournament_matches.values():
            if isinstance(match_ids_list, list):
                all_match_ids.update(match_ids_list)
        
        all_match_ids = list(all_match_ids)
        total_matches = len(all_match_ids)
        
        logger.info(f"Total unique matches to fetch: {total_matches}")
        
        # Progress tracking for callback
        def match_progress_callback(match_id: str, current: int, total: int):
            progress = (current / total) * 100
            self._update_progress(f"Fetching match {current}/{total}: {match_id}", progress)
        
        try:
            match_details = self.riot_client.get_all_match_details(
                match_ids=all_match_ids,
                use_cache=use_cache,
                progress_callback=match_progress_callback
            )
            
            # Save each match detail
            for match_id, match_data in match_details.items():
                self.data_manager.add_match_detail(match_id, match_data)
            
            self._update_progress(f"Match details fetched: {len(match_details)} matches", 100)
            
            return match_details
            
        except Exception as e:
            self._log_error(f"Error fetching match details: {str(e)}")
            return {}
    
    # ========================================
    # STEP 6: Calculate statistics
    # ========================================
    
    def step6_calculate_stats(self) -> Dict[str, Any]:
        """
        Step 6: Calculate all tournament statistics
        
        Returns:
            General stats data
        """
        self._update_progress("Calculating statistics...", 0)
        
        match_details = self.data_manager.load_match_details()
        teams_with_puuid = self.data_manager.load_teams_with_puuid()
        
        if not match_details:
            self._log_error("No match details found. Run step 5 first.")
            return {}
        
        if not teams_with_puuid:
            self._log_error("No teams with PUUID found. Run step 2 first.")
            return {}
        
        try:
            stats = self.stats_calculator.calculate_all_stats(match_details, teams_with_puuid)
            
            # Save general_stats.json (contains everything)
            self.data_manager.save_general_stats(stats)
            
            # Generate team_stats.json in the format expected by Stats Équipes page
            # Structure: { "TeamName": { "team_stats": {...}, "players": {...} } }
            if "team_stats" in stats and "player_stats" in stats:
                import json
                
                team_stats_formatted = {}
                
                for team_name, team_data in stats["team_stats"].items():
                    # Initialize team structure
                    team_stats_formatted[team_name] = {
                        "team_stats": team_data,
                        "players": {}
                    }
                    
                    # Add players belonging to this team
                    for player_name, player_data in stats["player_stats"].items():
                        if player_data.get("team") == team_name:
                            team_stats_formatted[team_name]["players"][player_name] = player_data
                
                # Save to team_stats.json
                team_stats_path = self.data_manager.edition_path / "team_stats.json"
                with open(team_stats_path, 'w', encoding='utf-8') as f:
                    json.dump(team_stats_formatted, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved team_stats.json with {len(team_stats_formatted)} teams")
            
            self._update_progress(
                f"Stats calculated: {stats['metadata']['total_players']} players, "
                f"{stats['metadata']['total_matches_processed']} matches",
                100
            )
            
            return stats
            
        except Exception as e:
            self._log_error(f"Error calculating stats: {str(e)}")
            return {}
    
    # ========================================
    # FULL PIPELINE
    # ========================================
    
    def run_full_pipeline(self, start_timestamp: int = None, 
                         end_timestamp: int = None,
                         use_cache: bool = True) -> Dict[str, Any]:
        """
        Run the complete pipeline (steps 2-6)
        Assumes teams are already added (step 1)
        
        Args:
            start_timestamp: Start date for match history
            end_timestamp: End date for match history
            use_cache: Use cached matches
        
        Returns:
            Pipeline results summary
        """
        
        logger.info(f"Starting full pipeline for edition {self.edition_id}")
        start_time = datetime.now()
        
        results = {
            "edition_id": self.edition_id,
            "start_time": start_time.isoformat(),
            "steps": {},
            "errors": [],
            "warnings": []
        }
        
        # Step 2: Fetch PUUIDs
        try:
            self._update_progress("STEP 2/6: Fetching PUUIDs...", 16)
            teams_with_puuid = self.step2_fetch_puuids()
            results["steps"]["step2_puuids"] = {
                "success": len(teams_with_puuid) > 0,
                "teams_count": len(teams_with_puuid)
            }
        except Exception as e:
            self._log_error(f"Step 2 failed: {str(e)}")
            results["steps"]["step2_puuids"] = {"success": False, "error": str(e)}
            results["success"] = False
            results["errors"] = self.errors
            results["warnings"] = self.warnings
            return results
        
        # Step 3: Fetch ranks
        try:
            self._update_progress("STEP 3/6: Fetching ranks...", 33)
            teams_with_puuid = self.step3_fetch_ranks()
            results["steps"]["step3_ranks"] = {"success": True}
        except Exception as e:
            self._log_error(f"Step 3 failed: {str(e)}")
            results["steps"]["step3_ranks"] = {"success": False, "error": str(e)}
        
        # Step 4: Fetch match IDs
        try:
            self._update_progress("STEP 4/6: Fetching match IDs...", 50)
            tournament_matches = self.step4_fetch_match_ids(start_timestamp, end_timestamp)
            
            # Count total matches - tournament_matches is Dict[str, List[str]]
            total_matches = sum(
                len(match_ids) if isinstance(match_ids, list) else 0
                for match_ids in tournament_matches.values()
            )
            
            results["steps"]["step4_match_ids"] = {
                "success": total_matches > 0,
                "total_match_ids": total_matches
            }
        except Exception as e:
            self._log_error(f"Step 4 failed: {str(e)}")
            results["steps"]["step4_match_ids"] = {"success": False, "error": str(e)}
            results["success"] = False
            results["errors"] = self.errors
            results["warnings"] = self.warnings
            return results
        
        # Step 5: Fetch match details
        try:
            self._update_progress("STEP 5/6: Fetching match details...", 66)
            match_details = self.step5_fetch_match_details(use_cache)
            results["steps"]["step5_match_details"] = {
                "success": len(match_details) > 0,
                "matches_fetched": len(match_details)
            }
        except Exception as e:
            self._log_error(f"Step 5 failed: {str(e)}")
            results["steps"]["step5_match_details"] = {"success": False, "error": str(e)}
            results["success"] = False
            results["errors"] = self.errors
            results["warnings"] = self.warnings
            return results
        
        # Step 6: Calculate stats
        try:
            self._update_progress("STEP 6/6: Calculating statistics...", 83)
            stats = self.step6_calculate_stats()
            results["steps"]["step6_stats"] = {
                "success": len(stats) > 0,
                "players_analyzed": stats.get("metadata", {}).get("total_players", 0),
                "matches_analyzed": stats.get("metadata", {}).get("total_matches_processed", 0)
            }
        except Exception as e:
            self._log_error(f"Step 6 failed: {str(e)}")
            results["steps"]["step6_stats"] = {"success": False, "error": str(e)}
        
        # Finalize
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results["end_time"] = end_time.isoformat()
        results["duration_seconds"] = duration
        results["errors"] = self.errors
        results["warnings"] = self.warnings
        results["success"] = all(
            step.get("success", False) 
            for step in results["steps"].values()
        )
        
        self._update_progress("Pipeline completed!", 100)
        
        logger.info(f"Pipeline completed in {duration:.1f}s")
        logger.info(f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
        
        return results
