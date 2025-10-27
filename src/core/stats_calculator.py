"""
Stats Calculator for OcciLan Stats
Calculates player stats, team stats, records, and champion statistics from match data
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class StatsCalculator:
    # Static mapping for championId to championName (partial, for demo; extend as needed)
    CHAMPION_ID_TO_NAME = {
        266: "Aatrox", 103: "Ahri", 84: "Akali", 166: "Akshan", 12: "Alistar", 32: "Amumu", 34: "Anivia", 1: "Annie",
        523: "Aphelios", 22: "Ashe", 136: "AurelionSol", 268: "Azir", 432: "Bard", 53: "Blitzcrank", 63: "Brand",
        201: "Braum", 51: "Caitlyn", 164: "Camille", 69: "Cassiopeia", 31: "Chogath", 42: "Corki", 122: "Darius",
        131: "Diana", 119: "Draven", 36: "DrMundo", 245: "Ekko", 60: "Elise", 28: "Evelynn", 81: "Ezreal",
        9: "Fiddlesticks", 114: "Fiora", 105: "Fizz", 3: "Galio", 41: "Gangplank", 86: "Garen", 150: "Gnar",
        79: "Gragas", 104: "Graves", 887: "Gwen", 120: "Hecarim", 74: "Heimerdinger", 420: "Illaoi", 39: "Irelia",
        427: "Ivern", 40: "Janna", 59: "JarvanIV", 24: "Jax", 126: "Jayce", 202: "Jhin", 222: "Jinx", 145: "Kaisa",
        429: "Kalista", 43: "Karma", 30: "Karthus", 38: "Kassadin", 55: "Katarina", 10: "Kayle", 141: "Kayn",
        85: "Kennen", 121: "Khazix", 203: "Kindred", 240: "Kled", 96: "KogMaw", 7: "Leblanc", 64: "LeeSin",
        89: "Leona", 876: "Lillia", 127: "Lissandra", 236: "Lucian", 117: "Lulu", 99: "Lux", 54: "Malphite",
        90: "Malzahar", 57: "Maokai", 11: "MasterYi", 21: "MissFortune", 62: "Wukong", 82: "Mordekaiser",
        25: "Morgana", 267: "Nami", 75: "Nasus", 111: "Nautilus", 518: "Neeko", 76: "Nidalee", 56: "Nocturne",
        20: "Nunu", 2: "Olaf", 61: "Orianna", 516: "Ornn", 80: "Pantheon", 78: "Poppy", 555: "Pyke",
        246: "Qiyana", 133: "Quinn", 497: "Rakan", 33: "Rammus", 421: "RekSai", 526: "Rell", 58: "Renekton",
        107: "Rengar", 92: "Riven", 68: "Rumble", 13: "Ryze", 360: "Samira", 113: "Sejuani", 235: "Senna",
        147: "Seraphine", 875: "Sett", 35: "Shaco", 98: "Shen", 102: "Shyvana", 27: "Singed", 14: "Sion",
        15: "Sivir", 72: "Skarner", 37: "Sona", 16: "Soraka", 50: "Swain", 517: "Sylas", 134: "Syndra",
        223: "TahmKench", 163: "Taliyah", 91: "Talon", 44: "Taric", 17: "Teemo", 412: "Thresh", 18: "Tristana",
        48: "Trundle", 23: "Tryndamere", 4: "TwistedFate", 29: "Twitch", 77: "Udyr", 6: "Urgot", 110: "Varus",
        67: "Vayne", 45: "Veigar", 161: "Velkoz", 711: "Vex", 254: "Vi", 234: "Viego", 112: "Viktor",
        8: "Vladimir", 106: "Volibear", 19: "Warwick", 498: "Xayah", 101: "Xerath", 5: "XinZhao", 157: "Yasuo",
        777: "Yone", 83: "Yorick", 350: "Yuumi", 154: "Zac", 238: "Zed", 221: "Zeri", 115: "Ziggs",
        26: "Zilean", 142: "Zoe", 143: "Zyra"
    }
    """Calculates comprehensive tournament statistics from match details"""
    
    def __init__(self):
        self.stats = self._initialize_stats()
    
    def _initialize_stats(self) -> Dict[str, Any]:
        """Initialize the statistics structure"""
        return {
            "longest_game": {"match_id": None, "duration": 0, "teams": None, "formatted": "0:00"},
            "shortest_game": {"match_id": None, "duration": float("inf"), "teams": None, "formatted": "0:00"},
            "most_kills_game": {"match_id": None, "kills": 0, "teams": None},
            "least_kills_game": {"match_id": None, "kills": float("inf"), "teams": None},
            "highest_vision_game": {"match_id": None, "score": 0, "player": None, "team": None, "champion": None},
            "highest_cs_per_min_game": {"match_id": None, "cs_per_min": 0, "player": None, "team": None, "champion": None},
            "champion_stats": {
                "picks": {},  # {champion_name: count}
                "bans": {},   # {champion_name: count}
                "wins": {}    # {champion_name: win_count}
            },
            "player_stats": {},  # {player_name: {...}}
            "team_stats": {},    # {team_name: {...}}
            "records": {}        # Best player for each stat
        }
    
    def _initialize_player_stats(self, player_name: str, team_name: str) -> Dict[str, Any]:
        """Initialize player statistics structure"""
        return {
            "player_name": player_name,
            "team": team_name,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "total_kills": 0,
            "total_deaths": 0,
            "total_assists": 0,
            "total_cs": 0,
            "total_vision_score": 0,
            "total_gold_earned": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "total_game_duration": 0,  # in seconds
            "champions_played": [],
            "champion_stats": {},  # {champion_name: {games, wins, kills, deaths, assists}}
            # Averages (calculated later)
            "average_kills": 0,
            "average_deaths": 0,
            "average_assists": 0,
            "average_kda": 0,
            "average_cs_per_min": 0,
            "average_cs_per_minute": 0,  # Alias for compatibility
            "average_vision_score": 0,
            "average_gold_per_min": 0,
            "average_damage_per_min": 0,
            "winrate": 0,
            "unique_champions_played": 0
        }
    
    def _initialize_team_stats(self, team_name: str) -> Dict[str, Any]:
        """Initialize team statistics structure"""
        return {
            "team_name": team_name,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "total_kills": 0,
            "total_deaths": 0,
            "total_game_duration": 0,
            "winrate": 0,
            "average_game_duration": 0
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds / 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}:{remaining_seconds:02d}"
    
    def _format_champion_name(self, champion_name: str) -> str:
        """Format champion name (handle special cases)"""
        special_cases = {
            "MonkeyKing": "Wukong",
            "FiddleSticks": "Fiddlesticks"
        }
        return special_cases.get(champion_name, champion_name)
    
    def _get_team_name_from_puuid(self, puuid: str, teams_with_puuid: Dict[str, Any]) -> str:
        """Get team name from player PUUID"""
        for team_name, team_data in teams_with_puuid.items():
            for player in team_data.get("players", []):
                if player.get("puuid") == puuid:
                    return team_name
        return "Unknown Team"
    
    def _get_player_name_from_puuid(self, puuid: str, teams_with_puuid: Dict[str, Any]) -> str:
        """Get player name from PUUID"""
        for team_data in teams_with_puuid.values():
            for player in team_data.get("players", []):
                if player.get("puuid") == puuid:
                    return f"{player.get('gameName', 'Unknown')}#{player.get('tagLine', '0000')}"
        return "Unknown Player"
    
    def _process_match(self, match_id: str, match_data: Dict[str, Any], 
                      teams_with_puuid: Dict[str, Any]) -> None:
        """Process a single match and update statistics"""
        
        info = match_data.get("info", {})
        duration_raw = info.get("gameDuration", 0)
        
        # Convertir duration en int (peut être string ou int selon l'API)
        try:
            duration = int(duration_raw) if duration_raw else 0
        except (ValueError, TypeError):
            logger.warning(f"Match {match_id}: invalid duration '{duration_raw}', skipping")
            return
        
        if duration == 0:
            logger.warning(f"Match {match_id}: duration is 0, skipping")
            return
        
        participants = info.get("participants", [])
        teams = info.get("teams", [])
        
        if not participants:
            logger.warning(f"Match {match_id}: no participants found")
            return
        
        # Track which teams already processed this match (to avoid counting it multiple times)
        teams_processed_in_match = set()
        
        # Get team names from first participant of each team
        team_100_name = None
        team_200_name = None
        
        for participant in participants:
            puuid = participant.get("puuid")
            team_id = participant.get("teamId")
            team_name = self._get_team_name_from_puuid(puuid, teams_with_puuid)
            
            if team_id == 100 and team_100_name is None:
                team_100_name = team_name
            elif team_id == 200 and team_200_name is None:
                team_200_name = team_name
        
        match_teams = f"{team_100_name} vs {team_200_name}"
        
        # Game duration records
        if duration > self.stats["longest_game"]["duration"]:
            self.stats["longest_game"].update({
                "match_id": match_id,
                "duration": duration,
                "formatted": self._format_duration(duration),
                "teams": match_teams
            })
        
        if duration < self.stats["shortest_game"]["duration"]:
            self.stats["shortest_game"].update({
                "match_id": match_id,
                "duration": duration,
                "formatted": self._format_duration(duration),
                "teams": match_teams
            })
        
        # Process participants
        total_kills = 0
        
        for participant in participants:
            puuid = participant.get("puuid")
            team_id = participant.get("teamId")
            team_name = self._get_team_name_from_puuid(puuid, teams_with_puuid)
            player_name = self._get_player_name_from_puuid(puuid, teams_with_puuid)
            champion_name = self._format_champion_name(participant.get("championName", "Unknown"))
            
            # Initialize player stats if needed
            if player_name not in self.stats["player_stats"]:
                self.stats["player_stats"][player_name] = self._initialize_player_stats(player_name, team_name)
            
            # Initialize team stats if needed
            if team_name not in self.stats["team_stats"]:
                self.stats["team_stats"][team_name] = self._initialize_team_stats(team_name)
            
            player_stats = self.stats["player_stats"][player_name]
            team_stats = self.stats["team_stats"][team_name]
            
            # Extract participant data
            kills = participant.get("kills", 0)
            deaths = participant.get("deaths", 0)
            assists = participant.get("assists", 0)
            cs = participant.get("totalMinionsKilled", 0) + participant.get("neutralMinionsKilled", 0)
            vision_score = participant.get("visionScore", 0)
            gold_earned = participant.get("goldEarned", 0)
            damage_dealt = participant.get("totalDamageDealtToChampions", 0)
            damage_taken = participant.get("totalDamageTaken", 0)
            win = participant.get("win", False)
            
            # Update player stats
            player_stats["games_played"] += 1
            player_stats["wins"] += 1 if win else 0
            player_stats["losses"] += 0 if win else 1
            player_stats["total_kills"] += kills
            player_stats["total_deaths"] += deaths
            player_stats["total_assists"] += assists
            player_stats["total_cs"] += cs
            player_stats["total_vision_score"] += vision_score
            player_stats["total_gold_earned"] += gold_earned
            player_stats["total_damage_dealt"] += damage_dealt
            player_stats["total_damage_taken"] += damage_taken
            player_stats["total_game_duration"] += duration
            
            if champion_name not in player_stats["champions_played"]:
                player_stats["champions_played"].append(champion_name)
            
            # Update champion stats for player
            if champion_name not in player_stats["champion_stats"]:
                player_stats["champion_stats"][champion_name] = {
                    "games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0
                }
            
            player_stats["champion_stats"][champion_name]["games"] += 1
            player_stats["champion_stats"][champion_name]["wins"] += 1 if win else 0
            player_stats["champion_stats"][champion_name]["kills"] += kills
            player_stats["champion_stats"][champion_name]["deaths"] += deaths
            player_stats["champion_stats"][champion_name]["assists"] += assists
            
            # Update team stats (only count match once per team)
            if team_name not in teams_processed_in_match:
                teams_processed_in_match.add(team_name)
                team_stats["games_played"] += 1
                team_stats["wins"] += 1 if win else 0
                team_stats["losses"] += 0 if win else 1
                team_stats["total_game_duration"] += duration
            
            # Always update kills/deaths (sum across all players)
            team_stats["total_kills"] += kills
            team_stats["total_deaths"] += deaths
            
            # Update global champion stats
            champ_stats = self.stats["champion_stats"]
            
            if champion_name not in champ_stats["picks"]:
                champ_stats["picks"][champion_name] = 0
                champ_stats["wins"][champion_name] = 0
            
            champ_stats["picks"][champion_name] += 1
            if win:
                champ_stats["wins"][champion_name] += 1
            
            # Records
            cs_per_min = float(cs) / (float(duration) / 60) if duration > 0 else 0
            
            if vision_score > self.stats["highest_vision_game"]["score"]:
                self.stats["highest_vision_game"].update({
                    "match_id": match_id,
                    "score": vision_score,
                    "player": player_name,
                    "team": team_name,
                    "champion": champion_name
                })
            
            if cs_per_min > self.stats["highest_cs_per_min_game"]["cs_per_min"]:
                self.stats["highest_cs_per_min_game"].update({
                    "match_id": match_id,
                    "cs_per_min": round(cs_per_min, 1),
                    "player": player_name,
                    "team": team_name,
                    "champion": champion_name
                })
            
            total_kills += kills
        
        # Kills records
        if total_kills > self.stats["most_kills_game"]["kills"]:
            self.stats["most_kills_game"].update({
                "match_id": match_id,
                "kills": total_kills,
                "teams": match_teams
            })
        
        if total_kills < self.stats["least_kills_game"]["kills"]:
            self.stats["least_kills_game"].update({
                "match_id": match_id,
                "kills": total_kills,
                "teams": match_teams
            })
        
        # Process bans
        for team in teams:
            for ban in team.get("bans", []):
                champion_id = ban.get("championId")
                champion_name = self.CHAMPION_ID_TO_NAME.get(champion_id)
                if champion_name:
                    champ_stats = self.stats["champion_stats"]
                    if champion_name not in champ_stats["bans"]:
                        champ_stats["bans"][champion_name] = 0
                    champ_stats["bans"][champion_name] += 1
    
    def _calculate_averages(self) -> None:
        """Calculate averages for all players and teams"""
        
        # Player averages
        for player_name, player_stats in self.stats["player_stats"].items():
            games = int(player_stats["games_played"])
            
            if games > 0:
                minutes_played = float(player_stats["total_game_duration"]) / 60
                
                player_stats["average_kills"] = round(player_stats["total_kills"] / games, 2)
                player_stats["average_deaths"] = round(player_stats["total_deaths"] / games, 2)
                player_stats["average_assists"] = round(player_stats["total_assists"] / games, 2)
                player_stats["average_vision_score"] = round(player_stats["total_vision_score"] / games, 2)
                player_stats["winrate"] = round((player_stats["wins"] / games) * 100, 2)
                player_stats["unique_champions_played"] = len(player_stats["champions_played"])
                
                if minutes_played > 0:
                    cs_per_min = round(player_stats["total_cs"] / minutes_played, 2)
                    player_stats["average_cs_per_min"] = cs_per_min
                    player_stats["average_cs_per_minute"] = cs_per_min  # Alias for compatibility
                    player_stats["average_gold_per_min"] = round(player_stats["total_gold_earned"] / minutes_played, 0)
                    player_stats["average_damage_per_min"] = round(player_stats["total_damage_dealt"] / minutes_played, 0)
                
                # KDA calculation
                deaths = max(1, player_stats["total_deaths"])  # Avoid division by zero
                player_stats["average_kda"] = round(
                    (player_stats["total_kills"] + player_stats["total_assists"]) / deaths,
                    2
                )
        
        # Team averages
        for team_name, team_stats in self.stats["team_stats"].items():
            games = int(team_stats["games_played"])
            
            if games > 0:
                team_stats["winrate"] = round((float(team_stats["wins"]) / games) * 100, 2)
                team_stats["average_game_duration"] = round(float(team_stats["total_game_duration"]) / games, 0)
                team_stats["average_game_duration_formatted"] = self._format_duration(
                    team_stats["average_game_duration"]
                )
    
    def _calculate_records(self) -> None:
        """Find best players for each statistic"""
        
        stats_to_check = [
            ("total_kills", "Total Kills"),
            ("total_deaths", "Total Deaths"),
            ("total_assists", "Total Assists"),
            ("average_kills", "Average Kills"),
            ("average_deaths", "Average Deaths"),
            ("average_assists", "Average Assists"),
            ("average_kda", "Average KDA"),
            ("average_cs_per_min", "Average CS/min"),
            ("average_vision_score", "Average Vision Score"),
            ("average_gold_per_min", "Average Gold/min"),
            ("average_damage_per_min", "Average Damage/min"),
            ("unique_champions_played", "Unique Champions"),
            ("winrate", "Winrate %")
        ]
        
        for stat_key, stat_name in stats_to_check:
            max_value = float('-inf')
            best_player = None
            best_team = None
            
            for player_name, player_stats in self.stats["player_stats"].items():
                value = player_stats.get(stat_key, 0)
                
                if value > max_value:
                    max_value = value
                    best_player = player_name
                    best_team = player_stats["team"]
            
            self.stats["records"][stat_key] = {
                "stat_name": stat_name,
                "player": best_player,
                "team": best_team,
                "value": round(max_value, 2) if max_value != float('-inf') else 0
            }
    
    def _finalize_champion_stats(self) -> None:
        """Calculate final champion statistics"""
        
        champ_stats = self.stats["champion_stats"]
        
        # Most picked
        if champ_stats["picks"]:
            most_picked = max(champ_stats["picks"].items(), key=lambda x: x[1])
            self.stats["most_picked_champion"] = {
                "champion": most_picked[0],
                "picks": most_picked[1]
            }
        
        # Most banned
        if champ_stats["bans"]:
            most_banned = max(champ_stats["bans"].items(), key=lambda x: x[1])
            self.stats["most_banned_champion"] = {
                "champion": most_banned[0],
                "bans": most_banned[1]
            }
        
        # Calculate winrates for champions
        champ_stats["winrates"] = {}
        for champion, picks in champ_stats["picks"].items():
            wins = champ_stats["wins"].get(champion, 0)
            winrate = (wins / picks * 100) if picks > 0 else 0
            champ_stats["winrates"][champion] = round(winrate, 2)
    
    def calculate_all_stats(self, match_details: Dict[str, Any], 
                           teams_with_puuid: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all tournament statistics
        
        Args:
            match_details: Dictionary of match data from match_details.json
            teams_with_puuid: Dictionary of team data from teams_with_puuid.json
        
        Returns:
            Complete statistics dictionary
        """
        
        logger.info(f"Calculating stats for {len(match_details)} matches")
        
        # Reset stats
        self.stats = self._initialize_stats()
        
        # Process each match
        processed = 0
        errors = 0
        
        for match_id, match_data in match_details.items():
            try:
                self._process_match(match_id, match_data, teams_with_puuid)
                processed += 1
            except Exception as e:
                logger.error(f"Error processing match {match_id}: {e}")
                errors += 1
        
        logger.info(f"Processed {processed} matches, {errors} errors")
        
        # Calculate averages
        self._calculate_averages()
        
        # Calculate records
        self._calculate_records()
        
        # Finalize champion stats
        self._finalize_champion_stats()
        
        # Add metadata
        self.stats["metadata"] = {
            "total_matches_processed": processed,
            "total_errors": errors,
            "total_players": len(self.stats["player_stats"]),
            "total_teams": len(self.stats["team_stats"])
        }
        
        return self.stats


# Standalone function for easy use
def calculate_stats(match_details: Dict[str, Any], 
                   teams_with_puuid: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all tournament statistics (standalone function)
    
    Args:
        match_details: Dictionary from match_details.json
        teams_with_puuid: Dictionary from teams_with_puuid.json
    
    Returns:
        Complete statistics dictionary
    """
    calculator = StatsCalculator()
    return calculator.calculate_all_stats(match_details, teams_with_puuid)
