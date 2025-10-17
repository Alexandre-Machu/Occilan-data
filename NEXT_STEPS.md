# 📋 Résumé des changements — OcciLan Stats

## ✅ Ce qui a été fait

### 1. Architecture révisée

**Décision majeure : JSON au lieu de SQL** ✅

**Raisons :**
- Les 3 projets existants utilisent déjà JSON
- Pas de relations complexes à gérer
- Plus simple à sauvegarder/versionner
- Portable (pas de serveur DB nécessaire)
- Un JSON par édition = isolation parfaite

**Nouvelle structure :**
```
data/editions/
├── edition_4/
│   ├── config.json     # Config édition
│   ├── teams.json      # Équipes + joueurs + PUUID + elo
│   ├── matches.json    # Matchs bruts Riot API
│   └── stats.json      # Stats calculées
├── edition_5/
├── edition_6/
└── edition_7/
```

### 2. Documents créés/mis à jour

| Fichier | Statut | Description |
|---------|--------|-------------|
| `README_NEW.md` | ✅ Créé | Nouveau README adapté au hub multi-éditions |
| `docs/ARCHITECTURE_REVISED.md` | ✅ Créé | Architecture détaillée avec workflow JSON |
| `config/config.yaml` | ✅ Mis à jour | Config pour multi-éditions + settings simplifiés |
| `.env.example` | ✅ Mis à jour | Simplifié (Riot API + Admin password) |

### 3. Workflow défini

```
CSV Upload (team_name, opgg_link)
    ↓
Parse OP.GG multi-link → Extract 5 Riot IDs
    ↓
Riot API: Account → PUUID
    ↓
Riot API: Summoner → Elo ranked
    ↓
Riot API: Match IDs → Custom games période tournoi
    ↓
Riot API: Match Details → Stats complètes
    ↓
Calculate Stats → KDA, CS/min, DPM, etc.
    ↓
Save JSON → teams.json, matches.json, stats.json
    ↓
Streamlit Display → Charger et afficher
```

---

## 🎯 Ce qui reste à faire

### Phase 1 : Core Data Management (Priorité 1)

#### À créer :
1. **`src/processors/data_manager.py`**
   - Gérer les éditions (create, load, save)
   - CRUD pour JSON (teams, matches, stats)
   - Gestion de la structure `data/editions/`

2. **Adapter `src/api/riot_api.py`**
   - Merger les bonnes pratiques des 3 projets
   - Rate limiting
   - Retry avec backoff
   - Gestion erreurs

3. **Adapter `src/parsers/opgg_parser.py`**
   - Extraire les 5 pseudos depuis multi-link OP.GG
   - Format : `https://op.gg/multisearch/euw?summoners=P1,P2,P3,P4,P5`
   - Output : Liste de `{game_name, tag_line}`

4. **Adapter `src/parsers/csv_parser.py`**
   - Parser CSV simple : `team_name,opgg_link`
   - Validation basique

### Phase 2 : Data Processing (Priorité 2)

5. **`src/processors/data_fetcher.py`**
   - Orchestrer tout le workflow de récupération
   - CSV → Teams → PUUIDs → Elo → Matches → Details
   - Progress reporting pour Streamlit

6. **`src/processors/stats_calculator.py`**
   - Calculs KPI joueurs (KDA, CS/min, DPM, etc.)
   - Calculs KPI équipes (winrate, first objectives, etc.)
   - Détection records (longest game, most kills, etc.)
   - S'inspirer de `OccilanStats-6/scripts/get_stats.py`

### Phase 3 : Streamlit Interface (Priorité 3)

7. **`src/streamlit_app/app.py`** (refonte)
   - Sélecteur d'édition dans sidebar
   - Afficher infos édition sélectionnée
   - Navigation vers pages

8. **`src/streamlit_app/pages/1_📊_Overview.py`**
   - Stats globales (nb équipes, matchs, joueurs)
   - Records du tournoi
   - Classement final équipes

9. **`src/streamlit_app/pages/2_👥_Teams.py`**
   - Liste des équipes avec stats
   - Détail d'une équipe (clic)
   - Stats joueurs de l'équipe

10. **`src/streamlit_app/pages/3_🏆_Players.py`**
    - Leaderboards (KDA, DPM, CS/min, Vision, etc.)
    - Filtre par rôle
    - Profil joueur (clic)

11. **`src/streamlit_app/pages/4_⚔️_Matches.py`**
    - Liste chronologique
    - Filtres (équipe, date)
    - Scoreboard détaillé (clic)

12. **`src/streamlit_app/pages/5_🔧_Admin.py`**
    - Authentification (ADMIN_PASSWORD)
    - Formulaire nouvelle édition
    - Upload CSV
    - Bouton "Process" avec logs temps réel
    - Bouton "Refresh data"

### Phase 4 : Composants & Utils (Priorité 4)

13. **`src/streamlit_app/components/charts.py`**
    - Graphiques Plotly/Altair réutilisables
    - Récupérer des `SC-Esport-Stats` et `Occilan-data-scrapper`

14. **`src/streamlit_app/components/tables.py`**
    - Tableaux formatés avec tri
    - Icônes champions

15. **`src/utils/constants.py`**
    - Roles : TOP, JUNGLE, MID, ADC, SUPPORT
    - Queue IDs
    - Régions/platforms

16. **`src/utils/formatters.py`**
    - Format duration (seconds → MM:SS)
    - Format numbers (1500 → 1.5k)
    - Format champion names
    - Champion icon URLs

---

## 📦 Code à récupérer des projets existants

### De `OccilanStats-6/`

#### `scripts/fetch_puuid.py`
```python
def fetch_puuid(teams, api_key, base_url):
    # Logique de récup PUUID par Riot ID
    # À adapter pour notre nouveau format
```

#### `scripts/fetch_matches.py`
```python
def fetch_tournament_matches(teams_with_puuid):
    # Récup match IDs de tous les joueurs
    # Filtrer custom games
    # Dédupliquer
```

#### `scripts/get_stats.py`
```python
def get_stats(match_details, teams_with_puuid):
    # Calculs KPI
    # Agrégations
    # Records
```

### De `Occilan-data-scrapper/`

#### `src/utils.py`
```python
def parse_opgg_adversaires_csv(...):
    # Logique d'extraction pseudos depuis lien OP.GG
    # Gestion alternates (A / B)
```

#### `src/match_stats.py`
```python
def aggregate_matches(...):
    # Agrégation stats matchs
```

#### `src/app.py`
```python
# Structure Streamlit multi-pages
# Système de sélection édition
# Persistence données
```

### De `SC-Esport-Stats/`
```python
# Visualisations Plotly
# Formatage champion icons
# Display player stats
```

---

## 🚧 Suppression du code obsolète

### À supprimer :
- ❌ `src/database/` (tout le dossier) → Remplacé par `data_manager.py`
- ❌ `src/database/schema.sql` → Plus besoin de SQL
- ❌ `src/database/models.py` → Remplacé par structures JSON
- ❌ `src/database/db_manager.py` → Remplacé par `data_manager.py`
- ❌ `src/api/toornament_api.py` → Pas utilisé pour l'instant
- ❌ Scripts anciens qui référencent la DB

### À garder mais adapter :
- ✅ `src/api/riot_api.py` → Adapter/améliorer
- ✅ `src/parsers/opgg_parser.py` → Adapter pour multi-link
- ✅ `src/parsers/csv_parser.py` → Simplifier (juste team + opgg)
- ✅ `src/utils/logger.py` → Garder tel quel

---

## 🎨 Interface Streamlit - Maquette

### Sidebar (toutes pages)
```
[Sélecteur d'édition]
▼ OcciLan #7

━━━━━━━━━━━━━━━━

📊 Overview
👥 Teams
🏆 Players
⚔️ Matches

━━━━━━━━━━━━━━━━

🔧 Admin
```

### Page d'accueil
```
🎮 OcciLan Stats Hub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Édition sélectionnée : OcciLan #7 (2025)

┌────────────┬────────────┬────────────┐
│ 16 équipes │ 95 matchs │ 80 joueurs │
└────────────┴────────────┴────────────┘

➜ Voir Overview
➜ Consulter les équipes
➜ Classements joueurs
```

### Page Overview
```
📊 OcciLan #7 — Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 Records du tournoi
┌────────────────────────────────────┐
│ Plus long match : 42:50            │
│ KCDQ vs La bande du PMU            │
│                                    │
│ Meilleur KDA : 15.0 — Player#EUW   │
│ Plus de kills : 18 — Player2#EUW   │
│ ...                                │
└────────────────────────────────────┘

📈 Classement final
1. Team Alpha — 12-3 (80%)
2. Team Beta — 11-4 (73%)
3. ...
```

### Page Admin
```
🔧 Administration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 Connexion
[Mot de passe] [🔑 Se connecter]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

➕ Nouvelle édition

Numéro : [7]
Nom : [OcciLan #7]
Année : [2025]
Date début : [2025-01-15]
Date fin : [2025-01-17]

📄 Upload CSV
[Drag & drop or browse]

[▶️ Process Edition]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Éditions existantes

Edition 6 — 2024
[🔄 Refresh] [📥 Export] [🗑️ Delete]

Edition 5 — 2024
[🔄 Refresh] [📥 Export] [🗑️ Delete]
```

---

## 🎯 Prochaine étape suggérée

**Je recommande de commencer par :**

1. **Créer `data_manager.py`** (gestion JSON)
   - Fonctions : `create_edition()`, `load_edition()`, `save_teams()`, etc.
   - C'est la fondation de tout

2. **Adapter `riot_client.py`**
   - Merger les meilleures parties des 3 projets
   - Ajouter rate limiting propre

3. **Créer `data_fetcher.py`**
   - Pipeline complet CSV → Stats
   - Utiliser `data_manager` et `riot_client`

4. **Tester sur édition 6** (données déjà disponibles)
   - Valider que tout fonctionne

5. **Créer l'interface Streamlit**
   - Une fois les données bien gérées

**Voulez-vous que je commence par créer ces fichiers ?**
