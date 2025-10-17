import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = "https://europe.api.riotgames.com"

def fetch_match_details(match_ids):
    """
    Récupère les détails des matchs pour une liste de match IDs.
    """
    match_details = {}

    for match_id in match_ids:
        print(f"Récupération des détails pour le match : {match_id}")

        # Construire l'URL pour récupérer les détails du match
        endpoint = f"/lol/match/v5/matches/{match_id}"
        api_url = f"{base_url}{endpoint}?api_key={api_key}"

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                match_details[match_id] = response.json()
                print(f"Détails récupérés pour le match : {match_id}")
            else:
                print(f"Erreur pour le match {match_id}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête pour le match {match_id}: {e}")

    return match_details

def save_match_details_to_json(match_details, output_path):
    """
    Enregistre les détails des matchs dans un fichier JSON.
    """
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(match_details, json_file, indent=4, ensure_ascii=False)
        print(f"Les détails des matchs ont été enregistrés dans {output_path}")

if __name__ == "__main__":
    # Définir les chemins des fichiers
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "../data")
    matches_json_path = os.path.join(data_dir, "tournament_matches.json")
    match_details_output_path = os.path.join(data_dir, "match_details.json")

    # Charger les match IDs depuis le fichier JSON
    print("Chargement des matchs depuis le fichier JSON...")
    with open(matches_json_path, "r", encoding="utf-8") as json_file:
        tournament_matches = json.load(json_file)

    # Récupérer tous les match IDs uniques
    print("Extraction des match IDs uniques...")
    all_match_ids = set()
    for team_matches in tournament_matches.values():
        all_match_ids.update(team_matches)

    print(f"{len(all_match_ids)} match IDs uniques trouvés.\n")

    # Récupérer les détails des matchs
    print("Récupération des détails des matchs...")
    match_details = fetch_match_details(all_match_ids)

    # Enregistrer les détails des matchs dans un fichier JSON
    print("Enregistrement des détails des matchs dans un fichier JSON...")
    save_match_details_to_json(match_details, match_details_output_path)
    print("Processus terminé avec succès.")