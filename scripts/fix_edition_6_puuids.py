"""
Script pour corriger les PUUIDs de l'édition 6 en utilisant les vrais PUUIDs des match_details
"""

import json
from pathlib import Path
from collections import defaultdict

EDITION_DIR = Path(__file__).parent.parent / "data" / "editions" / "edition_6"

print("🔍 Extraction des PUUIDs réels depuis match_details.json...")

# Charger les match details
with open(EDITION_DIR / "match_details.json", "r", encoding="utf-8") as f:
    match_details = json.load(f)

# Extraire tous les PUUIDs uniques avec leurs noms
player_puuids = {}  # {(gameName, tagLine): puuid}

for match_id, match_data in match_details.items():
    participants = match_data.get("info", {}).get("participants", [])
    
    for participant in participants:
        game_name = participant.get("riotIdGameName", "")
        tag_line = participant.get("riotIdTagline", "")
        puuid = participant.get("puuid", "")
        
        if game_name and tag_line and puuid:
            key = (game_name, tag_line)
            if key not in player_puuids:
                player_puuids[key] = puuid

print(f"✅ {len(player_puuids)} PUUIDs uniques trouvés")

# Charger teams_with_puuid
with open(EDITION_DIR / "teams_with_puuid.json", "r", encoding="utf-8") as f:
    teams_with_puuid = json.load(f)

# Mettre à jour les PUUIDs
updated_count = 0
not_found = []

for team_name, team_data in teams_with_puuid.items():
    for player in team_data["players"]:
        key = (player["gameName"], player["tagLine"])
        
        if key in player_puuids:
            player["puuid"] = player_puuids[key]
            updated_count += 1
        else:
            not_found.append(f"{player['gameName']}#{player['tagLine']}")
            # Garder le PUUID legacy si on ne trouve pas le vrai

# Sauvegarder
with open(EDITION_DIR / "teams_with_puuid.json", "w", encoding="utf-8") as f:
    json.dump(teams_with_puuid, f, indent=2, ensure_ascii=False)

print(f"✅ {updated_count} PUUIDs mis à jour")

if not_found:
    print(f"\n⚠️  {len(not_found)} joueurs non trouvés dans les matchs:")
    for player in not_found[:10]:  # Afficher seulement les 10 premiers
        print(f"   - {player}")

print("\n✅ Fichier teams_with_puuid.json mis à jour!")
