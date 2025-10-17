"""
Edition Data Manager
Gestion des fichiers JSON par édition avec validation et CRUD.

Structure par édition:
data/editions/edition_X/
├── config.json              # Configuration édition
├── teams.json               # Équipes avec OP.GG links
├── teams_with_puuid.json    # + PUUID, elo
├── tournament_matches.json  # {team: [match_ids]}
├── match_details.json       # {match_id: full_data}
└── general_stats.json       # Stats agrégées
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EditionDataManager:
    """
    Gestionnaire de données JSON pour une édition de tournoi.
    
    Responsabilités:
    - Création/lecture/écriture des fichiers JSON
    - Validation des schémas
    - Auto-création de la structure de dossiers
    - Backups automatiques
    """
    
    # Structure des fichiers par édition
    EDITION_FILES = [
        "config.json",
        "teams.json",
        "teams_with_puuid.json",
        "tournament_matches.json",
        "match_details.json",
        "general_stats.json"
    ]
    
    def __init__(self, edition_number: int, base_path: str = "data/editions"):
        """
        Initialise le gestionnaire pour une édition.
        
        Args:
            edition_number: Numéro de l'édition (4, 5, 6, 7, ...)
            base_path: Chemin de base pour les éditions
        """
        self.edition_number = edition_number
        self.base_path = Path(base_path)
        self.edition_path = self.base_path / f"edition_{edition_number}"
        
        # Créer la structure si nécessaire
        self._ensure_edition_structure()
        
        logger.info(f"EditionDataManager initialized for edition {edition_number}")
    
    # =========================================================================
    # STRUCTURE & INITIALIZATION
    # =========================================================================
    
    def _ensure_edition_structure(self):
        """Crée la structure de dossiers pour l'édition si elle n'existe pas."""
        self.edition_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Edition directory ensured: {self.edition_path}")
    
    def initialize_edition(
        self,
        edition_name: str,
        year: int,
        start_date: str,
        end_date: str,
        is_private: bool = False
    ):
        """
        Initialise une nouvelle édition avec sa config.
        
        Args:
            edition_name: Nom de l'édition (ex: "OcciLan Stats 7")
            year: Année du tournoi
            start_date: Date de début (ISO format: "2024-01-15")
            end_date: Date de fin (ISO format: "2024-03-20")
            is_private: Si True, visible uniquement par les admins
        
        Example:
            >>> manager = EditionDataManager(7)
            >>> manager.initialize_edition("OcciLan Stats 7", 2024, "2024-01-15", "2024-03-20")
        """
        config = {
            "edition_number": self.edition_number,
            "edition_name": edition_name,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "created_at": datetime.now().isoformat(),
            "status": "pending",  # pending, processing, completed
            "is_private": is_private  # Nouvelle propriété
        }
        
        self.save_config(config)
        
        # Initialiser les autres fichiers vides
        self.save_teams({})
        self.save_teams_with_puuid({})
        self.save_tournament_matches({})
        self.save_match_details({})
        self.save_general_stats({})
        
        logger.info(f"Edition {self.edition_number} initialized: {edition_name}")
    
    def exists(self) -> bool:
        """Vérifie si l'édition existe (config.json présent)."""
        return (self.edition_path / "config.json").exists()
    
    # =========================================================================
    # GENERIC FILE OPERATIONS
    # =========================================================================
    
    def _read_json(self, filename: str) -> Optional[Dict]:
        """
        Lit un fichier JSON de l'édition.
        
        Args:
            filename: Nom du fichier (ex: "teams.json")
        
        Returns:
            Contenu du fichier ou None si inexistant
        """
        file_path = self.edition_path / filename
        
        if not file_path.exists():
            logger.debug(f"File not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded {filename} ({len(str(data))} bytes)")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            return None
    
    def _write_json(self, filename: str, data: Dict, backup: bool = True):
        """
        Écrit un fichier JSON de l'édition.
        
        Args:
            filename: Nom du fichier (ex: "teams.json")
            data: Données à écrire
            backup: Si True, crée un backup avant d'écraser
        """
        file_path = self.edition_path / filename
        
        # Backup si le fichier existe déjà
        if backup and file_path.exists():
            self._backup_file(filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {filename} ({len(str(data))} bytes)")
        except Exception as e:
            logger.error(f"Error writing {filename}: {e}")
            raise
    
    def _backup_file(self, filename: str):
        """Crée un backup d'un fichier avec timestamp."""
        file_path = self.edition_path / filename
        
        if not file_path.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.edition_path / f"{filename}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Backup created: {backup_path.name}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    # =========================================================================
    # CONFIG.JSON
    # =========================================================================
    
    def load_config(self) -> Optional[Dict]:
        """
        Charge la configuration de l'édition.
        
        Returns:
            {
                "edition_number": 7,
                "edition_name": "OcciLan Stats 7",
                "year": 2024,
                "start_date": "2024-01-15",
                "end_date": "2024-03-20",
                "created_at": "2024-01-10T12:00:00",
                "status": "pending"
            }
        """
        return self._read_json("config.json")
    
    def save_config(self, config: Dict):
        """Sauvegarde la configuration de l'édition."""
        self._write_json("config.json", config, backup=False)
    
    def update_status(self, status: str):
        """
        Met à jour le statut de l'édition.
        
        Args:
            status: pending, processing, completed, error
        """
        config = self.load_config() or {}
        config["status"] = status
        config["updated_at"] = datetime.now().isoformat()
        self.save_config(config)
        logger.info(f"Edition {self.edition_number} status → {status}")
    
    # =========================================================================
    # TEAMS.JSON
    # =========================================================================
    
    def load_teams(self) -> Dict[str, Dict]:
        """
        Charge les équipes (sans PUUID).
        
        Returns:
            {
                "KCDQ": {
                    "players": [
                        {"role": "TOP", "game_name": "Player1", "tag_line": "EUW"},
                        ...
                    ],
                    "opgg_link": "https://..."
                },
                ...
            }
        """
        return self._read_json("teams.json") or {}
    
    def save_teams(self, teams: Dict):
        """Sauvegarde les équipes (format teams.json)."""
        self._write_json("teams.json", teams)
    
    def add_team(self, team_name: str, team_data: Dict):
        """
        Ajoute/met à jour une équipe.
        
        Args:
            team_name: Nom de l'équipe
            team_data: {
                "players": [...],
                "opgg_link": "..."
            }
        """
        teams = self.load_teams()
        teams[team_name] = team_data
        self.save_teams(teams)
        logger.info(f"Team '{team_name}' added/updated")
    
    # =========================================================================
    # TEAMS_WITH_PUUID.JSON
    # =========================================================================
    
    def load_teams_with_puuid(self) -> Dict[str, Dict]:
        """
        Charge les équipes avec PUUID et elo.
        
        Returns:
            {
                "KCDQ": {
                    "players": [
                        {
                            "role": "TOP",
                            "game_name": "Player1",
                            "tag_line": "EUW",
                            "puuid": "abc123...",
                            "summoner_id": "xyz789...",
                            "summoner_name": "Player1",
                            "ranked_tier": "DIAMOND",
                            "ranked_rank": "II",
                            "ranked_lp": 45,
                            "wins": 127,
                            "losses": 98
                        },
                        ...
                    ]
                },
                ...
            }
        """
        return self._read_json("teams_with_puuid.json") or {}
    
    def save_teams_with_puuid(self, teams: Dict):
        """Sauvegarde les équipes avec PUUID."""
        self._write_json("teams_with_puuid.json", teams)
    
    # =========================================================================
    # TOURNAMENT_MATCHES.JSON
    # =========================================================================
    
    def load_tournament_matches(self) -> Dict[str, List[str]]:
        """
        Charge les IDs de matchs par équipe.
        
        Returns:
            {
                "KCDQ": ["EUW1_6234567890", "EUW1_6234567891", ...],
                "TeamB": [...],
                ...
            }
        """
        return self._read_json("tournament_matches.json") or {}
    
    def save_tournament_matches(self, matches: Dict):
        """Sauvegarde les IDs de matchs."""
        self._write_json("tournament_matches.json", matches)
    
    def add_team_matches(self, team_name: str, match_ids: List[str]):
        """
        Ajoute des match IDs pour une équipe.
        
        Args:
            team_name: Nom de l'équipe
            match_ids: Liste d'IDs de matchs
        """
        matches = self.load_tournament_matches()
        
        if team_name not in matches:
            matches[team_name] = []
        
        # Éviter les doublons
        existing = set(matches[team_name])
        new_matches = [m for m in match_ids if m not in existing]
        
        matches[team_name].extend(new_matches)
        self.save_tournament_matches(matches)
        
        logger.info(f"Added {len(new_matches)} new matches for {team_name} ({len(matches[team_name])} total)")
    
    # =========================================================================
    # MATCH_DETAILS.JSON
    # =========================================================================
    
    def load_match_details(self) -> Dict[str, Dict]:
        """
        Charge les détails de tous les matchs.
        
        Returns:
            {
                "EUW1_6234567890": {
                    "metadata": {...},
                    "info": {...}
                },
                ...
            }
        """
        return self._read_json("match_details.json") or {}
    
    def save_match_details(self, match_details: Dict):
        """Sauvegarde les détails de matchs."""
        self._write_json("match_details.json", match_details)
    
    def add_match_detail(self, match_id: str, match_data: Dict):
        """
        Ajoute les détails d'un match.
        
        Args:
            match_id: ID du match
            match_data: Données complètes du match (Match-V5)
        """
        details = self.load_match_details()
        details[match_id] = match_data
        self.save_match_details(details)
        logger.debug(f"Match detail added: {match_id}")
    
    def get_match_detail(self, match_id: str) -> Optional[Dict]:
        """Récupère les détails d'un match spécifique."""
        details = self.load_match_details()
        return details.get(match_id)
    
    # =========================================================================
    # GENERAL_STATS.JSON
    # =========================================================================
    
    def load_general_stats(self) -> Dict:
        """
        Charge les statistiques générales.
        
        Returns:
            {
                "longest_game": {...},
                "shortest_game": {...},
                "most_kills_in_game": {...},
                "player_stats": {
                    "Player1#EUW": {...},
                    ...
                },
                "team_stats": {
                    "KCDQ": {...},
                    ...
                },
                "champion_stats": {
                    "157": {...},  # Yasuo
                    ...
                }
            }
        """
        return self._read_json("general_stats.json") or {}
    
    def save_general_stats(self, stats: Dict):
        """Sauvegarde les statistiques générales."""
        self._write_json("general_stats.json", stats)
    
    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================
    
    def get_all_match_ids(self) -> List[str]:
        """
        Récupère tous les IDs de matchs de l'édition.
        
        Returns:
            Liste unique de tous les match IDs
        """
        matches = self.load_tournament_matches()
        all_ids = []
        
        for team_matches in matches.values():
            all_ids.extend(team_matches)
        
        # Dédupliquer (un match peut avoir plusieurs équipes participantes)
        unique_ids = list(set(all_ids))
        logger.debug(f"Total unique matches: {len(unique_ids)}")
        return unique_ids
    
    def get_teams_count(self) -> int:
        """Compte le nombre d'équipes."""
        teams = self.load_teams()
        return len(teams)
    
    def get_matches_count(self) -> int:
        """Compte le nombre de matchs uniques."""
        return len(self.get_all_match_ids())
    
    def get_summary(self) -> Dict:
        """
        Génère un résumé de l'édition.
        
        Returns:
            {
                "edition_number": 7,
                "status": "completed",
                "teams_count": 12,
                "matches_count": 45,
                "players_count": 60,
                "has_stats": True
            }
        """
        config = self.load_config() or {}
        teams = self.load_teams()
        stats = self.load_general_stats()
        
        # Handle both list and dict formats
        if isinstance(teams, list):
            players_count = sum(len(team.get("players", [])) for team in teams)
            teams_count = len(teams)
        elif isinstance(teams, dict):
            players_count = sum(len(team.get("players", [])) for team in teams.values())
            teams_count = len(teams)
        else:
            players_count = 0
            teams_count = 0
        
        return {
            "edition_number": self.edition_number,
            "edition_name": config.get("edition_name", f"Edition {self.edition_number}"),
            "year": config.get("year"),
            "status": config.get("status", "unknown"),
            "total_teams": teams_count,
            "teams_count": teams_count,  # Legacy compatibility
            "total_players": players_count,
            "players_count": players_count,  # Legacy compatibility
            "total_matches": self.get_matches_count(),
            "matches_count": self.get_matches_count(),  # Legacy compatibility
            "has_stats": bool(stats)
        }
    
    # =========================================================================
    # CLEANUP & MAINTENANCE
    # =========================================================================
    
    def clear_all_data(self):
        """
        Supprime toutes les données de l'édition (garde la structure).
        Utile pour reset une édition.
        """
        for filename in self.EDITION_FILES:
            file_path = self.edition_path / filename
            if file_path.exists():
                self._backup_file(filename)
                file_path.unlink()
        
        logger.warning(f"All data cleared for edition {self.edition_number}")
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Exporte toutes les données de l'édition en un seul dict.
        Utile pour backup complet ou transfert.
        
        Returns:
            {
                "config": {...},
                "teams": {...},
                "teams_with_puuid": {...},
                "tournament_matches": {...},
                "match_details": {...},
                "general_stats": {...}
            }
        """
        return {
            "config": self.load_config(),
            "teams": self.load_teams(),
            "teams_with_puuid": self.load_teams_with_puuid(),
            "tournament_matches": self.load_tournament_matches(),
            "match_details": self.load_match_details(),
            "general_stats": self.load_general_stats()
        }


# =============================================================================
# HELPER: MULTI-EDITION MANAGER
# =============================================================================

class MultiEditionManager:
    """Gestionnaire pour plusieurs éditions."""
    
    def __init__(self, base_path: str = "data/editions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def get_edition_manager(self, edition_number: int) -> EditionDataManager:
        """Récupère le manager pour une édition."""
        return EditionDataManager(edition_number, str(self.base_path))
    
    def list_editions(self, include_private: bool = True) -> List[int]:
        """
        Liste toutes les éditions disponibles.
        
        Args:
            include_private: Si False, exclut les éditions privées
        
        Returns:
            Liste des numéros d'éditions [4, 5, 6, 7]
        """
        editions = []
        
        for path in self.base_path.iterdir():
            if path.is_dir() and path.name.startswith("edition_"):
                try:
                    edition_num = int(path.name.split("_")[1])
                    
                    # Si on n'inclut pas les privées, vérifier la config
                    if not include_private:
                        manager = self.get_edition_manager(edition_num)
                        config = manager.load_config()
                        if config and config.get("is_private", False):
                            continue  # Skip cette édition
                    
                    editions.append(edition_num)
                except ValueError:
                    continue
        
        return sorted(editions)
    
    def get_all_summaries(self) -> List[Dict]:
        """
        Récupère les résumés de toutes les éditions.
        
        Returns:
            [
                {"edition_number": 4, "status": "completed", ...},
                {"edition_number": 5, "status": "completed", ...},
                ...
            ]
        """
        summaries = []
        
        for edition_num in self.list_editions():
            manager = self.get_edition_manager(edition_num)
            summaries.append(manager.get_summary())
        
        return summaries


# =============================================================================
# EXEMPLE D'UTILISATION
# =============================================================================

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("TEST: EditionDataManager")
    print("="*70)
    
    # Test 1: Créer une nouvelle édition
    print("\n1. Initialiser édition 7:")
    manager = EditionDataManager(7)
    
    if not manager.exists():
        manager.initialize_edition(
            edition_name="OcciLan Stats 7",
            year=2024,
            start_date="2024-01-15",
            end_date="2024-03-20"
        )
        print("   ✅ Édition 7 initialisée")
    else:
        print("   ℹ️  Édition 7 existe déjà")
    
    # Test 2: Ajouter une équipe
    print("\n2. Ajouter une équipe:")
    team_data = {
        "players": [
            {"role": "TOP", "game_name": "TopPlayer", "tag_line": "EUW"},
            {"role": "JUNGLE", "game_name": "JunglePlayer", "tag_line": "EUW"},
            {"role": "MID", "game_name": "MidPlayer", "tag_line": "EUW"},
            {"role": "ADC", "game_name": "AdcPlayer", "tag_line": "EUW"},
            {"role": "SUPPORT", "game_name": "SupportPlayer", "tag_line": "EUW"}
        ],
        "opgg_link": "https://op.gg/multisearch/euw?summoners=..."
    }
    
    manager.add_team("KCDQ", team_data)
    print("   ✅ Équipe 'KCDQ' ajoutée")
    
    # Test 3: Charger et afficher
    print("\n3. Charger les équipes:")
    teams = manager.load_teams()
    print(f"   ✅ {len(teams)} équipe(s) chargée(s)")
    for team_name, data in teams.items():
        print(f"      - {team_name}: {len(data['players'])} joueurs")
    
    # Test 4: Résumé
    print("\n4. Résumé de l'édition:")
    summary = manager.get_summary()
    print(f"   Édition: {summary['edition_name']}")
    print(f"   Année: {summary['year']}")
    print(f"   Status: {summary['status']}")
    print(f"   Équipes: {summary['teams_count']}")
    print(f"   Matchs: {summary['matches_count']}")
    print(f"   Joueurs: {summary['players_count']}")
    
    # Test 5: Multi-éditions
    print("\n5. Liste des éditions:")
    multi = MultiEditionManager()
    editions = multi.list_editions()
    print(f"   ✅ {len(editions)} édition(s) trouvée(s): {editions}")
    
    print("\n" + "="*70)
    print("Tests terminés !")
    print("="*70 + "\n")
