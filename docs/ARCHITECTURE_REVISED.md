# 📝 Architecture Révisée — OcciLan Stats Hub

## 🎯 Décisions clés

### 1. JSON au lieu de SQL ✅

**Pourquoi ?**
- ✅ Données structurées par édition (pas de relations complexes)
- ✅ Format déjà utilisé dans les 3 projets existants
- ✅ Simple à sauvegarder/charger/versionner
- ✅ Portable, pas de serveur nécessaire
- ✅ Structure flexible selon les éditions

**Structure choisie :**
```
data/editions/
├── edition_4/
│   ├── config.json       # Nom, dates, format tournoi
│   ├── teams.json        # Équipes et joueurs avec PUUID
│   ├── matches.json      # Matchs bruts de Riot API
│   └── stats.json        # Stats calculées (joueurs, équipes, records)
├── edition_5/
├── edition_6/
└── edition_7/
```

---

## 🔄 Workflow réel

```
1. UPLOAD CSV
   team_name,opgg_link
   ↓

2. PARSE OP.GG
   Extraire les 5 pseudos du multi-link
   ↓

3. RIOT API - Account
   game_name + tag_line → PUUID
   ↓

4. RIOT API - Summoner
   PUUID → summoner_id + elo (ranked solo/duo)
   ↓

5. RIOT API - Matches
   Fetch custom games dans la période du tournoi
   ↓

6. RIOT API - Match Details
   Détails complets de chaque match
   ↓

7. CALCULATE STATS
   KDA, CS/min, damage/min, kill participation, etc.
   ↓

8. SAVE JSON
   Tout dans data/editions/edition_X/
   ↓

9. STREAMLIT DISPLAY
   Charger et afficher les données
```

---

## 📦 Merge des 3 projets

### Ce qu'on récupère de chaque projet :

#### 1. **OccilanStats-6** (Excel generator)
✅ **À garder :**
- `scripts/load_teams.py` : Logique de tri par rôle
- `scripts/fetch_puuid.py` : Récup PUUID via Riot API
- `scripts/fetch_matches.py` : Logique de fetch matchs custom
- `scripts/get_stats.py` : Calculs de stats (KDA, moyennes, etc.)
- Structure JSON `teams.json`, `matches.json`, `stats.json`

❌ **À remplacer :**
- Excel input/output → Remplacé par CSV upload + Streamlit
- Logique mono-édition → Multi-édition

#### 2. **Occilan-data-scrapper** (Streamlit prototype)
✅ **À garder :**
- `src/app.py` : Structure Streamlit multi-pages
- `src/utils.py` : Parser OP.GG CSV avec gestion alternates
- `src/match_stats.py` : Fonctions d'agrégation matchs
- Système de sélection d'édition dans sidebar
- Logique de persistence `tournament_matches.json`

❌ **À remplacer :**
- Structure de données ad-hoc → JSON structuré par édition
- Parsing CSV complexe → CSV simplifié (team + opgg_link seulement)

#### 3. **SC-Esport-Stats** (Flask + visualisations)
✅ **À garder :**
- Visualisations Plotly/Altair
- Formatage champion icons
- Structure des stats de joueurs

❌ **À laisser :**
- Flask → Tout en Streamlit
- Structure de données spécifique scrims

---

## 🏗️ Nouvelle architecture

### Structure de dossiers
```
src/
├── api/
│   └── riot_client.py              # Client Riot API unifié
│
├── parsers/
│   ├── opgg_parser.py              # Parse multi OP.GG links
│   └── csv_parser.py               # Parse CSV (team + opgg_link)
│
├── processors/
│   ├── data_fetcher.py             # Orchestration fetch data
│   ├── stats_calculator.py         # Calculs stats
│   └── data_manager.py             # Gestion JSON par édition
│
├── streamlit_app/
│   ├── app.py                      # Home + sélecteur édition
│   ├── pages/
│   │   ├── 1_📊_Overview.py        # Stats globales + records
│   │   ├── 2_👥_Teams.py           # Classement + détails équipes
│   │   ├── 3_🏆_Players.py         # Leaderboards joueurs
│   │   ├── 4_⚔️_Matches.py         # Historique matchs
│   │   └── 5_🔧_Admin.py           # Upload CSV + process
│   └── components/
│       ├── charts.py               # Graphiques réutilisables
│       ├── tables.py               # Tableaux formatés
│       └── filters.py              # Filtres/sélecteurs
│
└── utils/
    ├── constants.py                # Rôles, queues, etc.
    ├── formatters.py               # Format affichage
    └── validators.py               # Validation données
```

---

## 📄 Formats de données

### 1. `config.json` (par édition)
```json
{
  "edition_number": 7,
  "name": "OcciLan #7",
  "year": 2025,
  "start_date": "2025-01-15",
  "end_date": "2025-01-17",
  "num_teams": 16,
  "format": "swiss_playoffs"
}
```

### 2. `teams.json`
```json
{
  "Team Alpha": {
    "players": [
      {
        "role": "TOP",
        "game_name": "Player1",
        "tag_line": "EUW",
        "puuid": "abc123...",
        "summoner_id": "xyz789...",
        "ranked_elo": "Diamond II",
        "ranked_tier": "DIAMOND",
        "ranked_rank": "II",
        "ranked_lp": 45
      },
      // ... 4 autres joueurs
    ],
    "opgg_link": "https://op.gg/multi/..."
  },
  // ... autres équipes
}
```

### 3. `matches.json`
```json
[
  {
    "match_id": "EUW1_7381594783",
    "game_creation": 1705334400000,
    "game_duration": 2570,
    "game_mode": "CLASSIC",
    "teams": {
      "blue": "Team Alpha",
      "red": "Team Beta"
    },
    "winner": "blue",
    "participants": [
      {
        "puuid": "abc123...",
        "team": "blue",
        "champion": "Ahri",
        "kills": 5,
        "deaths": 2,
        "assists": 10,
        // ... toutes les stats Riot
      },
      // ... 9 autres participants
    ]
  },
  // ... autres matchs
]
```

### 4. `stats.json`
```json
{
  "players": {
    "Player1#EUW": {
      "games_played": 12,
      "wins": 8,
      "losses": 4,
      "winrate": 0.667,
      "kda": 3.5,
      "avg_kills": 5.2,
      "avg_deaths": 2.1,
      "avg_assists": 8.5,
      "cs_per_min": 8.2,
      "gold_per_min": 425.3,
      "damage_per_min": 650.2,
      "vision_score_per_min": 1.2,
      "kill_participation": 0.72,
      "most_played_champion": "Ahri",
      "champions": {
        "Ahri": {"games": 5, "winrate": 0.8, "kda": 4.2},
        // ... autres champions
      }
    },
    // ... autres joueurs
  },
  
  "teams": {
    "Team Alpha": {
      "games_played": 12,
      "wins": 9,
      "losses": 3,
      "winrate": 0.75,
      "avg_game_duration": 1850,
      "avg_kills": 18.5,
      "avg_deaths": 12.3,
      "first_blood_rate": 0.67,
      "first_tower_rate": 0.58,
      "first_dragon_rate": 0.75
    },
    // ... autres équipes
  },
  
  "records": {
    "longest_game": {
      "match_id": "EUW1_...",
      "duration": 2570,
      "teams": "Team Alpha vs Team Beta"
    },
    "most_kills_player": {
      "player": "Player1#EUW",
      "kills": 18,
      "match_id": "EUW1_..."
    },
    "highest_kda_game": {
      "player": "Player2#EUW",
      "kda": 15.0,
      "match_id": "EUW1_..."
    },
    // ... autres records
  }
}
```

---

## 🔐 Admin workflow

### Page Admin protégée par mot de passe

```python
# Dans .env
ADMIN_PASSWORD=votre-mot-de-passe-securise
```

### Étapes dans l'interface admin :

1. **Se connecter** : Entrer le mot de passe

2. **Nouvelle édition** :
   - Cliquer "Nouvelle édition"
   - Remplir formulaire (numéro, nom, année, dates)
   - Upload CSV (`team_name,opgg_link`)
   - Cliquer "Process"
   
3. **Processing automatique** :
   - ✅ Parse CSV
   - ✅ Extract Riot IDs from OP.GG
   - ✅ Fetch PUUIDs (Riot API)
   - ✅ Fetch Summoner info + elo
   - ✅ Fetch tournament matches (custom games)
   - ✅ Calculate stats
   - ✅ Save all JSON files
   
4. **Résultat** :
   - Nouvelle édition disponible dans le sélecteur
   - Toutes les pages fonctionnent automatiquement

5. **Refresh data** :
   - Bouton pour re-fetch matchs et recalculer stats
   - Utile si nouveaux matchs après upload initial

---

## 🎨 Interface Streamlit

### Home (app.py)
- Sélecteur d'édition (dropdown)
- Résumé rapide (nombre équipes, matchs, joueurs)
- Liens vers les pages

### Overview
- Stats globales du tournoi
- Records (plus long match, plus de kills, meilleur KDA, etc.)
- Classement final des équipes

### Teams
- Tableau classement équipes (winrate, avg kills, etc.)
- Clic sur équipe → Détail avec stats joueurs

### Players
- Leaderboards par stat (KDA, DPM, CS/min, Vision, etc.)
- Filtres par rôle
- Clic sur joueur → Profil complet

### Matches
- Liste chronologique des matchs
- Filtres (équipe, date, durée)
- Clic sur match → Scoreboard détaillé

### Admin
- 🔒 Authentification
- Formulaire nouvelle édition
- Upload CSV
- Bouton "Process"
- Bouton "Refresh data"
- Logs en temps réel

---

## 🚀 Priorités de développement

### Phase 1 : Core (1-2 jours)
1. ✅ Restructurer config.yaml
2. ✅ Créer `data_manager.py` (gestion JSON éditions)
3. ✅ Adapter `riot_client.py` (merge des 3 projets)
4. ✅ Créer `opgg_parser.py` (extraire pseudos multi-link)
5. ✅ Créer `csv_parser.py` (simple: team + opgg_link)

### Phase 2 : Processing (2-3 jours)
6. ✅ Créer `data_fetcher.py` (orchestration fetch)
7. ✅ Créer `stats_calculator.py` (calculs KPI)
8. ✅ Tester workflow complet sur édition 6

### Phase 3 : Streamlit (2-3 jours)
9. ✅ Page Home avec sélecteur édition
10. ✅ Page Overview (stats + records)
11. ✅ Page Teams
12. ✅ Page Players
13. ✅ Page Matches
14. ✅ Page Admin (upload + process)

### Phase 4 : Migration données (1 jour)
15. ✅ Migrer éditions 4, 5, 6 existantes
16. ✅ Tests complets

### Phase 5 : Polish (1 jour)
17. ✅ Graphiques Plotly/Altair
18. ✅ Formatage champion icons
19. ✅ Export CSV/Excel
20. ✅ Documentation utilisateur

---

## 💡 Changements majeurs vs première version

| Aspect | Avant | Maintenant |
|--------|-------|------------|
| **Storage** | SQL (DuckDB) | JSON par édition |
| **Architecture** | Mono-édition | Multi-édition (hub) |
| **Input** | Toornament API | CSV simple (team + opgg_link) |
| **Roles** | Définis dans CSV | Auto-détectés via Riot API |
| **Database** | Schéma SQL complexe | Fichiers JSON structurés |
| **Admin** | Scripts Python | Interface Streamlit |
| **Déploiement** | Nécessite DB | Fichiers JSON portables |

---

## ✅ Avantages de la nouvelle approche

1. **Simplicité** : Pas de DB à gérer, juste des fichiers JSON
2. **Portabilité** : Copier le dossier = copier toutes les données
3. **Versionning** : Git-friendly (JSON text files)
4. **Flexibilité** : Structure peut varier entre éditions
5. **Performance** : Pandas charge JSON très vite
6. **Debuggabilité** : Facile d'inspecter/éditer JSON
7. **Backup** : Simple copie de fichiers
8. **Migration** : Scripts existants déjà en JSON

---

**Prêt à coder la nouvelle architecture ! 🚀**
