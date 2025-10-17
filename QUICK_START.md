# 🚀 Quick Start — Tests & Validation

## ✅ Composants implémentés

### 1. **OPGGParser** — Parser liens OP.GG
Parse les liens multisearch et extrait les Riot IDs avec assignation des rôles.

### 2. **RiotAPIClient** — Client API Riot unifié
Gère tous les appels Riot API (Account-V1, Summoner-V4, League-V4, Match-V5) avec rate limiting et cache.

### 3. **EditionDataManager** — Gestion données JSON
CRUD complet pour gérer les données d'une édition (teams, matches, stats).

---

## 🧪 Tester les composants

### 1. Configuration

**Créer le fichier `.env` à la racine :**
```bash
# Copier depuis .env.example
cp .env.example .env

# Éditer et ajouter votre clé API Riot
RIOT_API_KEY=RGAPI-votre-cle-ici
```

**Obtenir une clé API Riot :**
👉 https://developer.riotgames.com/

### 2. Lancer les tests

```bash
# Tests automatiques de tous les composants
python scripts/test_core.py
```

**Résultat attendu :**
```
✅ PASS OPGGParser
✅ PASS RiotAPIClient
✅ PASS EditionDataManager

🎉 Tous les tests sont passés !
```

---

## 📖 Exemples d'utilisation

### OPGGParser

```python
from src.parsers.opgg_parser import OPGGParser

# Parse lien OP.GG
link = "https://op.gg/multisearch/euw?summoners=P1-EUW,P2-EUW,P3-EUW,P4-EUW,P5-EUW"
riot_ids = OPGGParser.parse_multisearch_url(link)
# → [("P1", "EUW"), ("P2", "EUW"), ...]

# Parse équipe complète avec rôles
team = OPGGParser.parse_team_opgg("KCDQ", link)
# → {"team_name": "KCDQ", "players": [{"role": "TOP", ...}, ...]}
```

### RiotAPIClient

```python
from src.core.riot_client import RiotAPIClient
import os

# Initialiser
client = RiotAPIClient(os.getenv("RIOT_API_KEY"))

# Pipeline complet: Riot ID → PUUID → Summoner → Rank
player = client.get_player_full_info("Faker", "KR1")
# → {"puuid": "...", "summoner_name": "...", "ranked": {...}}

# Récupérer matchs custom (tournoi)
from datetime import datetime
match_ids = client.get_match_ids_by_puuid(
    player["puuid"],
    start_time=int(datetime(2024, 1, 1).timestamp()),
    end_time=int(datetime(2024, 3, 1).timestamp()),
    queue_id=0  # Custom games
)

# Détails d'un match (avec cache)
match = client.get_match_details("EUW1_6234567890")
```

### EditionDataManager

```python
from src.core.data_manager import EditionDataManager

# Créer/charger édition
manager = EditionDataManager(7)

# Initialiser nouvelle édition
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
        {"role": "JUNGLE", "game_name": "Player2", "tag_line": "EUW"},
        {"role": "MID", "game_name": "Player3", "tag_line": "EUW"},
        {"role": "ADC", "game_name": "Player4", "tag_line": "EUW"},
        {"role": "SUPPORT", "game_name": "Player5", "tag_line": "EUW"}
    ],
    "opgg_link": "https://op.gg/multisearch/euw?summoners=..."
}
manager.add_team("KCDQ", team_data)

# Charger données
teams = manager.load_teams()
config = manager.load_config()

# Résumé
summary = manager.get_summary()
# → {"teams_count": 12, "matches_count": 45, "players_count": 60, ...}
```

---

## 🔄 Workflow complet

```python
from src.parsers.opgg_parser import OPGGParser
from src.core.riot_client import RiotAPIClient
from src.core.data_manager import EditionDataManager
import os

# 1. Initialiser
client = RiotAPIClient(os.getenv("RIOT_API_KEY"))
manager = EditionDataManager(7)

# 2. Parser OP.GG
link = "https://op.gg/multisearch/euw?summoners=..."
team = OPGGParser.parse_team_opgg("KCDQ", link)

# 3. Sauvegarder équipe
manager.add_team(team["team_name"], {
    "players": team["players"],
    "opgg_link": team["opgg_link"]
})

# 4. Fetch PUUID + Rank pour chaque joueur
teams_with_puuid = {}
for team_name, team_data in manager.load_teams().items():
    enriched_players = []
    
    for player in team_data["players"]:
        # API calls
        info = client.get_player_full_info(
            player["game_name"], 
            player["tag_line"]
        )
        
        # Enrichir
        enriched_players.append({
            **player,
            "puuid": info["puuid"],
            "summoner_id": info["summoner_id"],
            "summoner_name": info["summoner_name"],
            **info.get("ranked", {})
        })
    
    teams_with_puuid[team_name] = {"players": enriched_players}

# 5. Sauvegarder
manager.save_teams_with_puuid(teams_with_puuid)

# 6. Fetch matchs custom
from datetime import datetime
start = int(datetime(2024, 1, 15).timestamp())
end = int(datetime(2024, 3, 20).timestamp())

for team_name, team_data in teams_with_puuid.items():
    first_player_puuid = team_data["players"][0]["puuid"]
    
    match_ids = client.get_match_ids_by_puuid(
        first_player_puuid,
        start_time=start,
        end_time=end,
        queue_id=0
    )
    
    manager.add_team_matches(team_name, match_ids)

# 7. Fetch détails
all_match_ids = manager.get_all_match_ids()
match_details = client.get_all_match_details(all_match_ids)

for match_id, details in match_details.items():
    manager.add_match_detail(match_id, details)

print("✅ Pipeline complet terminé !")
```

---

## 📁 Structure générée

Après exécution du workflow :

```
data/
├── cache/
│   ├── matches/
│   │   └── EUW1_*.json        # Détails matchs (cache global)
│   └── puuid_map.json          # Mapping PUUID → name
│
└── editions/
    └── edition_7/
        ├── config.json                 # Config édition
        ├── teams.json                  # Équipes + OP.GG links
        ├── teams_with_puuid.json       # + PUUID + elo
        ├── tournament_matches.json     # {team: [match_ids]}
        ├── match_details.json          # Détails complets
        └── general_stats.json          # Stats (à calculer)
```

---

## 🐛 Debugging

### Logs
Tous les composants loggent en détail :

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Voir tous les détails
```

### Cache
Vider le cache si nécessaire :

```bash
rm -rf data/cache/matches/*
rm data/cache/puuid_map.json
```

### Tests individuels
Tester chaque composant séparément :

```bash
# OPGGParser
python src/parsers/opgg_parser.py

# RiotAPIClient
python src/core/riot_client.py

# EditionDataManager
python src/core/data_manager.py
```

---

## 📚 Documentation complète

- **Architecture finale** → `docs/ARCHITECTURE_FINAL.md`
- **Workflow API Riot** → `docs/API_WORKFLOW.md`
- **Status implémentation** → `docs/IMPLEMENTATION_STATUS.md`

---

## 🚀 Prochaines étapes

1. ⏳ **stats_calculator.py** — Calculs stats (KDA, CS/min, records)
2. ⏳ **edition_processor.py** — Pipeline orchestration 6 étapes
3. ⏳ **Streamlit app** — Interface multi-pages

---

**Status : 3/6 composants ✅** | **Tests : 100% pass 🎉**
