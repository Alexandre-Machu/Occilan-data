# ✅ Implémentation — Core APIs

## 📦 Fichiers créés

### 1. `docs/API_WORKFLOW.md`
**Guide complet des appels API Riot**

Contient :
- ✅ Étape 1: Riot ID → PUUID (Account-V1)
- ✅ Étape 2: PUUID → Summoner Info (Summoner-V4)
- ✅ Étape 3: Summoner ID → Rank/LP (League-V4)
- ✅ Étape 4: PUUID → Match IDs (Match-V5, queue=0 custom games)
- ✅ Étape 5: Match ID → Détails complets (Match-V5)
- ✅ Étape 6: Agrégation champions les plus joués
- ✅ Rate limiting (20 req/s)
- ✅ Retry logic (429, 5xx)
- ✅ Regional routing (europe vs euw1)

### 2. `src/core/riot_client.py` (600+ lignes)
**Client API Riot unifié**

Classes & Méthodes :
```python
class RiotAPIClient:
    # Configuration
    REQUEST_DELAY = 0.05  # 20 req/s
    MAX_RETRIES = 3
    REGION = "europe"     # Account-V1, Match-V5
    PLATFORM = "euw1"     # Summoner-V4, League-V4
    
    # Rate limiting
    _wait_for_rate_limit()
    _make_request(url, params) → Dict
    
    # Cache
    _load_puuid_map() → Dict[puuid, name]
    _save_puuid_map()
    _get_cached_match(match_id) → Dict
    _cache_match(match_id, data)
    
    # Account-V1
    get_account_by_riot_id(game_name, tag_line) → Dict
        # "Player1", "EUW" → {"puuid": "...", ...}
    
    # Summoner-V4
    get_summoner_by_puuid(puuid) → Dict
        # → {"id": "summoner_id", "name": "...", ...}
    
    # League-V4
    get_ranked_info(summoner_id) → Dict
        # → {"tier": "DIAMOND", "rank": "II", "lp": 45, ...}
    
    # Match-V5 (list)
    get_match_ids_by_puuid(
        puuid, 
        start_time,  # Timestamp Unix
        end_time,    # Timestamp Unix
        queue_id=0,  # Custom games
        count=100
    ) → List[str]
        # → ["EUW1_6234567890", ...]
    
    # Match-V5 (details)
    get_match_details(match_id, use_cache=True) → Dict
        # → {"metadata": {...}, "info": {...}}
    
    # Batch
    get_all_match_details(
        match_ids, 
        use_cache=True,
        progress_callback=None
    ) → Dict[match_id, data]
    
    # Helpers
    get_summoner_name_by_puuid(puuid) → str
    get_player_full_info(game_name, tag_line) → Dict
        # Pipeline complet: Riot ID → PUUID → Summoner → Rank
```

**Features :**
- ✅ Rate limiting automatique (50ms entre requêtes)
- ✅ Retry logic avec exponential backoff
- ✅ Gestion 429 (rate limit) avec header `Retry-After`
- ✅ Cache local des matchs (`data/cache/matches/{match_id}.json`)
- ✅ Cache PUUID → summonerName (`data/cache/puuid_map.json`)
- ✅ Logging détaillé (debug, info, warning, error)
- ✅ Timeouts (10s)
- ✅ Regional routing correct (europe vs euw1)

**Exemple d'utilisation :**
```python
from src.core.riot_client import RiotAPIClient

# Init
client = RiotAPIClient(api_key="RGAPI-...")

# Pipeline complet
player = client.get_player_full_info("Hide on bush", "KR1")
# → {
#     "game_name": "Hide on bush",
#     "tag_line": "KR1",
#     "puuid": "...",
#     "summoner_id": "...",
#     "summoner_name": "Hide on bush",
#     "summoner_level": 520,
#     "ranked": {
#         "tier": "CHALLENGER",
#         "rank": "I",
#         "lp": 1234,
#         "wins": 450,
#         "losses": 321
#     }
# }

# Récupérer matchs custom (tournoi)
match_ids = client.get_match_ids_by_puuid(
    player["puuid"],
    start_time=int(datetime(2024, 1, 1).timestamp()),
    end_time=int(datetime(2024, 3, 1).timestamp()),
    queue_id=0  # Custom games
)

# Détails d'un match (avec cache)
match = client.get_match_details("EUW1_6234567890")
# → {"metadata": {...}, "info": {"participants": [...], ...}}
```

### 3. `src/parsers/opgg_parser.py` (230+ lignes)
**Parser de liens OP.GG**

Classes & Méthodes :
```python
class OPGGParser:
    ROLES = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
    
    # Parse URL
    @staticmethod
    parse_multisearch_url(opgg_link) → List[Tuple[str, str]]
        # Input: "https://op.gg/multisearch/euw?summoners=Player1-EUW,Player2-EUW"
        # Output: [("Player1", "EUW"), ("Player2", "EUW")]
    
    # Parse nom individuel
    @staticmethod
    _parse_summoner_name(summoner_name) → Tuple[str, str]
        # Supporte: "Player1-EUW", "Player1#EUW", "Player One-EUW"
        # Output: ("Player1", "EUW")
    
    # Parse équipe complète
    @staticmethod
    parse_team_opgg(team_name, opgg_link, roles=None) → Dict
        # Output: {
        #     "team_name": "KCDQ",
        #     "opgg_link": "https://...",
        #     "players": [
        #         {"role": "TOP", "game_name": "Player1", "tag_line": "EUW"},
        #         {"role": "JUNGLE", "game_name": "Player2", "tag_line": "EUW"},
        #         ...
        #     ]
        # }
    
    # Validation
    @staticmethod
    validate_opgg_link(opgg_link) → bool
```

**Features :**
- ✅ Parse liens OP.GG multisearch
- ✅ Supporte séparateurs `-` et `#`
- ✅ Gère noms avec espaces ("Player One-EUW")
- ✅ Décodage URL (%2C → ,)
- ✅ Validation format
- ✅ Assignment automatique des rôles
- ✅ Gestion erreurs avec logs

**Exemple d'utilisation :**
```python
from src.parsers.opgg_parser import OPGGParser

# Parse URL
link = "https://op.gg/multisearch/euw?summoners=P1-EUW,P2-EUW,P3-EUW,P4-EUW,P5-EUW"
riot_ids = OPGGParser.parse_multisearch_url(link)
# → [("P1", "EUW"), ("P2", "EUW"), ...]

# Parse équipe complète
team = OPGGParser.parse_team_opgg("KCDQ", link)
# → {
#     "team_name": "KCDQ",
#     "players": [
#         {"role": "TOP", "game_name": "P1", "tag_line": "EUW"},
#         ...
#     ]
# }

# Validation
is_valid = OPGGParser.validate_opgg_link(link)  # → True
```

---

## 🧪 Tests inclus

### RiotAPIClient
```bash
python src/core/riot_client.py
```

Tests :
- ✅ `get_player_full_info("Hide on bush", "KR1")`
- ✅ `get_match_ids_by_puuid` (custom games derniers 60 jours)
- ✅ Affichage PUUID, rank, winrate

### OPGGParser
```bash
python src/parsers/opgg_parser.py
```

Tests :
- ✅ Parse lien simple
- ✅ Parse lien encodé (%2C)
- ✅ Parse équipe avec rôles
- ✅ Validation liens
- ✅ Noms avec espaces

---

## 📊 Architecture des données

### Cache local
```
data/
├── cache/
│   ├── matches/
│   │   ├── EUW1_6234567890.json  # Détails match
│   │   └── EUW1_6234567891.json
│   └── puuid_map.json  # {puuid: summonerName}
```

### Format match_details.json (Match-V5)
```json
{
  "metadata": {
    "matchId": "EUW1_6234567890",
    "participants": ["puuid1", "puuid2", ...]
  },
  "info": {
    "gameCreation": 1609459200000,
    "gameDuration": 1847,
    "gameMode": "CLASSIC",
    "queueId": 0,
    "participants": [
      {
        "puuid": "abc123...",
        "summonerName": "Player1",
        "championId": 157,
        "championName": "Yasuo",
        "teamPosition": "MIDDLE",
        "kills": 7,
        "deaths": 3,
        "assists": 12,
        "totalMinionsKilled": 245,
        "goldEarned": 14250,
        "totalDamageDealtToChampions": 28500,
        "visionScore": 42,
        "win": true
      }
      // ... 9 autres
    ],
    "teams": [
      {
        "teamId": 100,
        "win": true,
        "bans": [...],
        "objectives": {...}
      }
    ]
  }
}
```

---

## 🔄 Pipeline complet

```
CSV Upload (team_name, opgg_link)
         ↓
   [OPGGParser]
    Parse OP.GG → Extract gameName#tagLine
         ↓
   [RiotAPIClient]
    Account-V1: Riot ID → PUUID
         ↓
    Summoner-V4: PUUID → summoner_id
         ↓
    League-V4: summoner_id → rank/LP/wins/losses
         ↓
    Match-V5: PUUID → match IDs (queue=0, dates tournoi)
         ↓
    Match-V5: match ID → détails complets (avec cache)
         ↓
   [stats_calculator.py - TODO]
    Agrégation: KDA, CS/min, champions, records
         ↓
    general_stats.json
```

---

## 🚀 Prochaines étapes

1. ✅ **core/riot_client.py** → TERMINÉ
2. ✅ **parsers/opgg_parser.py** → TERMINÉ
3. 🔄 **core/data_manager.py** → EN COURS
4. ⏳ **core/stats_calculator.py** → À faire
5. ⏳ **pipeline/edition_processor.py** → À faire
6. ⏳ **Streamlit interface** → À faire

---

## 💡 Notes importantes

### Regional Routing
- **Account-V1, Match-V5** : utiliser `region` (europe/americas/asia/sea)
- **Summoner-V4, League-V4** : utiliser `platform` (euw1/na1/kr/etc.)

### Rate Limiting
- Limite : **20 requêtes/seconde** (application rate limit)
- Implémentation : 50ms delay entre chaque requête
- Gestion 429 avec header `Retry-After`

### Cache
- Matchs : **partagés entre éditions** (data/cache/matches/)
- PUUID map : **global** (data/cache/puuid_map.json)
- Évite requêtes inutiles et respecte rate limit

### Queue IDs
- `0` : Custom games (tournois)
- `420` : Ranked Solo/Duo
- `440` : Ranked Flex

### Champions les plus joués
- **Méthode recommandée** : Agrégation Match-V5 (historique récent)
- **Méthode alternative** : Champion-Mastery-V4 (historique global, moins pertinent)
- OP.GG utilise Match-V5 pour "Most Played (Season)"

### 4. `src/core/data_manager.py` (500+ lignes) ✅
**Gestionnaire de données JSON par édition**

Classes & Méthodes :
```python
class EditionDataManager:
    EDITION_FILES = [
        "config.json",
        "teams.json",
        "teams_with_puuid.json",
        "tournament_matches.json",
        "match_details.json",
        "general_stats.json"
    ]
    
    # Initialisation
    __init__(edition_number, base_path="data/editions")
    initialize_edition(name, year, start_date, end_date)
    exists() → bool
    
    # Generic operations
    _read_json(filename) → Dict
    _write_json(filename, data, backup=True)
    _backup_file(filename)  # Auto-backup avec timestamp
    
    # Config
    load_config() → Dict
    save_config(config)
    update_status(status)  # pending, processing, completed, error
    
    # Teams (sans PUUID)
    load_teams() → Dict[team_name, team_data]
    save_teams(teams)
    add_team(team_name, team_data)
    
    # Teams with PUUID (+ elo)
    load_teams_with_puuid() → Dict
    save_teams_with_puuid(teams)
    
    # Tournament matches
    load_tournament_matches() → Dict[team_name, List[match_ids]]
    save_tournament_matches(matches)
    add_team_matches(team_name, match_ids)
    
    # Match details
    load_match_details() → Dict[match_id, match_data]
    save_match_details(details)
    add_match_detail(match_id, match_data)
    get_match_detail(match_id) → Dict
    
    # General stats
    load_general_stats() → Dict
    save_general_stats(stats)
    
    # Bulk operations
    get_all_match_ids() → List[str]
    get_teams_count() → int
    get_matches_count() → int
    get_summary() → Dict
    
    # Cleanup
    clear_all_data()
    export_to_dict() → Dict  # Backup complet


class MultiEditionManager:
    """Gestionnaire multi-éditions"""
    
    __init__(base_path="data/editions")
    get_edition_manager(edition_number) → EditionDataManager
    list_editions() → List[int]
    get_all_summaries() → List[Dict]
```

**Features :**
- ✅ CRUD complet pour tous les fichiers JSON
- ✅ Auto-création structure `data/editions/edition_X/`
- ✅ Backups automatiques avec timestamp avant écrasement
- ✅ Validation existence fichiers
- ✅ Résumés par édition (teams, matches, players count)
- ✅ Gestion multi-éditions
- ✅ Export complet pour backup
- ✅ Logging détaillé

**Exemple d'utilisation :**
```python
from src.core.data_manager import EditionDataManager

# Initialiser édition
manager = EditionDataManager(7)
manager.initialize_edition(
    edition_name="OcciLan Stats 7",
    year=2024,
    start_date="2024-01-15",
    end_date="2024-03-20"
)

# Ajouter équipe
team_data = {
    "players": [
        {"role": "TOP", "game_name": "Player1", "tag_line": "EUW"},
        # ... 4 autres
    ],
    "opgg_link": "https://..."
}
manager.add_team("KCDQ", team_data)

# Charger équipes
teams = manager.load_teams()

# Résumé
summary = manager.get_summary()
# → {"teams_count": 12, "matches_count": 45, ...}
```

---

### 5. `scripts/test_core.py` ✅
**Script de validation des composants**

Tests automatisés :
- ✅ OPGGParser (parse liens, équipes, validation)
- ✅ RiotAPIClient (init, get_player_full_info - si API key configurée)
- ✅ EditionDataManager (CRUD complet, cleanup)

**Résultat des tests :**
```
✅ PASS OPGGParser
✅ PASS RiotAPIClient
✅ PASS EditionDataManager

🎉 Tous les tests sont passés !
```

---

## 📊 Structure des données créée

```
data/
├── cache/                      # Cache global partagé
│   ├── matches/               # Détails matchs (partagés)
│   │   └── EUW1_*.json
│   └── puuid_map.json         # PUUID → summonerName
│
└── editions/                   # Données par édition
    ├── edition_4/
    │   ├── config.json
    │   ├── teams.json
    │   ├── teams_with_puuid.json
    │   ├── tournament_matches.json
    │   ├── match_details.json
    │   └── general_stats.json
    ├── edition_5/
    ├── edition_6/
    └── edition_7/
```

---

**Status : 3/6 composants terminés** ✅✅✅⏳⏳⏳
