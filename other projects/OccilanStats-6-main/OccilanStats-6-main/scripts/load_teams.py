import openpyxl
import json
import os

# Définition de l'ordre des rôles
ROLE_ORDER = {
    "TOP": 0,
    "JUNGLE": 1,
    "MID": 2,
    "ADC": 3,
    "SUPPORT": 4
}

def sort_players_by_role(players):
    """Trie les joueurs par rôle selon l'ordre défini"""
    return sorted(players, key=lambda x: ROLE_ORDER.get(x['role'].upper(), 999))

def load_teams_from_excel(file_path):
    """
    Charge les équipes depuis un fichier Excel.
    
    Args:
        file_path (str): Chemin du fichier Excel.
    
    Returns:
        dict: Un dictionnaire contenant les équipes et leurs joueurs triés par rôle.
    """
    try:
        # Utiliser un chemin absolu
        absolute_path = os.path.abspath(file_path)
        if not os.path.exists(absolute_path):
            print(f"Erreur : Le fichier {absolute_path} est introuvable.")
            return {}

        # Charger le fichier Excel
        wb = openpyxl.load_workbook(absolute_path)
        sheet = wb.active  # Utiliser la première feuille

        teams = {}
        for row in sheet.iter_rows(min_row=2, max_col=4, values_only=True):
            team_name, role, player_name, player_tag = row

            # Vérifier que les données nécessaires sont présentes
            if not all([team_name, role, player_name, player_tag]):
                print(f"Ligne ignorée : données manquantes ({row})")
                continue

            if team_name not in teams:
                teams[team_name] = []

            teams[team_name].append({
                "role": role.title(),  # Première lettre en majuscule
                "player_name": player_name.strip(),
                "player_tag": str(player_tag).strip()
            })

        # Trier les joueurs par rôle pour chaque équipe
        for team_name in teams:
            teams[team_name] = sort_players_by_role(teams[team_name])

        return teams

    except FileNotFoundError:
        print(f"Erreur : Le fichier {file_path} est introuvable.")
        return {}
    except Exception as e:
        print(f"Erreur inattendue lors du chargement du fichier Excel : {e}")
        return {}

def save_teams_to_json(teams, output_path):
    """Sauvegarde les équipes dans un fichier JSON"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(teams, f, indent=4, ensure_ascii=False)
        print(f"Les données ont été sauvegardées dans {output_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier JSON : {e}")

if __name__ == "__main__":
    # Chemins des fichiers
    current_dir = os.path.dirname(__file__)
    excel_path = os.path.join(current_dir, "..", "data", "pseudosOccilan#6.xlsx")
    json_path = os.path.join(current_dir, "..", "data", "teams.json")
    
    print("Chargement des équipes depuis le fichier Excel...")
    print(f"Fichier Excel : {os.path.abspath(excel_path)}")
    print(f"Destination JSON : {os.path.abspath(json_path)}")
    
    # Charger et traiter les données
    teams = load_teams_from_excel(excel_path)
    if teams:
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        # Sauvegarder en JSON
        save_teams_to_json(teams, json_path)
        
        # Afficher un résumé
        print("\nRésumé des équipes chargées :")
        for team_name, players in teams.items():
            print(f"\nÉquipe {team_name} :")
            for player in players:
                print(f"  - {player['role']} : {player['player_name']}#{player['player_tag']}")
    else:
        print("Aucune équipe n'a été chargée.")