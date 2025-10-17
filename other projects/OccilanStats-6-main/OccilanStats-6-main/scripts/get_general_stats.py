import json
import os

def get_general_stats(team_stats):
    """
    Trouve les joueurs avec les meilleures statistiques.
    
    Args:
        team_stats (dict): Les statistiques des équipes et des joueurs.
    
    Returns:
        dict: Un dictionnaire contenant les meilleurs joueurs pour chaque statistique.
    """
    # Liste des statistiques à analyser
    stat_keys = [
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

    for stat_key in stat_keys:
        max_value = float('-inf')  # Initialiser avec une valeur très basse
        best_player = None
        best_team = None

        # Parcourir toutes les équipes et joueurs
        for team_name, players in team_stats.items():
            for player_name, stats in players.items():
                if stat_key in stats:  # Vérifier si la statistique existe pour ce joueur
                    if stats[stat_key] > max_value:
                        max_value = stats[stat_key]
                        best_player = player_name
                        best_team = team_name

        # Ajouter le résultat pour cette statistique
        results[stat_key] = {
            "team": best_team,
            "player": best_player,
            "value": round(max_value, 1)  # Arrondir à 1 chiffre après la virgule
        }

    return results

def save_results_to_json(results, output_path):
    """
    Enregistre les résultats dans un fichier JSON.
    """
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(results, output_file, indent=4, ensure_ascii=False)
        print(f"Les résultats ont été enregistrés dans {output_path}.")

if __name__ == "__main__":
    # Définir les chemins des fichiers
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "../data")
    team_stats_path = os.path.join(data_dir, "team_stats.json")
    general_stats_output_path = os.path.join(data_dir, "general_stats.json")

    # Charger les données de team_stats.json
    print("Chargement des statistiques des équipes depuis le fichier JSON...")
    with open(team_stats_path, "r", encoding="utf-8") as file:
        team_stats = json.load(file)

    # Obtenir les meilleurs joueurs pour chaque statistique
    print("Analyse des statistiques pour trouver les meilleurs joueurs...")
    results = get_general_stats(team_stats)

    # Afficher les résultats formatés
    print("\nRésultats :")
    for stat, result in results.items():
        print(f"Le joueur avec le plus de {stat} est {result['player']} de l'équipe {result['team']} avec {result['value']}.")

    # Enregistrer les résultats dans un fichier JSON
    print("\nEnregistrement des résultats dans un fichier JSON...")
    save_results_to_json(results, general_stats_output_path)
    print("Processus terminé avec succès.")