"""
Script de nettoyage du projet Occilan-data
Supprime tous les fichiers inutiles, backups, tests obsolètes, etc.
"""

import os
import shutil
from pathlib import Path

def cleanup():
    base_path = Path("d:/Occilan-data")
    
    # Liste des fichiers et dossiers à supprimer
    files_to_delete = [
        # Backups JSON
        "data/editions/edition_6/general_stats.json.backup_20251018_210444",
        "data/editions/edition_6/teams_with_puuid.json.backup_20251018_210254",
        "data/editions/edition_6/teams_with_puuid.json.backup_20251018_210442",
        "data/editions/edition_6/tournament_matches.json.backup_20251018_210444",
        "data/editions/edition_6/tournament_matches.json.backup_20251018_211500",
        
        # Backups Edition 7
        "data/editions/edition_7/teams_with_puuid.json.backup_20251017_143714",
        "data/editions/edition_7/teams_with_puuid.json.backup_20251017_143905",
        
        # Backup pages Streamlit
        "src/streamlit_app/pages/1_📊_Stats_Generales.py.backup",
        
        # Fichiers database SQL (obsolètes)
        "src/database/schema.sql",
        "src/database/db_manager.py",
        "src/database/models.py",
        
        # Scripts de test obsolètes
        "scripts/test_api_real.py",
        "scripts/test_workflow.py",
        "scripts/test_pipeline.py",
        "scripts/test_core.py",
        "tests/test_parsers.py",
        
        # Scripts de migration obsolètes
        "scripts/init_db.py",
        "scripts/migrate_edition_6.py",
        "scripts/fix_edition_6_puuids.py",
        
        # Documentation obsolète
        "ARCHITECTURE_SUMMARY.md",
        "FICHIERS_CREES.md",
        "NEXT_STEPS.md",
        "OcciLan_Stats_Documentation.md",
        "QUICK_START.md",
        "README_NEW.md",
        "SESSION_RECAP.md",
        "Occi Lan Stats — Architecture & Delivery Plan.pdf",
        "docs/ARCHITECTURE_FINAL.md",
        "docs/ARCHITECTURE_REVISED.md",
        "docs/ARCHITECTURE.md",
        "docs/FIX_API_2025.md",
        "docs/IMPLEMENTATION_STATUS.md",
    ]
    
    # Dossiers à supprimer entièrement
    folders_to_delete = [
        "other projects",
        "tests",
        "src/database",  # Toute la partie database SQL
    ]
    
    deleted_count = 0
    
    print("🧹 Nettoyage du projet Occilan-data...\n")
    
    # Suppression des fichiers
    for file_path in files_to_delete:
        full_path = base_path / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"✅ Supprimé : {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
        else:
            print(f"⚠️  Fichier déjà absent : {file_path}")
    
    # Suppression des dossiers
    for folder_path in folders_to_delete:
        full_path = base_path / folder_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"✅ Dossier supprimé : {folder_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {folder_path}: {e}")
        else:
            print(f"⚠️  Dossier déjà absent : {folder_path}")
    
    print(f"\n✅ Nettoyage terminé ! {deleted_count} éléments supprimés.")
    
    # Afficher la structure restante
    print("\n📁 Structure du projet après nettoyage :")
    print("""
    Occilan-data/
    ├── .env                          # Configuration API (privé)
    ├── .env.example                  # Template de configuration
    ├── .gitignore                    # Fichiers ignorés par Git
    ├── README.md                     # Documentation principale
    ├── requirements.txt              # Dépendances Python
    ├── LICENSE                       # Licence du projet
    │
    ├── config/
    │   └── config.yaml               # Configuration générale
    │
    ├── data/
    │   ├── cache/                    # Cache API (PUUID, matches)
    │   ├── editions/                 # Données par édition
    │   │   ├── edition_6/            # Edition 6 (data manuelle)
    │   │   ├── edition_7/            # Edition 7 (data API)
    │   │   └── edition_999/          # Edition test
    │   ├── exports/                  # Exports CSV/Excel
    │   ├── processed/                # Données traitées
    │   └── raw/                      # Données brutes
    │
    ├── docs/
    │   ├── API_GUIDE.md              # Guide d'utilisation API
    │   ├── API_WORKFLOW.md           # Workflow des appels API
    │   └── CONTRIBUTING.md           # Guide de contribution
    │
    ├── scripts/
    │   ├── export_stats.py           # Export des statistiques
    │   ├── refresh_data.py           # Refresh des données
    │   ├── update_edition_6_ranks.py # Mise à jour rangs édition 6
    │   └── update_lp.py              # Mise à jour LP
    │
    └── src/
        ├── api/                      # Clients API (Riot, Toornament)
        ├── core/                     # Logique métier
        ├── parsers/                  # Parseurs CSV/OPGG
        ├── pipeline/                 # Pipeline de traitement
        ├── utils/                    # Utilitaires
        └── streamlit_app/            # Application Streamlit
            ├── app.py                # Point d'entrée
            └── pages/                # Pages de l'application
    """)

if __name__ == "__main__":
    cleanup()
