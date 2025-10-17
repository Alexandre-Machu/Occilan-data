"""
Script rapide pour re-fetch les ranks avec les bons LP
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.data_manager import MultiEditionManager
from src.pipeline.edition_processor import EditionProcessor
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def update_lp_for_edition(edition_number: int):
    """Re-fetch les ranks pour une édition"""
    print(f"\n{'='*60}")
    print(f"Mise à jour des LP pour l'édition {edition_number}")
    print(f"{'='*60}\n")
    
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        print("❌ Erreur: RIOT_API_KEY non trouvée dans .env")
        return
    
    processor = EditionProcessor(edition_number, api_key)
    
    # Re-run step 3 (fetch ranks)
    print("🔄 Re-fetch des ranks avec les LP corrects...")
    result = processor.step3_fetch_ranks()
    
    if result:
        # Compter les joueurs ranked
        ranked_count = 0
        for team_name, team_data in result.items():
            for player in team_data.get("players", []):
                if player.get("tier") != "UNRANKED":
                    ranked_count += 1
        
        print("\n✅ Rangs mis à jour avec succès!")
        print(f"📊 {ranked_count} joueurs ranked trouvés")
        
        # Afficher quelques exemples de Master+ avec LP
        print("\n🎯 Exemples de Master+ avec LP:")
        for team_name, team_data in result.items():
            for player in team_data.get("players", []):
                tier = player.get("tier")
                if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
                    lp = player.get("leaguePoints", 0)
                    print(f"  - {player.get('gameName')}#{player.get('tagLine')}: {tier} ({lp} LP)")
    else:
        print(f"\n❌ Erreur lors de la mise à jour des rangs")

if __name__ == "__main__":
    # Par défaut, update l'édition 7
    edition = 7
    if len(sys.argv) > 1:
        edition = int(sys.argv[1])
    
    update_lp_for_edition(edition)
