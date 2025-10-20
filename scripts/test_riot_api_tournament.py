"""
Script de test de l'API Riot pour vérifier si on peut récupérer des matchs de tournoi récents
Test avec SU Esport qui a joué le 19/10/2025
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.api.riot_api import RiotAPIClient
from datetime import datetime, timedelta

load_dotenv()

def test_riot_api_tournament_matches():
    """Test de récupération de matchs de tournoi via l'API Riot"""
    
    api = RiotAPIClient(api_key=os.getenv("RIOT_API_KEY"))
    
    print("🔍 Test de l'API Riot - Récupération de matchs de tournoi")
    print("=" * 60)
    
    # Joueurs de test
    # Colfeo#LRC - compte par défaut pour les tests
    # Lamnich#210 - SU Esport, a joué 3 games de tournoi le 19/10/2025
    test_players = [
        {"gameName": "Colfeo", "tagLine": "LRC"},
        {"gameName": "Lamnich", "tagLine": "210"},
    ]
    
    print("\n1️⃣ Résolution des PUUID...")
    puuids = []
    for player in test_players:
        try:
            account_data = api.get_account_by_riot_id(player["gameName"], player["tagLine"])
            puuid = account_data.get("puuid")
            if puuid:
                print(f"✅ {player['gameName']}#{player['tagLine']}: {puuid[:20]}...")
                puuids.append(puuid)
            else:
                print(f"❌ {player['gameName']}#{player['tagLine']}: PUUID non trouvé")
        except Exception as e:
            print(f"❌ Erreur pour {player['gameName']}#{player['tagLine']}: {e}")
    
    if not puuids:
        print("\n❌ Aucun PUUID trouvé, impossible de continuer le test")
        return
    
    print(f"\n2️⃣ Récupération des matchs ARURF Custom (Queue 3130)...")
    print("   🎯 Queue 3130 = ARURF 5v5 Custom (matchs de tournoi)")
    
    # Date précise : 19 octobre 2025
    start_time = int(datetime(2025, 10, 19, 0, 0, 0).timestamp())
    end_time = int(datetime(2025, 10, 20, 23, 59, 59).timestamp())
    
    # Tester avec Lamnich uniquement (qui a joué les matchs)
    test_player = test_players[1]  # Lamnich#210
    puuid = puuids[1]
    
    print(f"\n📋 Matches ARURF Custom pour {test_player['gameName']}#{test_player['tagLine']}:")
    try:
        # Récupérer les IDs de matchs ARURF Custom (queue 3130)
        match_ids = api.get_match_ids_by_puuid(
            puuid=puuid,
            start_time=start_time,
            end_time=end_time,
            count=50,
            queue=3130  # 🎯 ARURF 5v5 Custom uniquement !
        )
        
        print(f"   ✅ {len(match_ids)} matchs ARURF Custom trouvés!")
        
        if not match_ids:
            print("   ⚠️  Aucun match trouvé dans cette période")
            return
        
        # Charger ou créer le fichier match_details.json
        edition_path = "data/editions/edition_999"
        match_details_path = f"{edition_path}/match_details.json"
        
        if os.path.exists(match_details_path):
            with open(match_details_path, 'r', encoding='utf-8') as f:
                all_matches = json.load(f)
        else:
            all_matches = {}
        
        # Traiter tous les matchs ARURF
        print(f"\n3️⃣ Traitement des {len(match_ids)} matchs de tournoi...")
        for idx, match_id in enumerate(match_ids, 1):
            try:
                match_data = api.get_match_details(match_id)
                info = match_data.get("info", {})
                
                game_time = datetime.fromtimestamp(info.get('gameCreation', 0) / 1000)
                duration = info.get("gameDuration", 0)
                queue_id = info.get("queueId")
                game_mode = info.get("gameMode")
                
                participants = info.get("participants", [])
                team_100_win = any(p.get("win") for p in participants if p.get("teamId") == 100)
                
                print(f"\n   [{idx}] {match_id}")
                print(f"      📅 {game_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"      ⏱️  Durée: {duration//60}m {duration%60}s")
                print(f"      🎮 Mode: {game_mode} (Queue {queue_id})")
                print(f"      🏆 Résultat: Team {'100' if team_100_win else '200'} WIN")
                
                # Afficher les 2 équipes
                team_100 = [p for p in participants if p.get("teamId") == 100]
                team_200 = [p for p in participants if p.get("teamId") == 200]
                
                print(f"      🔵 Team 100: {', '.join([p.get('championName', 'Unknown') for p in team_100])}")
                print(f"      🔴 Team 200: {', '.join([p.get('championName', 'Unknown') for p in team_200])}")
                
                # Sauvegarder
                all_matches[match_id] = match_data
                print(f"      ✅ Sauvegardé!")
                
            except Exception as e:
                print(f"      ❌ Erreur: {e}")
        
        # Sauvegarder tout dans le JSON
        with open(match_details_path, 'w', encoding='utf-8') as f:
            json.dump(all_matches, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 {len(match_ids)} matchs sauvegardés dans {match_details_path}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Test terminé!")

if __name__ == "__main__":
    test_riot_api_tournament_matches()
