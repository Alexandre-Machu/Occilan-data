# Write this in the terminal
# pip install requests python-dotenv openpyxl

# Imports
from dotenv import load_dotenv
from datetime import datetime
from openpyxl.styles import Font, Alignment
import os
import requests
import json
import time
import openpyxl

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    print("La clé API n'a pas été trouvée.")
else:
    # URL de base de l'API Riot
    base_url = "https://europe.api.riotgames.com"

    # Endpoint spécifique pour obtenir les informations du compte
    endpoint = "/riot/account/v1/accounts/by-riot-id/Colfeo/EUW"

    # Construire l'URL complète avec la clé API
    api_url_summoner = f"{base_url}{endpoint}?api_key={api_key}"

    try:
        # Effectuer la requête GET
        response = requests.get(api_url_summoner)

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            player_info = response.json()

            # Afficher les informations du joueur de manière lisible
            print(json.dumps(player_info, indent=4))
            
            # On veut maintenant récupérer les informations de la partie grâce au puuid
            puuid = player_info["puuid"]

            # Calculer les timestamps pour les dates spécifiées
            start_date = datetime(2025, 4, 24)
            end_date = datetime(2025, 4, 27, 23, 59, 59)
            start_time = int(time.mktime(start_date.timetuple()))
            end_time = int(time.mktime(end_date.timetuple()))
            count = int(50)
            type = "tourney"

            # Endpoint pour obtenir les informations de la partie
            endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"

            # Construire l'URL complète avec la clé API et les paramètres de temps
            api_url_match = f"{base_url}{endpoint}?count={count}&type={type}&startTime={start_time}&endTime={end_time}&api_key={api_key}"

            # Effectuer la requête GET
            response = requests.get(api_url_match)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                match_info = response.json()
                # Afficher les informations de la partie de manière lisible
                print(json.dumps(match_info, indent=4))

                # On veut maintenant récupérer les informations de chaque partie, et enregistrer les données dans un fichier JSON
                for match_id in match_info:
                    # Endpoint pour obtenir les détails de la partie
                    endpoint = f"/lol/match/v5/matches/{match_id}"
                    api_url_match_details = f"{base_url}{endpoint}?api_key={api_key}"

                    # Effectuer la requête GET
                    response = requests.get(api_url_match_details)

                    # Vérifier si la requête a réussi
                    if response.status_code == 200:
                        match_details = response.json()
                        # Enregistrer les données dans un fichier JSON
                        with open(f"match_{match_id}.json", "w") as json_file:
                            json.dump(match_details, json_file, indent=4)
                            print(f"Données de la partie {match_id} enregistrées dans match_{match_id}.json")
                            
                    else:
                        print(f"Erreur lors de la requête : {response.status_code}")
                        print("Réponse :", response.text)
            else:
                print(f"Erreur lors de la requête : {response.status_code}")
                print("Réponse :", response.text)
        else:
            print(f"Erreur lors de la requête : {response.status_code}")
            print("Réponse :", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite : {e}")