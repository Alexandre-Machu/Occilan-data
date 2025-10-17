"""
Test workflow complet: Parse OP.GG → Fetch données → Sauvegarder JSON

Ce script démontre le pipeline complet end-to-end.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Ajouter src/ au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parsers.opgg_parser import OPGGParser
from core.riot_client import RiotAPIClient
from core.data_manager import EditionDataManager

# Charger .env
load_dotenv()

print("\n" + "="*70)
print("WORKFLOW COMPLET: CSV → OP.GG → Riot API → JSON")
print("="*70)

# 1. Simuler un CSV avec un lien OP.GG réel
print("\n[1/6] Parse lien OP.GG...")
opgg_link = "https://www.op.gg/multisearch/euw?summoners=Colfeo-LRC,TestPlayer-EUW"

try:
    # Parse le lien (va extraire Colfeo#LRC)
    riot_ids = OPGGParser.parse_multisearch_url(opgg_link)
    print(f"   [OK] {len(riot_ids)} joueurs extraits:")
    for game_name, tag_line in riot_ids:
        print(f"      - {game_name}#{tag_line}")
except Exception as e:
    print(f"   [ERREUR] {e}")
    sys.exit(1)

# 2. Créer une édition test
print("\n[2/6] Initialiser édition 999 (test)...")
manager = EditionDataManager(999)

try:
    manager.initialize_edition(
        edition_name="Test Workflow",
        year=2025,
        start_date="2025-10-01",
        end_date="2025-10-31"
    )
    print("   [OK] Edition initialisee")
except Exception as e:
    print(f"   [INFO] Edition deja existante (normal)")

# 3. Ajouter équipe avec OP.GG link
print("\n[3/6] Sauvegarder equipe...")
team_data = {
    "players": [
        {"role": "TOP", "game_name": riot_ids[0][0], "tag_line": riot_ids[0][1]}
    ] if len(riot_ids) >= 1 else [],
    "opgg_link": opgg_link
}

manager.add_team("TestTeam", team_data)
print("   [OK] Equipe 'TestTeam' sauvegardee")

# 4. Fetch PUUID + Rank
print("\n[4/6] Fetch donnees Riot API...")
client = RiotAPIClient(os.getenv("RIOT_API_KEY"))

teams_with_puuid = {}
for team_name, data in manager.load_teams().items():
    enriched_players = []
    
    for player in data["players"]:
        print(f"   Fetching {player['game_name']}#{player['tag_line']}...")
        
        try:
            info = client.get_player_full_info(
                player["game_name"],
                player["tag_line"]
            )
            
            if info:
                enriched_players.append({
                    **player,
                    "puuid": info["puuid"],
                    "summoner_name": info["summoner_name"],
                    "summoner_level": info["summoner_level"],
                    "profile_icon_id": info.get("profile_icon_id"),
                    **(info.get("ranked") or {})
                })
                
                rank_info = ""
                if info.get("ranked"):
                    r = info["ranked"]
                    rank_info = f" - {r['tier']} {r['rank']} ({r['lp']} LP)"
                
                print(f"      [OK] Level {info['summoner_level']}{rank_info}")
            else:
                print(f"      [WARNING] Joueur non trouve")
        except Exception as e:
            print(f"      [ERREUR] {e}")
            enriched_players.append(player)  # Garder sans enrichissement
    
    teams_with_puuid[team_name] = {"players": enriched_players}

# 5. Sauvegarder données enrichies
print("\n[5/6] Sauvegarder donnees enrichies...")
manager.save_teams_with_puuid(teams_with_puuid)
print("   [OK] teams_with_puuid.json sauvegarde")

# 6. Afficher résumé
print("\n[6/6] Resume de l'edition...")
summary = manager.get_summary()
print(f"   Edition: {summary['edition_name']}")
print(f"   Status: {summary['status']}")
print(f"   Equipes: {summary['teams_count']}")
print(f"   Joueurs: {summary['players_count']}")

# Afficher le chemin des fichiers créés
print(f"\n[INFO] Fichiers crees dans:")
print(f"   {manager.edition_path}")
print(f"   - config.json")
print(f"   - teams.json")
print(f"   - teams_with_puuid.json")

print("\n" + "="*70)
print("WORKFLOW COMPLET TERMINE!")
print("="*70)
print("\nPour nettoyer:")
print(f"   import shutil")
print(f"   shutil.rmtree('{manager.edition_path}')")
print()
