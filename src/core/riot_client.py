"""
Riot Games API Client
Centralise tous les appels API Riot avec rate limiting, retry logic et cache.

Endpoints implémentés:
- Account-V1: Riot ID → PUUID
- Summoner-V4: PUUID → summoner info
- League-V4: summoner ID → rank/LP
- Match-V5: PUUID → match IDs, match details
"""

import os
import time
import json
import logging
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class RiotAPIClient:
    """
    Client API Riot unifié avec gestion de rate limit et cache.
    
    Regional routing:
    - Account-V1, Match-V5: region (europe, americas, asia, sea)
    - Summoner-V4, League-V4: platform (euw1, na1, kr, etc.)
    """
    
    # Rate limiting
    REQUEST_DELAY = 0.05  # 50ms entre requêtes (20 req/s max)
    MAX_RETRIES = 3
    
    # Régions et platforms
    REGION = "europe"  # Pour Account-V1 et Match-V5
    PLATFORM = "euw1"  # Pour Summoner-V4 et League-V4
    
    def __init__(self, api_key: str, cache_dir: str = "data/cache"):
        """
        Initialise le client API.
        
        Args:
            api_key: Clé API Riot Games
            cache_dir: Répertoire pour le cache local
        """
        self.api_key = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache des matchs
        self.matches_cache_dir = self.cache_dir / "matches"
        self.matches_cache_dir.mkdir(exist_ok=True)
        
        # Cache PUUID → summonerName
        self.puuid_map_file = self.cache_dir / "puuid_map.json"
        self.puuid_map = self._load_puuid_map()
        
        # Headers pour toutes les requêtes
        self.headers = {
            "X-Riot-Token": self.api_key,
            "Accept": "application/json"
        }
        
        # Timestamp dernière requête (rate limiting)
        self.last_request_time = 0
        
        logger.info(f"RiotAPIClient initialized (region={self.REGION}, platform={self.PLATFORM})")
    
    # =========================================================================
    # RATE LIMITING & RETRY LOGIC
    # =========================================================================
    
    def _wait_for_rate_limit(self):
        """Attend pour respecter le rate limit (20 req/s)."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Effectue une requête API avec retry logic.
        
        Args:
            url: URL complète de l'endpoint
            params: Paramètres query string
        
        Returns:
            Réponse JSON ou None si erreur
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                self._wait_for_rate_limit()
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                # Succès
                if response.status_code == 200:
                    return response.json()
                
                # Rate limit dépassé
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    logger.warning(f"Rate limited (429), waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                
                # Non trouvé (normal, pas une erreur)
                elif response.status_code == 404:
                    logger.debug(f"Resource not found (404): {url}")
                    return None
                
                # Autres erreurs
                else:
                    logger.warning(f"API error {response.status_code}: {response.text}")
                    if attempt < self.MAX_RETRIES - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time}s... (attempt {attempt + 1}/{self.MAX_RETRIES})")
                        time.sleep(wait_time)
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        logger.error(f"Failed after {self.MAX_RETRIES} retries: {url}")
        return None
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    def _load_puuid_map(self) -> Dict[str, str]:
        """Charge le mapping PUUID → summonerName depuis le cache."""
        if self.puuid_map_file.exists():
            try:
                with open(self.puuid_map_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading puuid_map: {e}")
        return {}
    
    def _save_puuid_map(self):
        """Sauvegarde le mapping PUUID → summonerName."""
        try:
            with open(self.puuid_map_file, 'w', encoding='utf-8') as f:
                json.dump(self.puuid_map, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving puuid_map: {e}")
    
    def _get_cached_match(self, match_id: str) -> Optional[Dict]:
        """Récupère un match depuis le cache local."""
        cache_file = self.matches_cache_dir / f"{match_id}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    logger.debug(f"Match {match_id} loaded from cache")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cached match {match_id}: {e}")
        return None
    
    def _cache_match(self, match_id: str, match_data: Dict):
        """Sauvegarde un match dans le cache local."""
        cache_file = self.matches_cache_dir / f"{match_id}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Match {match_id} cached")
        except Exception as e:
            logger.error(f"Error caching match {match_id}: {e}")
    
    # =========================================================================
    # ACCOUNT-V1: Riot ID → PUUID
    # =========================================================================
    
    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """
        Convertit un Riot ID (gameName#tagLine) en PUUID.
        
        Args:
            game_name: Nom du joueur (sans le #)
            tag_line: Tag après le # (ex: "EUW")
        
        Returns:
            {"puuid": "...", "gameName": "...", "tagLine": "..."}
            ou None si non trouvé
        
        Exemple:
            >>> client.get_account_by_riot_id("Player1", "EUW")
            {"puuid": "abc123...", "gameName": "Player1", "tagLine": "EUW"}
        """
        url = f"https://{self.REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        
        logger.debug(f"Fetching PUUID for {game_name}#{tag_line}...")
        result = self._make_request(url)
        
        if result:
            logger.info(f"✓ PUUID found for {game_name}#{tag_line}")
        else:
            logger.warning(f"✗ PUUID not found for {game_name}#{tag_line}")
        
        return result
    
    # =========================================================================
    # SUMMONER-V4: PUUID → Summoner Info
    # =========================================================================
    
    def get_summoner_by_puuid(self, puuid: str) -> Optional[Dict]:
        """
        Récupère les infos summoner à partir du PUUID.
        
        Args:
            puuid: PUUID du joueur
        
        Returns:
            {
                "id": "encrypted_summoner_id",  # Pour League-V4
                "accountId": "...",
                "puuid": "...",
                "name": "Player1",
                "profileIconId": 1234,
                "summonerLevel": 234
            }
            ou None si non trouvé
        
        Exemple:
            >>> client.get_summoner_by_puuid("abc123...")
            {"id": "xyz789...", "name": "Player1", ...}
        """
        url = f"https://{self.PLATFORM}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        
        logger.debug(f"Fetching summoner info for PUUID {puuid[:20]}...")
        result = self._make_request(url)
        
        if result:
            # Mise à jour cache PUUID → gameName (nouveau format Riot ID)
            summoner_name = result.get("gameName", result.get("name", "Unknown"))
            self.puuid_map[puuid] = summoner_name
            self._save_puuid_map()
            logger.info(f"✓ Summoner info found (level {result.get('summonerLevel', '?')})")
            logger.debug(f"Summoner full data: {result}")
        
        return result
    
    # =========================================================================
    # LEAGUE-V4: Summoner ID → Rank/LP
    # =========================================================================
    
    def get_ranked_info(self, puuid: str) -> Optional[Dict]:
        """
        Récupère le rank actuel (SoloQ) d'un summoner via PUUID.
        
        Args:
            puuid: PUUID du joueur
        
        Returns:
            {
                "tier": "DIAMOND",
                "rank": "II",
                "lp": 45,
                "wins": 127,
                "losses": 98
            }
            ou None si unranked
        
        Note: Renvoie uniquement la SoloQ (RANKED_SOLO_5x5).
              Si besoin de Flex, adapter le code.
        """
        # Nouvelle API: League-V4 accepte maintenant le PUUID directement
        url = f"https://{self.PLATFORM}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
        
        logger.debug(f"Fetching ranked info for PUUID {puuid[:20]}...")
        result = self._make_request(url)
        
        if not result:
            logger.warning("✗ No ranked data (unranked)")
            return None
        
        # Filtrer pour SoloQ uniquement
        soloq = next((entry for entry in result if entry["queueType"] == "RANKED_SOLO_5x5"), None)
        
        if not soloq:
            logger.warning("✗ Player not ranked in SoloQ")
            return None
        
        ranked_info = {
            "tier": soloq["tier"],
            "rank": soloq.get("rank", "I"),  # Challenger/GM/Master n'ont pas de rank
            "leaguePoints": soloq["leaguePoints"],
            "wins": soloq["wins"],
            "losses": soloq["losses"]
        }
        
        logger.info(f"✓ Ranked: {ranked_info['tier']} {ranked_info['rank']} ({ranked_info['leaguePoints']} LP)")
        return ranked_info
    
    # =========================================================================
    # MATCH-V5: PUUID → Match IDs (Custom Games)
    # =========================================================================
    
    def get_match_ids_by_puuid(
        self,
        puuid: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        queue_id: Optional[int] = None,
        match_type: Optional[str] = None,  # "tourney" pour tournois !
        count: int = 100
    ) -> List[str]:
        """
        Récupère les IDs de matchs d'un joueur.
        
        Args:
            puuid: PUUID du joueur
            start_time: Timestamp Unix début (None = pas de limite)
            end_time: Timestamp Unix fin (None = pas de limite)
            queue_id: 0 = custom, 420 = SoloQ, 440 = Flex (optionnel si match_type défini)
            match_type: "tourney" = tournois uniquement, None = tous
            count: Nombre max de matchs (max 100)
        
        Returns:
            Liste d'IDs de matchs ["EUW1_6234567890", ...]
        
        Exemple:
            >>> # Récupérer matchs de tournoi
            >>> client.get_match_ids_by_puuid(puuid, start, end, match_type="tourney")
            ["EUW1_6234567890", ...]
            
            >>> # Récupérer custom games
            >>> client.get_match_ids_by_puuid(puuid, start, end, queue_id=0)
            ["EUW1_6234567890", ...]
        """
        url = f"https://{self.REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        
        params = {
            "count": count
        }
        
        # Priorité au match_type (tourney) si spécifié
        if match_type:
            params["type"] = match_type
        elif queue_id is not None:
            params["queue"] = queue_id
        
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        type_desc = match_type or f"queue={queue_id}"
        logger.debug(f"Fetching match IDs for PUUID {puuid[:20]} ({type_desc}, count={count})...")
        result = self._make_request(url, params)
        
        if result:
            logger.info(f"✓ Found {len(result)} matches")
            return result
        
        logger.warning("✗ No matches found")
        return []
    
    # =========================================================================
    # MATCH-V5: Match ID → Détails Complets
    # =========================================================================
    
    def get_match_details(self, match_id: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Récupère les détails complets d'un match.
        
        Args:
            match_id: ID du match (ex: "EUW1_6234567890")
            use_cache: Si True, utilise le cache local
        
        Returns:
            {
                "metadata": {
                    "matchId": "EUW1_6234567890",
                    "participants": ["puuid1", "puuid2", ...]
                },
                "info": {
                    "gameCreation": 1609459200000,
                    "gameDuration": 1847,
                    "participants": [...],  # 10 joueurs avec stats complètes
                    "teams": [...]  # 2 équipes avec bans, objectifs
                }
            }
            ou None si non trouvé
        
        Note: Les matchs sont automatiquement mis en cache localement.
        """
        # Vérifier cache
        if use_cache:
            cached = self._get_cached_match(match_id)
            if cached:
                return cached
        
        url = f"https://{self.REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        
        logger.debug(f"Fetching match details for {match_id}...")
        result = self._make_request(url)
        
        if result:
            # Mise en cache
            self._cache_match(match_id, result)
            
            duration = result["info"]["gameDuration"]
            game_mode = result["info"]["gameMode"]
            logger.info(f"✓ Match details retrieved ({duration}s, {game_mode})")
        else:
            logger.warning(f"✗ Match details not found for {match_id}")
        
        return result
    
    # =========================================================================
    # BATCH OPERATIONS
    # =========================================================================
    
    def get_all_match_details(
        self,
        match_ids: List[str],
        use_cache: bool = True,
        progress_callback=None
    ) -> Dict[str, Dict]:
        """
        Récupère les détails de plusieurs matchs en batch.
        
        Args:
            match_ids: Liste d'IDs de matchs
            use_cache: Si True, utilise le cache local
            progress_callback: Fonction(current, total, match_id) pour suivre la progression
        
        Returns:
            {match_id: match_data, ...}
        """
        match_details = {}
        total = len(match_ids)
        
        logger.info(f"Fetching {total} match details...")
        
        for i, match_id in enumerate(match_ids, 1):
            if progress_callback:
                progress_callback(i, total, match_id)
            
            details = self.get_match_details(match_id, use_cache)
            if details:
                match_details[match_id] = details
        
        logger.info(f"✓ Retrieved {len(match_details)}/{total} match details")
        return match_details
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def get_summoner_name_by_puuid(self, puuid: str) -> str:
        """
        Récupère le nom d'invocateur à partir du PUUID (cache ou API).
        
        Args:
            puuid: PUUID du joueur
        
        Returns:
            Nom d'invocateur ou "Unknown"
        """
        # Vérifier cache
        if puuid in self.puuid_map:
            return self.puuid_map[puuid]
        
        # Sinon, appel API
        summoner = self.get_summoner_by_puuid(puuid)
        if summoner:
            return summoner["name"]
        
        return "Unknown"
    
    def get_player_full_info(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """
        Pipeline complet: Riot ID → PUUID → Summoner → Rank.
        
        Args:
            game_name: Nom du joueur (sans #)
            tag_line: Tag (après #)
        
        Returns:
            {
                "game_name": "Player1",
                "tag_line": "EUW",
                "puuid": "...",
                "summoner_id": "...",
                "summoner_name": "Player1",
                "summoner_level": 234,
                "ranked": {
                    "tier": "DIAMOND",
                    "rank": "II",
                    "lp": 45,
                    "wins": 127,
                    "losses": 98
                }
            }
            ou None si joueur non trouvé
        """
        logger.info(f"Fetching full info for {game_name}#{tag_line}...")
        
        # Étape 1: Riot ID → PUUID
        account = self.get_account_by_riot_id(game_name, tag_line)
        if not account:
            return None
        
        puuid = account["puuid"]
        
        # Étape 2: PUUID → Summoner
        summoner = self.get_summoner_by_puuid(puuid)
        if not summoner:
            return None
        
        # Étape 3: PUUID → Rank
        ranked = self.get_ranked_info(puuid)
        
        return {
            "game_name": game_name,
            "tag_line": tag_line,
            "puuid": puuid,
            "summoner_name": summoner.get("gameName", summoner.get("name", game_name)),
            "summoner_level": summoner["summonerLevel"],
            "profile_icon_id": summoner.get("profileIconId"),
            "ranked": ranked  # Peut être None si unranked
        }


# =============================================================================
# EXEMPLE D'UTILISATION
# =============================================================================

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Charger API key
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        print("❌ RIOT_API_KEY not found in environment variables")
        exit(1)
    
    # Initialiser client
    client = RiotAPIClient(api_key)
    
    # Test: Full info d'un joueur
    print("\n" + "="*60)
    print("TEST: get_player_full_info")
    print("="*60)
    
    player_info = client.get_player_full_info("Hide on bush", "KR1")
    if player_info:
        print(f"\n✅ Joueur trouvé:")
        print(f"   Riot ID: {player_info['game_name']}#{player_info['tag_line']}")
        print(f"   Summoner: {player_info['summoner_name']} (lvl {player_info['summoner_level']})")
        if player_info['ranked']:
            r = player_info['ranked']
            print(f"   Rank: {r['tier']} {r['rank']} ({r['lp']} LP)")
            print(f"   Winrate: {r['wins']}W {r['losses']}L")
    else:
        print("❌ Joueur non trouvé")
    
    # Test: Match IDs
    print("\n" + "="*60)
    print("TEST: get_match_ids_by_puuid (custom games)")
    print("="*60)
    
    if player_info:
        from datetime import datetime, timedelta
        
        # Derniers 2 mois
        end = datetime.now()
        start = end - timedelta(days=60)
        
        match_ids = client.get_match_ids_by_puuid(
            player_info['puuid'],
            start_time=int(start.timestamp()),
            end_time=int(end.timestamp()),
            queue_id=0,  # Custom games
            count=10
        )
        
        print(f"\n✅ Trouvé {len(match_ids)} custom games")
        for match_id in match_ids[:3]:
            print(f"   - {match_id}")
