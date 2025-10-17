"""
OP.GG Link Parser
Extrait les Riot IDs (gameName#tagLine) depuis les liens OP.GG multisearch.

Formats supportés:
- https://www.op.gg/multisearch/euw?summoners=Player1-EUW,Player2-EUW,Player3-EUW
- https://op.gg/multisearch/euw?summoners=Player1-EUW%2CPlayer2-EUW
"""

import re
import logging
from typing import List, Dict, Tuple
from urllib.parse import urlparse, parse_qs, unquote

logger = logging.getLogger(__name__)


class OPGGParser:
    """Parse les liens OP.GG pour extraire les Riot IDs."""
    
    # Rôles League of Legends (ordre standard)
    ROLES = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
    
    @staticmethod
    def parse_multisearch_url(opgg_link: str) -> List[Tuple[str, str]]:
        """
        Parse un lien OP.GG multisearch et extrait les Riot IDs.
        
        Args:
            opgg_link: URL OP.GG multisearch
                       Ex: "https://op.gg/multisearch/euw?summoners=Player1-EUW,Player2-EUW"
        
        Returns:
            Liste de tuples (gameName, tagLine)
            Ex: [("Player1", "EUW"), ("Player2", "EUW")]
        
        Raises:
            ValueError: Si l'URL est invalide ou le format incorrect
        """
        if not opgg_link or not opgg_link.strip():
            raise ValueError("OP.GG link is empty")
        
        # Vérifier que c'est bien un lien OP.GG
        if "op.gg" not in opgg_link.lower():
            raise ValueError(f"Not an OP.GG link: {opgg_link}")
        
        # Parser l'URL
        try:
            parsed_url = urlparse(opgg_link)
            query_params = parse_qs(parsed_url.query)
        except Exception as e:
            raise ValueError(f"Invalid URL format: {e}")
        
        # Extraire le paramètre "summoners"
        if "summoners" not in query_params:
            raise ValueError("Missing 'summoners' parameter in OP.GG link")
        
        summoners_str = query_params["summoners"][0]
        summoners_str = unquote(summoners_str)  # Décoder %2C → ,
        
        # Séparer les noms (virgule ou %2C)
        summoner_names = [s.strip() for s in summoners_str.split(",") if s.strip()]
        
        if not summoner_names:
            raise ValueError("No summoners found in OP.GG link")
        
        # Extraire gameName#tagLine de chaque summoner
        riot_ids = []
        for summoner in summoner_names:
            try:
                game_name, tag_line = OPGGParser._parse_summoner_name(summoner)
                riot_ids.append((game_name, tag_line))
            except ValueError as e:
                logger.warning(f"Skipping invalid summoner name '{summoner}': {e}")
                continue
        
        if not riot_ids:
            raise ValueError("No valid Riot IDs extracted from OP.GG link")
        
        logger.info(f"Extracted {len(riot_ids)} Riot IDs from OP.GG link")
        return riot_ids
    
    @staticmethod
    def _parse_summoner_name(summoner_name: str) -> Tuple[str, str]:
        """
        Parse un nom de summoner et extrait gameName + tagLine.
        
        Formats supportés:
        - "Player1-EUW" → ("Player1", "EUW")
        - "Player1#EUW" → ("Player1", "EUW")
        - "Player One-EUW" → ("Player One", "EUW")  (avec espaces)
        
        Args:
            summoner_name: Nom au format "Player-TAG" ou "Player#TAG"
        
        Returns:
            (gameName, tagLine)
        
        Raises:
            ValueError: Si le format est invalide
        """
        summoner_name = summoner_name.strip()
        
        # Détecter le séparateur (- ou #)
        if "-" in summoner_name:
            separator = "-"
            # Séparer sur le DERNIER séparateur (car gameName peut contenir des -)
            parts = summoner_name.rsplit(separator, 1)
            
            if len(parts) != 2:
                raise ValueError(f"Invalid format: {summoner_name}")
            
            game_name = parts[0].strip()
            tag_line = parts[1].strip()
            
        elif "#" in summoner_name:
            separator = "#"
            # Séparer sur le DERNIER séparateur (car gameName peut contenir des -)
            parts = summoner_name.rsplit(separator, 1)
            
            if len(parts) != 2:
                raise ValueError(f"Invalid format: {summoner_name}")
            
            game_name = parts[0].strip()
            tag_line = parts[1].strip()
            
        else:
            # Pas de séparateur = tagline par défaut EUW
            game_name = summoner_name
            tag_line = "EUW"
        
        if not game_name:
            raise ValueError(f"Empty gameName: {summoner_name}")
        
        return (game_name, tag_line)
    
    @staticmethod
    def parse_team_opgg(team_name: str, opgg_link: str, roles: List[str] = None) -> Dict:
        """
        Parse un lien OP.GG pour une équipe complète et assigne les rôles.
        
        Args:
            team_name: Nom de l'équipe
            opgg_link: Lien OP.GG multisearch
            roles: Liste des rôles à assigner (ordre: TOP, JUNGLE, MID, ADC, SUPPORT)
                   Si None, utilise l'ordre standard
        
        Returns:
            {
                "team_name": "KCDQ",
                "opgg_link": "https://...",
                "players": [
                    {"role": "TOP", "game_name": "Player1", "tag_line": "EUW"},
                    {"role": "JUNGLE", "game_name": "Player2", "tag_line": "EUW"},
                    ...
                ]
            }
        
        Raises:
            ValueError: Si nombre de joueurs ≠ 5 ou autre erreur
        """
        if roles is None:
            roles = OPGGParser.ROLES
        
        # Extraire les Riot IDs
        riot_ids = OPGGParser.parse_multisearch_url(opgg_link)
        
        # Vérifier qu'on a exactement 5 joueurs
        if len(riot_ids) != 5:
            raise ValueError(f"Expected 5 players, got {len(riot_ids)}: {riot_ids}")
        
        # Assigner les rôles (ordre OP.GG = ordre rôles)
        players = []
        for i, (game_name, tag_line) in enumerate(riot_ids):
            players.append({
                "role": roles[i],
                "gameName": game_name,  # Use camelCase for consistency
                "tagLine": tag_line
            })
        
        return {
            "name": team_name,  # Use 'name' instead of 'team_name'
            "opgg_link": opgg_link,
            "players": players
        }
    
    @staticmethod
    def validate_opgg_link(opgg_link: str) -> bool:
        """
        Vérifie qu'un lien OP.GG est valide (sans parser).
        
        Args:
            opgg_link: Lien OP.GG à vérifier
        
        Returns:
            True si valide, False sinon
        """
        try:
            OPGGParser.parse_multisearch_url(opgg_link)
            return True
        except ValueError:
            return False


# =============================================================================
# EXEMPLE D'UTILISATION
# =============================================================================

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("TEST: OPGGParser")
    print("="*70)
    
    # Test 1: Lien simple
    print("\n1. Parse lien OP.GG simple:")
    link1 = "https://www.op.gg/multisearch/euw?summoners=Player1-EUW,Player2-EUW,Player3-EUW,Player4-EUW,Player5-EUW"
    
    try:
        riot_ids = OPGGParser.parse_multisearch_url(link1)
        print(f"   ✅ {len(riot_ids)} Riot IDs extraits:")
        for game_name, tag_line in riot_ids:
            print(f"      - {game_name}#{tag_line}")
    except ValueError as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Parse équipe complète
    print("\n2. Parse équipe complète avec rôles:")
    
    try:
        team_data = OPGGParser.parse_team_opgg("KCDQ", link1)
        print(f"   ✅ Équipe '{team_data['team_name']}' parsée:")
        for player in team_data["players"]:
            print(f"      {player['role']:7} → {player['game_name']}#{player['tag_line']}")
    except ValueError as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "="*70)
    print("Tests terminés !")
    print("="*70 + "\n")
