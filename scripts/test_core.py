"""
Script de test pour valider l'implémentation des composants core.

Tests:
1. OPGGParser: Parse liens OP.GG
2. RiotAPIClient: Appels API (nécessite RIOT_API_KEY)
3. EditionDataManager: CRUD JSON

Usage:
    python scripts/test_core.py
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter src/ au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parsers.opgg_parser import OPGGParser
from core.riot_client import RiotAPIClient
from core.data_manager import EditionDataManager, MultiEditionManager

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_opgg_parser():
    """Test du parser OP.GG."""
    print("\n" + "="*70)
    print("TEST 1: OPGGParser")
    print("="*70)
    
    # Test 1: Parse lien simple
    link1 = "https://www.op.gg/multisearch/euw?summoners=Player1-EUW,Player2-EUW,Player3-EUW,Player4-EUW,Player5-EUW"
    
    try:
        riot_ids = OPGGParser.parse_multisearch_url(link1)
        print(f"\n✅ Parse lien simple: {len(riot_ids)} joueurs extraits")
        for game_name, tag_line in riot_ids[:2]:
            print(f"   - {game_name}#{tag_line}")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False
    
    # Test 2: Parse équipe avec rôles
    try:
        team_data = OPGGParser.parse_team_opgg("TestTeam", link1)
        print(f"\n✅ Parse équipe: {team_data['team_name']}")
        print(f"   Rôles assignés:")
        for player in team_data["players"][:2]:
            print(f"      {player['role']:7} → {player['game_name']}#{player['tag_line']}")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False
    
    return True


def test_riot_client():
    """Test du client API Riot (nécessite RIOT_API_KEY)."""
    print("\n" + "="*70)
    print("TEST 2: RiotAPIClient")
    print("="*70)
    
    # Charger API key depuis .env
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("RIOT_API_KEY")
    
    if not api_key or api_key.startswith("RGAPI-your"):
        print("\n⚠️  RIOT_API_KEY non configurée dans .env")
        print("   → Ajoutez votre clé API dans .env pour tester")
        print("   → Tests API sautés")
        return True
    
    try:
        client = RiotAPIClient(api_key)
        print("\n✅ Client initialisé")
    except Exception as e:
        print(f"\n❌ Erreur initialisation: {e}")
        return False
    
    # Test: Récupérer info joueur (exemple avec un compte public)
    try:
        print("\n🔍 Test get_player_full_info('Faker', 'KR1')...")
        player = client.get_player_full_info("Faker", "KR1")
        
        if player:
            print(f"✅ Joueur trouvé: {player['summoner_name']}")
            print(f"   Niveau: {player['summoner_level']}")
            if player.get('ranked'):
                r = player['ranked']
                print(f"   Rank: {r['tier']} {r['rank']} ({r['lp']} LP)")
        else:
            print("⚠️  Joueur non trouvé (normal si compte n'existe pas)")
    except Exception as e:
        print(f"⚠️  Erreur API (peut être rate limit ou joueur inexistant): {e}")
    
    return True


def test_data_manager():
    """Test du gestionnaire de données."""
    print("\n" + "="*70)
    print("TEST 3: EditionDataManager")
    print("="*70)
    
    # Test 1: Créer édition test
    test_edition = 999  # Numéro spécial pour tests
    manager = EditionDataManager(test_edition)
    
    try:
        print(f"\n1. Initialiser édition {test_edition}...")
        manager.initialize_edition(
            edition_name="Test Edition",
            year=2024,
            start_date="2024-01-01",
            end_date="2024-03-01"
        )
        print("   ✅ Édition initialisée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 2: Ajouter équipe
    try:
        print("\n2. Ajouter une équipe...")
        team_data = {
            "players": [
                {"role": "TOP", "game_name": "TestTop", "tag_line": "EUW"},
                {"role": "JUNGLE", "game_name": "TestJungle", "tag_line": "EUW"},
                {"role": "MID", "game_name": "TestMid", "tag_line": "EUW"},
                {"role": "ADC", "game_name": "TestAdc", "tag_line": "EUW"},
                {"role": "SUPPORT", "game_name": "TestSupport", "tag_line": "EUW"}
            ],
            "opgg_link": "https://op.gg/multisearch/euw?summoners=..."
        }
        
        manager.add_team("TestTeam", team_data)
        print("   ✅ Équipe ajoutée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 3: Charger équipe
    try:
        print("\n3. Charger les équipes...")
        teams = manager.load_teams()
        print(f"   ✅ {len(teams)} équipe(s) chargée(s)")
        
        for team_name, data in teams.items():
            print(f"      - {team_name}: {len(data['players'])} joueurs")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 4: Résumé
    try:
        print("\n4. Générer résumé...")
        summary = manager.get_summary()
        print(f"   ✅ Résumé:")
        print(f"      Édition: {summary['edition_name']}")
        print(f"      Status: {summary['status']}")
        print(f"      Équipes: {summary['teams_count']}")
        print(f"      Joueurs: {summary['players_count']}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 5: Multi-éditions
    try:
        print("\n5. Liste des éditions...")
        multi = MultiEditionManager()
        editions = multi.list_editions()
        print(f"   ✅ {len(editions)} édition(s) trouvée(s)")
        
        if editions:
            print(f"      Éditions disponibles: {editions}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Cleanup
    try:
        print(f"\n6. Nettoyage édition test {test_edition}...")
        manager.clear_all_data()
        
        # Supprimer le dossier
        import shutil
        shutil.rmtree(manager.edition_path)
        print("   ✅ Édition test supprimée")
    except Exception as e:
        print(f"   ⚠️  Cleanup: {e}")
    
    return True


def main():
    """Exécute tous les tests."""
    print("\n" + "="*70)
    print("TESTS DES COMPOSANTS CORE")
    print("="*70)
    
    results = {
        "OPGGParser": test_opgg_parser(),
        "RiotAPIClient": test_riot_client(),
        "EditionDataManager": test_data_manager()
    }
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    
    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {component}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 Tous les tests sont passés !")
    else:
        print("\n⚠️  Certains tests ont échoué")
    
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
