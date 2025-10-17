# 🏗️ Architecture Finale — OcciLan Stats Hub
## Basée sur l'analyse des 3 projets existants

---

## 📊 Analyse des projets existants

### 🎯 OccilanStats-6 (Le plus complet)

**Structure réelle :**
```python
# main.py - Pipeline linéaire en 6 étapes
1. load_teams_from_excel(excel) → teams.json
2. fetch_puuid(teams) → teams_with_puuid.json  
3. fetch_tournament_matches(teams_with_puuid) → tournament_matches.json
4. fetch_match_details(match_ids) → match_details.json
5. get_stats(match_details, teams) → general_stats.json
6. create_excel(stats) → OccilanStats.xlsx
```

**Points forts à garder :**
- ✅ Pipeline clair et séquentiel
- ✅ Sauvegarde intermédiaire à chaque étape
- ✅ Calculs stats exhaustifs (records, joueurs, équipes, champions)
- ✅ Format JSON déjà bien structuré

**À adapter :**
- ❌ Excel input → CSV simple (team, opgg_link)
- ❌ Excel output → Streamlit interface
- ❌ Mono-édition → Multi-édition

---

### 🌐 Occilan-data-scrapper (Interface Streamlit)

**Structure réelle :**
```python
# src/app.py - Streamlit avec sélecteur édition
- Sidebar: selectbox edition (4,5,6,7)
- Parse CSV avec gestion alternates (A / B)
- Système de persistence: data/tournament_matches.json avec clés par édition
- Admin auth: OCCILAN_ADMIN_SECRET
- Cache matches: data/cache/matches/{match_id}.json
- Processed files: data/processed/match_stats_edition{X}_*.json
```

**Points forts à garder :**
- ✅ Sélecteur d'édition dans sidebar
- ✅ Structure JSON par édition: `{"edition_4": [...], "edition_5": [...]}`
- ✅ Système d'auth admin avec token
- ✅ Cache local des matchs
- ✅ Resolve player PUUID → SummonerName

**À adapter :**
- ❌ Code trop complexe avec trop de fallbacks
- ❌ Structure de fichiers pas claire

---

### 🎨 SC-Esport-Stats (Visualisations)

**Structure réelle :**
```python
# Surtout du Flask + templates HTML
- Formatage champion icons
- Graphiques Plotly
- Display player stats par rôle
```

**Points forts à garder :**
- ✅ Formatage champion names/icons
- ✅ Visualisations Plotly

---

## 🎯 Architecture proposée (synthèse)

### Structure de dossiers FINALE

```
Occilan-data/
├── src/
│   ├── core/                          # Code métier principal
│   │   ├── __init__.py
│   │   ├── riot_client.py             # Client Riot API unifié
│   │   ├── data_manager.py            # Gestion JSON multi-édition
│   │   └── stats_calculator.py        # Calculs statistiques
│   │
│   ├── parsers/                       # Parseurs entrées
│   │   ├── __init__.py
│   │   ├── csv_parser.py              # Parse CSV (team, opgg_link)
│   │   └── opgg_parser.py             # Extract Riot IDs from OP.GG
│   │
│   ├── pipeline/                      # Pipeline de traitement
│   │   ├── __init__.py
│   │   ├── edition_processor.py       # Orchestration complète
│   │   └── steps.py                   # Chaque étape du pipeline
│   │
│   ├── streamlit_app/                 # Interface Streamlit
│   │   ├── app.py                     # Home + sidebar édition
│   │   ├── pages/
│   │   │   ├── 1_📊_Overview.py
│   │   │   ├── 2_👥_Teams.py
│   │   │   ├── 3_🏆_Players.py
│   │   │   ├── 4_⚔️_Matches.py
│   │   │   └── 5_🔧_Admin.py
│   │   └── components/
│   │       ├── charts.py              # Graphiques Plotly
│   │       ├── tables.py              # Tableaux
│   │       └── utils.py               # Helpers UI
│   │
│   └── utils/                         # Utilitaires
│       ├── __init__.py
│       ├── constants.py               # Constantes
│       ├── formatters.py              # Format affichage
│       └── logger.py                  # Logging
│
├── data/
│   ├── editions/                      # Données par édition
│   │   ├── edition_4/
│   │   │   ├── config.json
│   │   │   ├── teams.json
│   │   │   ├── teams_with_puuid.json
│   │   │   ├── tournament_matches.json
│   │   │   ├── match_details.json
│   │   │   └── general_stats.json
│   │   ├── edition_5/
│   │   ├── edition_6/
│   │   └── edition_7/
│   │
│   ├── cache/                         # Cache partagé
│   │   ├── matches/                   # Cache matchs Riot API
│   │   └── puuid_map.json             # Cache PUUID → Name
│   │
│   └── raw/                           # CSV uploadés (backup)
│       └── edition_X_teams.csv
│
├── config/
│   └── config.yaml                    # Config globale
│
├── .env                               # Variables d'environnement
└── requirements.txt
```

---

## 🔄 Pipeline de traitement (inspiré d'OccilanStats-6)

### Workflow complet

```python
# pipeline/edition_processor.py

class EditionProcessor:
    """
    Orchestrateur principal du traitement d'une édition
    Basé sur le workflow d'OccilanStats-6
    """
    
    def process_edition(edition_number, csv_file, config):
        """
        Pipeline complet en 6 étapes
        """
        
        # ÉTAPE 1: Parse CSV et OP.GG
        print("Étape 1: Parsing CSV et extraction OP.GG...")
        teams = parse_csv_and_opgg(csv_file)
        # → {team_name: {players: [{game_name, tag_line, role}], opgg_link}}
        save_json(teams, f"editions/edition_{edition_number}/teams.json")
        
        # ÉTAPE 2: Fetch PUUIDs
        print("Étape 2: Récupération des PUUIDs...")
        teams_with_puuid = fetch_puuids(teams, riot_client)
        # → Ajoute puuid, summoner_id à chaque joueur
        save_json(teams_with_puuid, f"editions/edition_{edition_number}/teams_with_puuid.json")
        
        # ÉTAPE 3: Fetch ranked elo
        print("Étape 3: Récupération des elos...")
        teams_with_elo = fetch_ranked_info(teams_with_puuid, riot_client)
        # → Ajoute ranked_tier, ranked_rank, ranked_lp
        save_json(teams_with_elo, f"editions/edition_{edition_number}/teams_with_puuid.json")  # overwrite
        
        # ÉTAPE 4: Fetch tournament matches
        print("Étape 4: Récupération des match IDs...")
        match_ids = fetch_tournament_matches(
            teams_with_elo, 
            start_date=config['start_date'],
            end_date=config['end_date']
        )
        # → {team_name: [match_ids]}
        save_json(match_ids, f"editions/edition_{edition_number}/tournament_matches.json")
        
        # ÉTAPE 5: Fetch match details
        print("Étape 5: Récupération des détails des matchs...")
        match_details = fetch_match_details(match_ids, riot_client)
        # → {match_id: {full match data}}
        save_json(match_details, f"editions/edition_{edition_number}/match_details.json")
        
        # ÉTAPE 6: Calculate stats
        print("Étape 6: Calcul des statistiques...")
        stats = calculate_stats(match_details, teams_with_elo)
        # → {players: {...}, teams: {...}, records: {...}, champions: {...}}
        save_json(stats, f"editions/edition_{edition_number}/general_stats.json")
        
        print("✅ Traitement terminé!")
        return stats
```

---

## 📁 Formats JSON (basés sur l'existant)

### 1. `config.json`
```json
{
  "edition_number": 6,
  "name": "OcciLan #6",
  "year": 2024,
  "start_date": "2024-11-15",
  "end_date": "2024-11-17",
  "num_teams": 16
}
```

### 2. `teams.json` (après parse CSV + OP.GG)
```json
{
  "KCDQ": {
    "players": [
      {
        "role": "TOP",
        "game_name": "Player1",
        "tag_line": "EUW"
      },
      // ... 4 autres
    ],
    "opgg_link": "https://op.gg/multisearch/euw?summoners=..."
  },
  // ... autres équipes
}
```

### 3. `teams_with_puuid.json` (après fetch PUUID + elo)
```json
{
  "KCDQ": {
    "players": [
      {
        "role": "TOP",
        "game_name": "Player1",
        "tag_line": "EUW",
        "puuid": "abc123...",
        "summoner_id": "xyz789...",
        "ranked_tier": "DIAMOND",
        "ranked_rank": "II",
        "ranked_lp": 45
      },
      // ... 4 autres
    ],
    "opgg_link": "https://op.gg/multisearch/euw?summoners=..."
  }
}
```

### 4. `tournament_matches.json`
```json
{
  "KCDQ": [
    "EUW1_7381594783",
    "EUW1_7381612199",
    // ... autres match IDs
  ],
  // ... autres équipes
}
```

### 5. `match_details.json`
```json
{
  "EUW1_7381594783": {
    "metadata": {
      "matchId": "EUW1_7381594783",
      "participants": ["puuid1", "puuid2", ...]
    },
    "info": {
      "gameCreation": 1700000000000,
      "gameDuration": 2570,
      "gameMode": "CLASSIC",
      "participants": [
        {
          "puuid": "abc123...",
          "summonerName": "Player1",
          "championName": "Ahri",
          "teamId": 100,
          "kills": 5,
          "deaths": 2,
          "assists": 10,
          // ... toutes les stats Riot
        },
        // ... 9 autres
      ],
      "teams": [
        {"teamId": 100, "win": true},
        {"teamId": 200, "win": false}
      ]
    }
  },
  // ... autres matchs
}
```

### 6. `general_stats.json` (format OccilanStats-6)
```json
{
  "longest_game": {
    "detail": "EUW1_7381594783",
    "value": 2570.0,
    "teams": "KCDQ vs La bande du PMU",
    "formatted_duration": "42:50"
  },
  "shortest_game": {...},
  "most_kills_in_game": {...},
  "highest_vision_game": {...},
  
  "player_stats": {
    "Player1#EUW": {
      "team": "KCDQ",
      "total_kills": 52,
      "total_deaths": 21,
      "total_assists": 85,
      "games_played": 12,
      "wins": 9,
      "avg_kills": 4.33,
      "avg_deaths": 1.75,
      "avg_assists": 7.08,
      "kda": 6.52,
      "total_cs": 2340,
      "cs_per_min": 8.2,
      "total_vision_score": 480,
      "vision_score_per_min": 1.68,
      "champions_played": ["Ahri", "Syndra", "Orianna"],
      "most_played": "Ahri"
    },
    // ... autres joueurs
  },
  
  "team_stats": {
    "KCDQ": {
      "games_played": 12,
      "wins": 9,
      "losses": 3,
      "winrate": 0.75,
      "avg_game_duration": 1850,
      "total_kills": 218,
      "avg_kills_per_game": 18.17
    },
    // ... autres équipes
  },
  
  "champion_stats": {
    "picks": {"Ahri": 15, "Lee Sin": 12, ...},
    "bans": {"Zed": 20, "Yasuo": 18, ...},
    "wins": {"Ahri": {"wins": 10, "games": 15}, ...}
  }
}
```

---

## 🔧 Composants principaux

### 1. `core/riot_client.py` (merge des 3 projets)

```python
class RiotClient:
    """Client Riot API unifié avec cache et rate limiting"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache_dir = Path("data/cache/matches")
        self.puuid_cache = self._load_puuid_cache()
        
    # De OccilanStats-6
    def get_account_by_riot_id(self, game_name, tag_line):
        """Account-V1: Riot ID → PUUID"""
        
    def get_summoner_by_puuid(self, puuid):
        """Summoner-V4: PUUID → summoner_id + ranked info"""
        
    def get_match_ids_by_puuid(self, puuid, start_time, end_time, count=100):
        """Match-V5: Get match IDs"""
        
    def get_match_details(self, match_id):
        """Match-V5: Get full match data (avec cache)"""
        
    # De Occilan-data-scrapper
    def _cache_get(self, match_id):
        """Récup match depuis cache local"""
        
    def _cache_set(self, match_id, data):
        """Sauvegarder match en cache"""
        
    def _rate_limit_wait(self):
        """Rate limiting: 20 req/s"""
```

### 2. `core/data_manager.py`

```python
class EditionDataManager:
    """Gestion des données JSON par édition"""
    
    def __init__(self, edition_number: int):
        self.edition_number = edition_number
        self.base_path = Path(f"data/editions/edition_{edition_number}")
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def load_teams(self) -> dict:
        """Charger teams.json ou teams_with_puuid.json"""
        
    def save_teams(self, data: dict, with_puuid: bool = False):
        """Sauvegarder teams"""
        
    def load_matches(self) -> dict:
        """Charger tournament_matches.json"""
        
    def save_matches(self, data: dict):
        """Sauvegarder match IDs"""
        
    def load_match_details(self) -> dict:
        """Charger match_details.json"""
        
    def save_match_details(self, data: dict):
        """Sauvegarder détails matchs"""
        
    def load_stats(self) -> dict:
        """Charger general_stats.json"""
        
    def save_stats(self, data: dict):
        """Sauvegarder stats calculées"""
        
    def load_config(self) -> dict:
        """Charger config.json"""
        
    def save_config(self, data: dict):
        """Sauvegarder config édition"""
```

### 3. `core/stats_calculator.py` (de OccilanStats-6/get_stats.py)

```python
class StatsCalculator:
    """Calculs statistiques (inspiré d'OccilanStats-6)"""
    
    def calculate_all_stats(self, match_details: dict, teams: dict) -> dict:
        """Calcul complet des stats"""
        stats = {
            "player_stats": {},
            "team_stats": {},
            "records": {},
            "champion_stats": {"picks": {}, "bans": {}, "wins": {}}
        }
        
        for match_id, match_data in match_details.items():
            self._process_match(match_id, match_data, teams, stats)
        
        self._finalize_stats(stats)
        return stats
    
    def _process_match(self, match_id, match_data, teams, stats):
        """Traiter un match (records, player stats, etc.)"""
        
    def _finalize_stats(self, stats):
        """Calculs finaux (moyennes, KDA, etc.)"""
```

### 4. `pipeline/edition_processor.py`

```python
class EditionProcessor:
    """Orchestration du pipeline complet"""
    
    def __init__(self, edition_number: int):
        self.edition_number = edition_number
        self.data_manager = EditionDataManager(edition_number)
        self.riot_client = RiotClient(os.getenv("RIOT_API_KEY"))
        self.stats_calculator = StatsCalculator()
    
    def process_new_edition(
        self, 
        csv_file: Path, 
        edition_config: dict,
        progress_callback=None
    ):
        """
        Pipeline complet (6 étapes)
        progress_callback: fonction pour afficher progression dans Streamlit
        """
        
        # Étape 1-6 comme dans le diagramme ci-dessus
        ...
```

---

## 🎨 Interface Streamlit

### Structure pages (inspirée d'Occilan-data-scrapper)

```python
# app.py

import streamlit as st
from src.core.data_manager import EditionDataManager
import yaml

# Config
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# Sidebar - Sélecteur édition
st.sidebar.title("🎮 OcciLan Stats")
available_editions = [e['number'] for e in config['editions'] if e['enabled']]
selected_edition = st.sidebar.selectbox(
    "Édition",
    available_editions,
    index=available_editions.index(config['app']['default_edition'])
)

# Charger données de l'édition
@st.cache_data
def load_edition_data(edition_number):
    dm = EditionDataManager(edition_number)
    return {
        'config': dm.load_config(),
        'teams': dm.load_teams(),
        'stats': dm.load_stats()
    }

data = load_edition_data(selected_edition)

# Affichage
st.title(f"{data['config']['name']} - {data['config']['year']}")

# Metrics rapides
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Équipes", len(data['teams']))
with col2:
    total_games = sum(p['games_played'] for p in data['stats']['player_stats'].values())
    st.metric("Matchs", total_games // 10)  # 10 joueurs par match
with col3:
    st.metric("Joueurs", len(data['stats']['player_stats']))

# Navigation
st.markdown("### 📊 Parcourir")
st.page_link("pages/1_📊_Overview.py", label="Overview")
st.page_link("pages/2_👥_Teams.py", label="Teams")
# ...
```

### Page Admin (inspirée d'Occilan-data-scrapper)

```python
# pages/5_🔧_Admin.py

import streamlit as st
import os
from src.pipeline.edition_processor import EditionProcessor

# Auth
admin_password = os.getenv("ADMIN_PASSWORD")
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if not st.session_state.is_admin:
    password = st.text_input("Mot de passe admin", type="password")
    if st.button("Se connecter"):
        if password == admin_password:
            st.session_state.is_admin = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# Interface admin
st.title("🔧 Administration")

# Nouvelle édition
with st.expander("➕ Nouvelle édition", expanded=True):
    edition_num = st.number_input("Numéro édition", min_value=1, value=8)
    edition_name = st.text_input("Nom", value=f"OcciLan #{edition_num}")
    edition_year = st.number_input("Année", min_value=2020, value=2025)
    start_date = st.date_input("Date début")
    end_date = st.date_input("Date fin")
    
    csv_file = st.file_uploader("CSV (team_name, opgg_link)", type="csv")
    
    if st.button("▶️ Traiter l'édition"):
        if csv_file:
            # Pipeline complet
            processor = EditionProcessor(edition_num)
            
            config = {
                "edition_number": edition_num,
                "name": edition_name,
                "year": edition_year,
                "start_date": str(start_date),
                "end_date": str(end_date)
            }
            
            # Progress bar
            progress = st.progress(0)
            status = st.empty()
            
            def progress_callback(step, total, message):
                progress.progress(step / total)
                status.text(message)
            
            try:
                processor.process_new_edition(
                    csv_file, 
                    config, 
                    progress_callback
                )
                st.success("✅ Édition traitée avec succès!")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
```

---

## 🎯 Plan d'implémentation par priorité

### Phase 1: Core (2-3 jours)
1. ✅ `core/riot_client.py` - Merger le meilleur des 3 projets
2. ✅ `core/data_manager.py` - Gestion JSON multi-édition
3. ✅ `parsers/csv_parser.py` + `opgg_parser.py`
4. ✅ `core/stats_calculator.py` - Adapter `get_stats.py`

### Phase 2: Pipeline (1-2 jours)
5. ✅ `pipeline/edition_processor.py` - Orchestration 6 étapes
6. ✅ Tester sur édition 6 existante

### Phase 3: Streamlit (2-3 jours)
7. ✅ `app.py` - Home + sélecteur édition
8. ✅ Pages Overview/Teams/Players/Matches
9. ✅ Page Admin avec upload + processing
10. ✅ Components (charts, tables)

### Phase 4: Migration (1 jour)
11. ✅ Migrer éditions 4, 5, 6 dans nouvelle structure
12. ✅ Tests complets

---

**Cette architecture reprend VRAIMENT ce qui existe et fonctionne. On garde les bonnes idées, on simplifie ce qui est trop complexe, et on unifie le tout.**

**Qu'en pensez-vous ? Voulez-vous que je commence l'implémentation ?** 🚀
