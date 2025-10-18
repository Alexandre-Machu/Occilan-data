"""
Script de migration de l'édition 6 depuis OccilanStats-6-main
Convertit les données de l'ancien format vers le nouveau format
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Chemins
OLD_DATA_DIR = Path(__file__).parent.parent / "other projects" / "OccilanStats-6-main" / "OccilanStats-6-main" / "data"
NEW_EDITION_DIR = Path(__file__).parent.parent / "data" / "editions" / "edition_6"

print("🔄 Migration de l'édition 6...")
print(f"Source: {OLD_DATA_DIR}")
print(f"Destination: {NEW_EDITION_DIR}")

# Créer le dossier de destination
NEW_EDITION_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 1. Créer config.json
# ============================================================================

config = {
    "edition_id": 6,
    "name": "Occi'lan #6",
    "start_date": "2025-04-25",
    "end_date": "2025-04-27",
    "location": "Toulouse, France",
    "is_private": False,
    "created_at": datetime.now().isoformat(),
    "description": "Édition 6 de l'Occi'lan - Migré depuis OccilanStats-6"
}

with open(NEW_EDITION_DIR / "config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ config.json créé")

# ============================================================================
# 2. Convertir teams.json (ancien format → nouveau format)
# ============================================================================

with open(OLD_DATA_DIR / "teams.json", "r", encoding="utf-8") as f:
    old_teams = json.load(f)

new_teams = {}

# Mapping des rôles
ROLE_MAPPING = {
    "Top": "TOP",
    "Jungle": "JGL",
    "Mid": "MID",
    "Adc": "ADC",
    "Support": "SUP"
}

for team_name, players_list in old_teams.items():
    # Construire le lien OP.GG
    summoners = []
    for player in players_list:
        summoners.append(f"{player['player_name']}%23{player['player_tag']}")
    
    opgg_link = f"https://op.gg/fr/lol/multisearch/euw?summoners={','.join(summoners)}"
    
    # Convertir les joueurs
    new_players = []
    for player in players_list:
        new_players.append({
            "role": ROLE_MAPPING.get(player["role"], player["role"]),
            "gameName": player["player_name"],
            "tagLine": player["player_tag"]
        })
    
    new_teams[team_name] = {
        "name": team_name,
        "opgg_link": opgg_link,
        "players": new_players
    }

with open(NEW_EDITION_DIR / "teams.json", "w", encoding="utf-8") as f:
    json.dump(new_teams, f, indent=2, ensure_ascii=False)

print(f"✅ teams.json converti ({len(new_teams)} équipes)")

# ============================================================================
# 3. Copier tournament_matches.json (format déjà compatible)
# ============================================================================

if (OLD_DATA_DIR / "tournament_matches.json").exists():
    shutil.copy(
        OLD_DATA_DIR / "tournament_matches.json",
        NEW_EDITION_DIR / "tournament_matches.json"
    )
    print("✅ tournament_matches.json copié")

# ============================================================================
# 4. Copier match_details.json (format déjà compatible)
# ============================================================================

if (OLD_DATA_DIR / "match_details.json").exists():
    shutil.copy(
        OLD_DATA_DIR / "match_details.json",
        NEW_EDITION_DIR / "match_details.json"
    )
    
    # Compter les matchs
    with open(OLD_DATA_DIR / "match_details.json", "r", encoding="utf-8") as f:
        match_details = json.load(f)
    
    print(f"✅ match_details.json copié ({len(match_details)} matchs)")

# ============================================================================
# 5. Créer teams_with_puuid.json avec PUUIDs fictifs
# ============================================================================

# L'ancien format n'a pas de PUUID, on crée une structure minimale
# pour que les stats puissent être calculées
teams_with_puuid = {}
for team_name, team_data in new_teams.items():
    teams_with_puuid[team_name] = {
        "name": team_name,
        "opgg_link": team_data["opgg_link"],
        "players": []
    }
    
    for player in team_data["players"]:
        # Créer un PUUID fictif mais unique basé sur le nom du joueur
        fake_puuid = f"LEGACY_{team_name}_{player['gameName']}_{player['tagLine']}"
        
        teams_with_puuid[team_name]["players"].append({
            "role": player["role"],
            "gameName": player["gameName"],
            "tagLine": player["tagLine"],
            "puuid": fake_puuid,
            "rank": "N/A",  # Rang non disponible pour l'édition 6
            "tier": "UNRANKED",
            "division": "",
            "lp": 0
        })

with open(NEW_EDITION_DIR / "teams_with_puuid.json", "w", encoding="utf-8") as f:
    json.dump(teams_with_puuid, f, indent=2, ensure_ascii=False)

print("✅ teams_with_puuid.json créé (avec PUUIDs legacy)")

# ============================================================================
# 6. Copier general_stats.json (statistiques déjà calculées)
# ============================================================================

if (OLD_DATA_DIR / "general_stats.json").exists():
    shutil.copy(
        OLD_DATA_DIR / "general_stats.json",
        NEW_EDITION_DIR / "general_stats.json"
    )
    print("✅ general_stats.json copié (stats historiques)")

print("\n📊 Résumé de la migration:")
print(f"  - Edition: {config['name']}")
print(f"  - Équipes: {len(new_teams)}")
print(f"  - Dates: {config['start_date']} → {config['end_date']}")
print(f"\n✅ Données historiques préservées:")
print(f"  - Statistiques générales copiées depuis l'édition originale")
print(f"  - Les PUUIDs sont en mode 'legacy' (non mis à jour)")
print(f"  - Les rangs sont marqués comme N/A (édition passée)")
print("\n✅ Migration terminée!")
