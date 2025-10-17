import os
from dotenv import load_dotenv
from scripts.load_teams import load_teams_from_excel
from scripts.fetch_puuid import fetch_puuid
from scripts.fetch_matches import fetch_tournament_matches
from scripts.fetch_match_details import fetch_match_details
from scripts.get_stats import get_stats
from scripts.create_excel import create_tournament_sheet
from scripts.save_json import save_to_json
from datetime import datetime
import openpyxl

def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    base_url = "https://europe.api.riotgames.com"

    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "data")
    output_dir = os.path.join(current_dir, "output")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    excel_file_path = os.path.join(data_dir, "pseudosOccilan#6.xlsx")
    teams_json_path = os.path.join(data_dir, "teams.json")
    teams_with_puuid_json_path = os.path.join(data_dir, "teams_with_puuid.json")
    matches_json_path = os.path.join(data_dir, "tournament_matches.json")
    match_details_path = os.path.join(data_dir, "match_details.json")
    general_stats_path = os.path.join(data_dir, "general_stats.json")
    excel_output_path = os.path.join(output_dir, "OccilanStats.xlsx")

    try:
        print("\nÉtape 1: Chargement des équipes...")
        teams = load_teams_from_excel(excel_file_path)
        save_to_json(teams, teams_json_path)

        print("\nÉtape 2: Récupération des PUUIDs...")
        teams_with_puuid = fetch_puuid(teams, api_key, base_url)
        save_to_json(teams_with_puuid, teams_with_puuid_json_path)

        print("\nÉtape 3: Récupération des matchs...")
        tournament_matches = fetch_tournament_matches(teams_with_puuid)
        save_to_json(tournament_matches, matches_json_path)

        print("\nÉtape 4: Récupération des détails des matchs...")
        match_details = fetch_match_details(tournament_matches)
        save_to_json(match_details, match_details_path)

        print("\nÉtape 5: Génération des statistiques...")
        stats = get_stats(match_details, teams_with_puuid)
        save_to_json(stats, general_stats_path)

        print("\nÉtape 6: Création du fichier Excel...")
        wb = openpyxl.Workbook()
        create_tournament_sheet(wb, stats)
        wb.save(excel_output_path)

        print("\nTraitement terminé avec succès!")

    except Exception as e:
        print(f"\nUne erreur s'est produite : {str(e)}")
        raise

if __name__ == "__main__":
    main()