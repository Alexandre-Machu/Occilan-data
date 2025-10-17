"""
Test rapide avec un joueur EUW réel pour valider l'API.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter src/ au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.riot_client import RiotAPIClient

# Charger .env
load_dotenv()

# Initialiser client
client = RiotAPIClient(os.getenv("RIOT_API_KEY"))

import logging
logging.basicConfig(level=logging.DEBUG)

print("\n" + "="*70)
print("TEST RÉEL : Fetch info joueur EUW")
print("="*70)

# Test avec un vrai compte EUW
test_players = [
    ("Colfeo", "LRC"),
]

for game_name, tag_line in test_players:
    print(f"\nRecherche: {game_name}#{tag_line}")
    print("-" * 70)
    
    try:
        player = client.get_player_full_info(game_name, tag_line)
        
        if player:
            print(f"[OK] Joueur trouve!")
            print(f"   Riot ID: {player['game_name']}#{player['tag_line']}")
            print(f"   Summoner: {player['summoner_name']}")
            print(f"   Niveau: {player['summoner_level']}")
            print(f"   PUUID: {player['puuid'][:20]}...")
            
            if player.get('ranked'):
                r = player['ranked']
                print(f"   Rank SoloQ: {r['tier']} {r['rank']} ({r['lp']} LP)")
                winrate = r['wins'] / (r['wins'] + r['losses']) * 100
                print(f"   Winrate: {r['wins']}W {r['losses']}L ({winrate:.1f}%)")
            else:
                print(f"   Rank: Unranked")
            
            # Test match IDs
            print(f"\n   Recherche des custom games recents...")
            from datetime import datetime, timedelta
            
            end = datetime.now()
            start = end - timedelta(days=30)
            
            match_ids = client.get_match_ids_by_puuid(
                player['puuid'],
                start_time=int(start.timestamp()),
                end_time=int(end.timestamp()),
                queue_id=0,  # Custom games
                count=5
            )
            
            if match_ids:
                print(f"   [OK] {len(match_ids)} custom game(s) trouve(s)")
                for i, match_id in enumerate(match_ids[:3], 1):
                    print(f"      {i}. {match_id}")
            else:
                print(f"   [INFO] Aucun custom game trouve (normal)")
            
            break  # On s'arrête au premier joueur trouvé
        else:
            print(f"[WARNING] Joueur non trouve")
    
    except Exception as e:
        import traceback
        print(f"[ERREUR] {e}")
        traceback.print_exc()

print("\n" + "="*70)
print("Test terminé !")
print("="*70 + "\n")
