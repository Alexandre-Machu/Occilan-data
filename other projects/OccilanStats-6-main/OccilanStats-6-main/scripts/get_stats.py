import json
import os
from typing import Dict, Any, List, Tuple

def format_duration(seconds: float) -> str:
    """Convertit les secondes en format MM:SS"""
    minutes = int(seconds / 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}:{remaining_seconds:02d}"

def format_champion_name(champion_name: str) -> str:
    """Formate le nom du champion (cas spéciaux)"""
    return "Wukong" if champion_name == "MonkeyKing" else champion_name

def get_team_name_from_id(team_id: int, participants: list, teams_data: Dict[str, Any]) -> str:
    """Récupère le vrai nom de l'équipe à partir de l'ID d'équipe"""
    for participant in participants:
        if participant.get("teamId") == team_id:
            puuid = participant.get("puuid")
            for team_name, team_info in teams_data.items():
                for player in team_info:
                    if player.get("puuid") == puuid:
                        return team_name
    return f"Team {team_id}"

def initialize_stats() -> Dict[str, Any]:
    """Initialise la structure des statistiques"""
    return {
        "longest_game": {"detail": None, "value": 0, "teams": None},
        "shortest_game": {"detail": None, "value": float("inf"), "teams": None},
        "most_kills_in_game": {"detail": None, "value": 0, "teams": None},
        "least_kills_in_game": {"detail": None, "value": float("inf"), "teams": None},
        "highest_vision_game": {"detail": None, "value": 0, "player": None, "team": None, "champion": None},
        "highest_cs_per_min": {"detail": None, "value": 0, "player": None, "team": None, "champion": None},
        "champion_stats": {"picks": {}, "bans": {}, "wins": {}},
        "player_stats": {},
        "records": {}
    }

def initialize_player_stats(team_name: str) -> Dict[str, Any]:
    """Initialise les statistiques d'un joueur"""
    return {
        "team": team_name,
        "total_kills": 0,
        "total_deaths": 0,
        "total_assists": 0,
        "games_played": 0,
        "total_cs": 0,
        "total_game_duration": 0,
        "total_vision_score": 0,
        "champions_played": [],
        "wins": 0
    }

def update_match_stats(stats: Dict[str, Any], match_id: str, match_data: Dict[str, Any], 
                      teams_data: Dict[str, Any], champ_data: Dict[str, Any]) -> None:
    """Met à jour les statistiques avec les données d'un match"""
    info = match_data["info"]
    duration_seconds = float(info.get("gameDuration", 0))
    if duration_seconds == 0:
        return

    participants = info.get("participants", [])
    teams = info.get("teams", [])
    
    team1_name = get_team_name_from_id(100, participants, teams_data)
    team2_name = get_team_name_from_id(200, participants, teams_data)
    match_teams = f"{team1_name} vs {team2_name}"

    # Stats de durée
    if duration_seconds > stats["longest_game"]["value"]:
        stats["longest_game"].update({
            "detail": match_id,
            "value": duration_seconds,
            "formatted_duration": format_duration(duration_seconds),
            "teams": match_teams
        })
    if duration_seconds < stats["shortest_game"]["value"]:
        stats["shortest_game"].update({
            "detail": match_id,
            "value": duration_seconds,
            "formatted_duration": format_duration(duration_seconds),
            "teams": match_teams
        })

    # Stats des participants
    total_kills = 0
    for participant in participants:
        champion_name = format_champion_name(participant.get("championName", "Unknown"))
        player_name = participant.get("riotIdGameName", "Unknown")
        team_name = team1_name if participant.get("teamId") == 100 else team2_name

        # Calcul des CS
        cs = participant.get("totalMinionsKilled", 0) + participant.get("neutralMinionsKilled", 0)
        cs_per_min = round(cs / (duration_seconds / 60), 1) if duration_seconds > 0 else 0

        # Mise à jour des stats du joueur
        player_stats = stats["player_stats"].get(player_name)
        if player_stats:
            player_stats["games_played"] += 1
            player_stats["total_kills"] += participant.get("kills", 0)
            player_stats["total_deaths"] += participant.get("deaths", 0)
            player_stats["total_assists"] += participant.get("assists", 0)
            player_stats["total_vision_score"] += participant.get("visionScore", 0)
            player_stats["total_game_duration"] += duration_seconds
            player_stats["total_cs"] += cs
            if participant.get("win"):
                player_stats["wins"] += 1
            if champion_name not in player_stats["champions_played"]:
                player_stats["champions_played"].append(champion_name)

        # Stats des champions
        if champion_name not in stats["champion_stats"]["picks"]:
            stats["champion_stats"]["picks"][champion_name] = 0
            stats["champion_stats"]["wins"][champion_name] = 0
        
        stats["champion_stats"]["picks"][champion_name] += 1
        if participant.get("win"):
            stats["champion_stats"]["wins"][champion_name] += 1

        # Vision score
        vision_score = participant.get("visionScore", 0)
        if vision_score > stats["highest_vision_game"]["value"]:
            stats["highest_vision_game"].update({
                "detail": match_id,
                "value": vision_score,
                "player": player_name,
                "team": team_name,
                "champion": champion_name
            })

        # CS per minute
        if cs_per_min > stats["highest_cs_per_min"]["value"]:
            stats["highest_cs_per_min"].update({
                "detail": match_id,
                "value": cs_per_min,
                "player": player_name,
                "team": team_name,
                "champion": champion_name
            })

        total_kills += participant.get("kills", 0)

    # Stats des kills par game
    if total_kills > stats["most_kills_in_game"]["value"]:
        stats["most_kills_in_game"].update({
            "detail": match_id,
            "value": total_kills,
            "teams": match_teams
        })
    if total_kills < stats["least_kills_in_game"]["value"]:
        stats["least_kills_in_game"].update({
            "detail": match_id,
            "value": total_kills,
            "teams": match_teams
        })

    # Bans
    for team in teams:
        for ban in team.get("bans", []):
            champion_id = ban.get("championId")
            if champion_id in champ_id_to_name:
                champion_name = format_champion_name(champ_id_to_name[champion_id])
                if champion_name not in stats["champion_stats"]["bans"]:
                    stats["champion_stats"]["bans"][champion_name] = 0
                stats["champion_stats"]["bans"][champion_name] += 1

def get_player_records(team_stats: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Trouve les joueurs avec les meilleures statistiques"""
    stats_to_check = [
        "total_kills",
        "total_deaths",
        "total_assists",
        "average_kills",
        "average_deaths",
        "average_assists",
        "average_kda",
        "average_cs_per_minute",
        "unique_champions_played",
        "average_vision_score"
    ]
    
    results = {}
    for stat_key in stats_to_check:
        max_value = float('-inf')
        best_player = None
        best_team = None

        # Parcourir toutes les équipes et leurs joueurs
        for team_name, team_data in team_stats.items():
            for player_name, player_stats in team_data.get("players", {}).items():
                if stat_key in player_stats:
                    value = player_stats[stat_key]
                    if value > max_value:
                        max_value = value
                        best_player = player_name
                        best_team = team_name

        # Ajouter le résultat pour cette statistique
        results[stat_key] = {
            "team": best_team,
            "player": best_player,
            "value": round(max_value, 1) if max_value != float('-inf') else 0
        }

    return results

def calculate_player_averages(stats: Dict[str, Any]) -> None:
    """Calcule les moyennes pour tous les joueurs"""
    for player_stats in stats["player_stats"].values():
        games = player_stats["games_played"]
        if games > 0:
            minutes_played = player_stats["total_game_duration"] / 60
            
            player_stats.update({
                "average_kills": round(player_stats["total_kills"] / games, 2),
                "average_deaths": round(player_stats["total_deaths"] / games, 2),
                "average_assists": round(player_stats["total_assists"] / games, 2),
                "average_vision_score": round(player_stats["total_vision_score"] / games, 2),
                "average_cs_per_minute": round(player_stats["total_cs"] / minutes_played, 2),
                "winrate": round((player_stats["wins"] / games) * 100, 2),
                "average_kda": round((player_stats["total_kills"] + player_stats["total_assists"]) / 
                                   max(1, player_stats["total_deaths"]), 2),
                "unique_champions_played": len(player_stats["champions_played"])
            })

def get_stats(match_details: Dict[str, Any], teams_data: Dict[str, Any], 
              champ_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule toutes les statistiques du tournoi"""
    global champ_id_to_name
    champ_id_to_name = {int(champ_data["data"][champ]["key"]): champ for champ in champ_data["data"]}
    
    # Initialisation des statistiques
    stats = initialize_stats()
    
    # Initialisation des stats des joueurs
    for team_name, players in teams_data.items():
        for player in players:
            player_name = player.get("riotIdGameName", "Unknown")
            stats["player_stats"][player_name] = initialize_player_stats(team_name)

    # Traitement des matchs
    for match_id, match_data in match_details.items():
        try:
            update_match_stats(stats, match_id, match_data, teams_data, champ_data)
        except Exception as e:
            print(f"Erreur lors du traitement du match {match_id}: {e}")
            continue

    # Calcul des moyennes
    calculate_player_averages(stats)
    
    # Charger team_stats.json pour les records
    current_dir = os.path.dirname(__file__)
    team_stats_path = os.path.join(current_dir, "../data/team_stats.json")
    
    with open(team_stats_path, "r", encoding="utf-8") as f:
        team_stats = json.load(f)
    
    # Calcul des records à partir de team_stats.json
    stats["records"] = get_player_records(team_stats)

    # Stats finales des champions
    champion_stats = stats["champion_stats"]
    most_picked = max(champion_stats["picks"].items(), key=lambda x: x[1])
    most_banned = max(champion_stats["bans"].items(), key=lambda x: x[1]) if champion_stats["bans"] else ("Aucun", 0)
    
    stats.update({
        "most_picked_champion": {"detail": most_picked[0], "value": most_picked[1]},
        "most_banned_champion": {"detail": most_banned[0], "value": most_banned[1]}
    })

    # Formater les durées pour l'affichage final
    stats["longest_game"]["display_value"] = format_duration(stats["longest_game"]["value"])
    stats["shortest_game"]["display_value"] = format_duration(stats["shortest_game"]["value"])

    return stats

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "../data")
    
    try:
        print("Chargement des données...")
        with open(os.path.join(data_dir, "match_details.json"), "r", encoding="utf-8") as f:
            match_details = json.load(f)
        
        with open(os.path.join(data_dir, "teams_with_puuid.json"), "r", encoding="utf-8") as f:
            teams_data = json.load(f)
        
        with open(os.path.join(data_dir, "champData.json"), "r", encoding="utf-8") as f:
            champ_data = json.load(f)

        print("Calcul des statistiques...")
        stats = get_stats(match_details, teams_data, champ_data)

        output_path = os.path.join(data_dir, "general_stats.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
        
        print(f"Les statistiques ont été enregistrées dans {output_path}")
        
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")