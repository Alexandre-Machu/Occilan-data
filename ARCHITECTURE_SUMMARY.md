# 📋 RÉSUMÉ — Architecture OcciLan Stats Hub

## 🎯 Ce qu'on garde de chaque projet

### ✅ De OccilanStats-6 (Le cœur)
```
✓ Pipeline en 6 étapes (parse → puuid → elo → matches → details → stats)
✓ Format JSON (teams.json, teams_with_puuid.json, match_details.json, general_stats.json)
✓ Calculs stats (get_stats.py) → records, player_stats, team_stats, champions
✓ Sauvegarde intermédiaire à chaque étape
```

### ✅ De Occilan-data-scrapper (L'interface)
```
✓ Streamlit avec sélecteur d'édition dans sidebar
✓ Structure JSON multi-édition: {"edition_4": [...], "edition_5": [...]}
✓ Auth admin avec password
✓ Cache local des matchs (data/cache/matches/)
✓ PUUID → SummonerName resolution
```

### ✅ De SC-Esport-Stats (Visualisation)
```
✓ Graphiques Plotly
✓ Formatage champion icons
✓ Display stats par rôle
```

---

## 📁 Structure finale des dossiers

```
src/
├── core/                    # ⭐ Cœur métier (d'OccilanStats-6)
│   ├── riot_client.py       # Client API unifié
│   ├── data_manager.py      # Gestion JSON par édition
│   └── stats_calculator.py  # Calculs stats (get_stats.py adapté)
│
├── parsers/                 # Parser CSV + OP.GG
│   ├── csv_parser.py
│   └── opgg_parser.py
│
├── pipeline/                # ⭐ Pipeline en 6 étapes
│   ├── edition_processor.py # Orchestration (main.py adapté)
│   └── steps.py            # Chaque étape détaillée
│
├── streamlit_app/           # ⭐ Interface (d'Occilan-data-scrapper)
│   ├── app.py              # Home + sidebar édition
│   ├── pages/
│   │   ├── 1_📊_Overview.py
│   │   ├── 2_👥_Teams.py
│   │   ├── 3_🏆_Players.py
│   │   ├── 4_⚔️_Matches.py
│   │   └── 5_🔧_Admin.py   # Upload CSV + process
│   └── components/
│       ├── charts.py        # Graphiques Plotly
│       ├── tables.py
│       └── utils.py
│
└── utils/
    ├── constants.py
    ├── formatters.py
    └── logger.py

data/
├── editions/                # ⭐ Une édition = un dossier
│   ├── edition_4/
│   │   ├── config.json
│   │   ├── teams.json
│   │   ├── teams_with_puuid.json
│   │   ├── tournament_matches.json
│   │   ├── match_details.json
│   │   └── general_stats.json
│   ├── edition_5/
│   ├── edition_6/
│   └── edition_7/
│
├── cache/                   # Cache partagé entre éditions
│   ├── matches/            # {match_id}.json
│   └── puuid_map.json      # {puuid: name}
│
└── raw/                     # Backup CSV uploadés
    └── edition_X_teams.csv
```

---

## 🔄 Pipeline (inspiré d'OccilanStats-6/main.py)

```
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 1: Parse CSV + OP.GG                         │
│ Input:  teams.csv (team_name, opgg_link)           │
│ Output: teams.json                                  │
│ {team: {players: [{game_name, tag_line, role}]}}   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 2: Fetch PUUIDs                               │
│ Riot API: Account-V1 (game_name#tag → PUUID)       │
│ Output: teams_with_puuid.json (ajoute puuid)       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 3: Fetch Ranked Elo                          │
│ Riot API: Summoner-V4 + League-V4                  │
│ Output: teams_with_puuid.json (update: add elo)    │
│ Ajoute: ranked_tier, ranked_rank, ranked_lp        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 4: Fetch Match IDs                           │
│ Riot API: Match-V5 (custom games, dates tournoi)   │
│ Output: tournament_matches.json                     │
│ {team_name: [match_ids]}                            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 5: Fetch Match Details                       │
│ Riot API: Match-V5 (détails complets) + Cache      │
│ Output: match_details.json                          │
│ {match_id: {full match data}}                       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 6: Calculate Stats                           │
│ Calculs: records, player_stats, team_stats         │
│ Output: general_stats.json                          │
│ {players, teams, records, champions}                │
└─────────────────────────────────────────────────────┘
                        ↓
                  ✅ TERMINÉ
```

---

## 📄 Formats JSON (d'OccilanStats-6)

### teams.json
```json
{
  "KCDQ": {
    "players": [
      {"role": "TOP", "game_name": "Player1", "tag_line": "EUW"},
      {"role": "JUNGLE", "game_name": "Player2", "tag_line": "EUW"},
      {"role": "MID", "game_name": "Player3", "tag_line": "EUW"},
      {"role": "ADC", "game_name": "Player4", "tag_line": "EUW"},
      {"role": "SUPPORT", "game_name": "Player5", "tag_line": "EUW"}
    ],
    "opgg_link": "https://op.gg/multisearch/euw?summoners=..."
  }
}
```

### teams_with_puuid.json
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
      }
      // ... 4 autres
    ]
  }
}
```

### general_stats.json
```json
{
  "longest_game": {...},
  "shortest_game": {...},
  "most_kills_in_game": {...},
  
  "player_stats": {
    "Player1#EUW": {
      "team": "KCDQ",
      "games_played": 12,
      "wins": 9,
      "total_kills": 52,
      "avg_kills": 4.33,
      "kda": 6.52,
      "cs_per_min": 8.2,
      // ...
    }
  },
  
  "team_stats": {
    "KCDQ": {
      "games_played": 12,
      "wins": 9,
      "winrate": 0.75,
      // ...
    }
  }
}
```

---

## 🎨 Interface Streamlit (d'Occilan-data-scrapper)

### Sidebar
```python
# Toutes les pages
st.sidebar.selectbox("Édition", [4, 5, 6, 7], index=3)
st.sidebar.markdown("---")
st.sidebar.info(f"Matchs: {len(matches)}")
```

### Home (app.py)
```python
- Sélecteur édition
- Metrics: équipes, matchs, joueurs
- Navigation vers pages
```

### Overview
```python
- Records du tournoi (plus long match, meilleur KDA, etc.)
- Classement final équipes
```

### Teams
```python
- Tableau classement (winrate, kills, etc.)
- Détail équipe (clic) → roster + stats joueurs
```

### Players
```python
- Leaderboards (KDA, DPM, CS/min, Vision)
- Filtre par rôle
- Profil joueur (clic) → stats + champions
```

### Matches
```python
- Liste chronologique
- Filtres (équipe, date)
- Scoreboard détaillé (clic)
```

### Admin
```python
- Auth password
- Form: numéro, nom, année, dates
- Upload CSV
- Button "Traiter" → Pipeline 6 étapes
- Progress bar temps réel
```

---

## 🚀 Plan d'implémentation

### ✅ Phase 1: Core (PRIORITÉ 1)
```
1. core/riot_client.py          → Merger OccilanStats-6 + data-scrapper
2. core/data_manager.py          → Nouveau (gestion JSON multi-édition)
3. core/stats_calculator.py      → Adapter get_stats.py
4. parsers/*.py                  → Simple (CSV + OP.GG)
```

### ✅ Phase 2: Pipeline (PRIORITÉ 2)
```
5. pipeline/edition_processor.py → Adapter main.py en classe
6. Tester sur édition 6 existante
```

### ✅ Phase 3: Streamlit (PRIORITÉ 3)
```
7. app.py + pages/               → Adapter data-scrapper
8. components/                   → Graphiques + tables
```

### ✅ Phase 4: Finalisation
```
9. Migrer éditions 4, 5, 6 dans nouvelle structure
10. Tests + docs
```

---

## 💡 Différences vs première version

| Aspect | V1 (abandonnée) | V2 (actuelle) |
|--------|-----------------|---------------|
| **Base** | SQL (DuckDB) | JSON par édition |
| **Structure** | Inventée from scratch | Basée sur OccilanStats-6 |
| **Pipeline** | Vague | 6 étapes précises |
| **Formats** | À définir | Existants et testés |
| **Complexité** | Élevée | Moyenne (code existant) |
| **Réutilisation** | 10% | 70% |

---

## ✅ Avantages de cette approche

1. **Réutilisation maximale** : 70% du code existe déjà
2. **Formats testés** : JSON d'OccilanStats-6 fonctionnent
3. **Pipeline clair** : 6 étapes bien définies
4. **Interface éprouvée** : Streamlit de data-scrapper marche
5. **Simple à comprendre** : Suit la logique d'OccilanStats-6
6. **Facile à debugger** : Fichiers intermédiaires à chaque étape

---

**Prêt à implémenter ! On commence par `core/riot_client.py` ?** 🚀
