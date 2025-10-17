import json
import os

def calculate_kda(kills, deaths, assists):
    """
    Calcule le KDA d'un joueur.
    """
    return (kills + assists) / deaths if deaths > 0 else "PERFECT"

def format_champion_name(champion_name):
    """
    Formate le nom du champion (cas spéciaux).
    """
    return "Wukong" if champion_name == "MonkeyKing" else champion_name

def analyze_match_stats(match_details, teams):
    """
    Analyse les statistiques des matchs et les organise par équipe et par joueur.
    """
    team_stats = {}
    team_match_ids = {}  # Pour suivre les matchs de chaque équipe

    # Initialiser les stats pour chaque équipe
    for team_name in teams.keys():
        team_stats[team_name] = {
            "team_stats": {
                "total_games": 0,
                "wins": 0,
                "losses": 0,
                "winrate": 0,
                "average_game_duration": 0,
                "shortest_game": float("inf"),
                "longest_game": 0,
                "total_game_duration": 0
            },
            "players": {}
        }
        team_match_ids[team_name] = set()

    # Traiter chaque match
    for match_id, match_data in match_details.items():
        try:
            participants = match_data["info"].get("participants", [])
            game_duration_minutes = match_data["info"].get("gameDuration", 0) / 60

            # Pour chaque joueur dans le match
            for participant in participants:
                participant_puuid = participant.get("puuid")
                if not participant_puuid:
                    continue

                # Trouver l'équipe du joueur
                for team_name, team_players in teams.items():
                    for player in team_players:
                        if player.get("puuid") == participant_puuid:
                            player_name = player.get("player_name")
                            if not player_name:
                                continue

                            # Mettre à jour les stats d'équipe (une seule fois par match)
                            if match_id not in team_match_ids[team_name]:
                                team_match_ids[team_name].add(match_id)
                                team_stats[team_name]["team_stats"]["total_games"] += 1
                                
                                if participant["win"]:
                                    team_stats[team_name]["team_stats"]["wins"] += 1
                                
                                team_stats[team_name]["team_stats"]["total_game_duration"] += game_duration_minutes
                                team_stats[team_name]["team_stats"]["shortest_game"] = min(
                                    team_stats[team_name]["team_stats"]["shortest_game"],
                                    game_duration_minutes
                                )
                                team_stats[team_name]["team_stats"]["longest_game"] = max(
                                    team_stats[team_name]["team_stats"]["longest_game"],
                                    game_duration_minutes
                                )

                            # Initialiser les stats du joueur si nécessaire
                            if player_name not in team_stats[team_name]["players"]:
                                team_stats[team_name]["players"][player_name] = {
                                    "total_kills": 0,
                                    "total_deaths": 0,
                                    "total_assists": 0,
                                    "total_cs": 0,
                                    "total_vision_score": 0,
                                    "champions_played": set()
                                }

                            # Mettre à jour les stats du joueur
                            player_stats = team_stats[team_name]["players"][player_name]
                            player_stats["total_kills"] += participant["kills"]
                            player_stats["total_deaths"] += participant["deaths"]
                            player_stats["total_assists"] += participant["assists"]
                            player_stats["total_cs"] += participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
                            player_stats["total_vision_score"] += participant["visionScore"]
                            champion_name = format_champion_name(participant["championName"])
                            player_stats["champions_played"].add(champion_name)

        except Exception as e:
            print(f"Erreur lors du traitement du match {match_id}: {e}")
            continue

    # Calculer les statistiques finales
    for team_name, data in team_stats.items():
        team_data = data["team_stats"]
        total_games = team_data["total_games"]

        if total_games > 0:
            # Calculer les stats d'équipe
            team_data["losses"] = total_games - team_data["wins"]
            team_data["winrate"] = round((team_data["wins"] / total_games) * 100, 1)
            team_data["average_game_duration"] = round(team_data["total_game_duration"] / total_games, 1)
            team_data["shortest_game"] = round(team_data["shortest_game"], 1)
            team_data["longest_game"] = round(team_data["longest_game"], 1)

            # Calculer les moyennes pour chaque joueur
            for player_name, player_stats in data["players"].items():
                if player_stats["total_deaths"] > 0:
                    player_stats["average_kda"] = calculate_kda(
                        player_stats["total_kills"],
                        player_stats["total_deaths"],
                        player_stats["total_assists"]
                    )
                else:
                    player_stats["average_kda"] = "PERFECT"

                player_stats["average_kills"] = round(player_stats["total_kills"] / total_games, 1)
                player_stats["average_deaths"] = round(player_stats["total_deaths"] / total_games, 1)
                player_stats["average_assists"] = round(player_stats["total_assists"] / total_games, 1)
                player_stats["average_cs_per_game"] = round(player_stats["total_cs"] / total_games, 1)
                player_stats["average_vision_score"] = round(player_stats["total_vision_score"] / total_games, 1)
                player_stats["average_cs_per_minute"] = round(player_stats["total_cs"] / team_data["total_game_duration"], 1)
                player_stats["unique_champions_played"] = len(player_stats["champions_played"])
                player_stats["champions_played"] = list(player_stats["champions_played"])

        # Afficher un résumé des stats pour vérification
        print(f"\nÉquipe : {team_name}")
        print(f"Nombre de parties : {total_games}")
        print(f"Victoires : {team_data['wins']}")
        print(f"Défaites : {team_data['losses']}")
        print(f"Nombre de joueurs : {len(data['players'])}")

    return team_stats

def save_team_stats_to_json(team_stats, output_path):
    """
    Enregistre les statistiques des équipes dans un fichier JSON.
    """
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(team_stats, json_file, indent=4, ensure_ascii=False)
        print(f"Les statistiques des équipes ont été enregistrées dans {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "../data")
    match_details_path = os.path.join(data_dir, "match_details.json")
    teams_with_puuid_path = os.path.join(data_dir, "teams_with_puuid.json")
    team_stats_output_path = os.path.join(data_dir, "team_stats.json")

    with open(match_details_path, "r", encoding="utf-8") as json_file:
        match_details = json.load(json_file)

    with open(teams_with_puuid_path, "r", encoding="utf-8") as json_file:
        teams = json.load(json_file)

    team_stats = analyze_match_stats(match_details, teams)
    save_team_stats_to_json(team_stats, team_stats_output_path)