import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = "https://europe.api.riotgames.com"

def fetch_tournament_matches(teams, start_date, end_date, count=50, match_type="tourney"):
    """
    Récupère les matchs de type tournoi pour le premier joueur de chaque équipe.
    
    Args:
        teams (dict): Dictionnaire des équipes avec leurs joueurs et PUUIDs
        start_date (datetime): Date de début pour la recherche des matchs
        end_date (datetime): Date de fin pour la recherche des matchs
        count (int, optional): Nombre maximum de matchs à récupérer. Defaults to 50.
        match_type (str, optional): Type de match à récupérer. Defaults to "tourney".

    Returns:
        dict: Dictionnaire des matchs par équipe
    """
    start_time = int(time.mktime(start_date.timetuple()))
    end_time = int(time.mktime(end_date.timetuple()))

    all_matches = {}
    matches_to_ignore = ["EUW1_7381728303"]  # Liste des matchs à ignorer

    for team_name, players in teams.items():
        print(f"\nRécupération des matchs pour l'équipe : {team_name}")
        
        # Prendre uniquement le premier joueur de l'équipe
        player = players[0]
        puuid = player.get("puuid")
        
        if not puuid:
            print(f"Pas de puuid pour le joueur {player.get('player_name')}, passage à l'équipe suivante.")
            continue

        # Construire l'URL pour récupérer les IDs des matchs
        endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        api_url = f"{base_url}{endpoint}?count={count}&type={match_type}&startTime={start_time}&endTime={end_time}&api_key={api_key}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                match_ids = response.json()
                
                # Filtrer les matchs à ignorer
                filtered_match_ids = [
                    match_id for match_id in match_ids 
                    if match_id not in matches_to_ignore
                ]
                
                if filtered_match_ids:
                    print(f"Matchs récupérés via {player.get('player_name')}: {filtered_match_ids}")
                    all_matches[team_name] = filtered_match_ids
                
                # Afficher les matchs ignorés
                ignored_matches = set(match_ids) - set(filtered_match_ids)
                if ignored_matches:
                    print(f"Matchs ignorés : {ignored_matches}")
            else:
                print(f"Erreur pour {player.get('player_name')}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête pour {player.get('player_name')}: {e}")

        if team_name in all_matches:
            print(f"Total des matchs pour {team_name}: {len(all_matches[team_name])}")

    return all_matches

def save_matches_to_json(matches, output_path):
    """
    Enregistre les matchs dans un fichier JSON.

    Args:
        matches (dict): Dictionnaire des matchs à sauvegarder
        output_path (str): Chemin du fichier de sortie
    """
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(matches, json_file, indent=4, ensure_ascii=False)
        print(f"Les matchs ont été enregistrés dans {output_path}")

if __name__ == "__main__":
    # Définir les chemins des fichiers
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "../data")
    teams_with_puuid_json_path = os.path.join(data_dir, "teams_with_puuid.json")
    matches_output_path = os.path.join(data_dir, "tournament_matches.json")

    # Charger les équipes depuis le fichier JSON
    print("Chargement des équipes depuis le fichier JSON...")
    with open(teams_with_puuid_json_path, "r", encoding="utf-8") as json_file:
        teams = json.load(json_file)

    # Définir les dates pour récupérer les matchs
    start_date = datetime(2025, 4, 25)
    end_date = datetime(2025, 4, 27, 23, 59, 59)

    # Récupérer les matchs
    print("Récupération des matchs de type tournoi...")
    tournament_matches = fetch_tournament_matches(teams, start_date, end_date)

    # Enregistrer les matchs dans un fichier JSON
    print("\nEnregistrement des matchs dans un fichier JSON...")
    save_matches_to_json(tournament_matches, matches_output_path)
    print("Processus terminé avec succès.")