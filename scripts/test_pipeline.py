"""
Test complet du pipeline de traitement des données
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.edition_processor import EditionProcessor
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def progress_callback(message: str, progress: float):
    """Callback pour afficher la progression"""
    print(f"[{progress*100:.0f}%] {message}")


def main():
    # Load API key
    load_dotenv()
    api_key = os.getenv("RIOT_API_KEY")
    
    if not api_key:
        logger.error("❌ RIOT_API_KEY non trouvée dans .env")
        return
    
    logger.info(f"✅ API Key chargée: {api_key[:20]}...")
    
    # Test avec l'édition 999
    edition_id = 999
    logger.info(f"\n{'='*60}")
    logger.info(f"Test du pipeline complet - Edition {edition_id}")
    logger.info(f"{'='*60}\n")
    
    # Initialize processor
    processor = EditionProcessor(
        edition_id=edition_id,
        api_key=api_key,
        progress_callback=progress_callback
    )
    
    # Execute full pipeline
    logger.info("🚀 Démarrage du pipeline complet...\n")
    
    try:
        result = processor.run_full_pipeline()
        
        print("\n" + "="*60)
        print("📊 RÉSULTATS")
        print("="*60)
        
        if result["success"]:
            print("✅ Pipeline exécuté avec succès !")
            print(f"\n📝 Résumé:")
            for key, value in result.get("summary", {}).items():
                print(f"  • {key}: {value}")
        else:
            print("❌ Le pipeline a échoué")
        
        if result.get("errors"):
            print(f"\n⚠️ Erreurs ({len(result['errors'])}):")
            for error in result["errors"]:
                print(f"  • {error}")
        
        if result.get("warnings"):
            print(f"\n⚠️ Avertissements ({len(result['warnings'])}):")
            for warning in result["warnings"]:
                print(f"  • {warning}")
                
    except Exception as e:
        logger.exception(f"❌ Erreur fatale: {e}")


if __name__ == "__main__":
    main()
