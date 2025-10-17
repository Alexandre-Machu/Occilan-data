"""
Script rapide pour re-fetch les ranks avec les bons LP
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.data_manager import MultiEditionManager
from pipeline.edition_processor import EditionProcessor

def update_lp_for_edition(edition_number: int):
    """Re-fetch les ranks pour une édition"""
    print(f"\n{'='*60}")
    print(f"Mise à jour des LP pour l'édition {edition_number}")
    print(f"{'='*60}\n")
    
    processor = EditionProcessor(edition_number)
    
    # Re-run step 3 (fetch ranks)
    print("🔄 Re-fetch des ranks avec les LP corrects...")
    result = processor.step3_fetch_ranks()
    
    if result["status"] == "success":
        print("\n✅ Rangs mis à jour avec succès!")
        print(f"📊 {result.get('ranked_count', 0)} joueurs ranked trouvés")
    else:
        print(f"\n❌ Erreur: {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    # Par défaut, update l'édition 7
    edition = 7
    if len(sys.argv) > 1:
        edition = int(sys.argv[1])
    
    update_lp_for_edition(edition)
