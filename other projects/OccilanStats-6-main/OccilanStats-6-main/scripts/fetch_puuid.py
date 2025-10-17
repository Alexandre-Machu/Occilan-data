import requests
from dotenv import load_dotenv
import os
import json

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = "https://europe.api.riotgames.com"

def fetch_puuid(teams, api_key, base_url):
    """
    Récupère les PUUIDs pour chaque joueur dans les équipes spécifiées.
    """
    for team_name, players in teams.items():
        print(f"Récupération des PUUIDs pour l'équipe : {team_name}")
        for player in players:
            player_name = player.get("player_name")
            player_tag = player.get("player_tag")

            if not player_name or not player_tag:
                print(f"Nom ou tag manquant pour un joueur de l'équipe {team_name}, passage au suivant.")
                continue

            # Endpoint pour récupérer le PUUID
            endpoint = f"/riot/account/v1/accounts/by-riot-id/{player_name}/{player_tag}"
            api_url = f"{base_url}{endpoint}?api_key={api_key}"

            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    player["puuid"] = response.json().get("puuid")
                    print(f"PUUID récupéré pour {player_name}#{player_tag}: {player['puuid']}")
                else:
                    print(f"Erreur pour {player_name}#{player_tag}: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la requête pour {player_name}#{player_tag}: {e}")
    return teams

if __name__ == "__main__":
    # Définir les chemins des fichiers
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "../data")
    teams_json_path = os.path.join(data_dir, "teams.json")
    teams_with_puuid_json_path = os.path.join(data_dir, "teams_with_puuid.json")

    # Charger les équipes depuis le fichier JSON
    print("Chargement des équipes depuis le fichier JSON...")
    with open(teams_json_path, "r", encoding="utf-8") as json_file:
        teams = json.load(json_file)

    # Récupérer les PUUIDs
    print("Récupération des PUUIDs pour chaque joueur...")
    teams_with_puuid = fetch_puuid(teams, api_key, base_url)

    # Enregistrer les équipes avec leurs PUUIDs dans un fichier JSON
    print("Enregistrement des équipes avec leurs PUUIDs dans un fichier JSON...")
    with open(teams_with_puuid_json_path, "w", encoding="utf-8") as json_file:
        json.dump(teams_with_puuid, json_file, indent=4, ensure_ascii=False)
    print(f"Les équipes avec leurs PUUIDs ont été enregistrées dans {teams_with_puuid_json_path}.")