# Architecture Détaillée — OcciLan Stats

## Vue d'ensemble

OcciLan Stats est conçu selon une architecture modulaire en couches, favorisant la séparation des responsabilités et la maintenabilité.

## Architecture en couches

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│              (Streamlit Web Interface)                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│         (Business Logic & Data Processing)               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│              (Database & Persistence)                    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Integration Layer                       │
│            (External APIs & Parsers)                     │
└─────────────────────────────────────────────────────────┘
```

## Modules détaillés

### 1. API Integration (`src/api/`)

#### `riot_api.py`
**Responsabilité**: Client pour l'API Riot Games

**Méthodes principales**:
- `get_account_by_riot_id()`: Récupère les infos de compte (PUUID)
- `get_summoner_by_puuid()`: Récupère les infos d'invocateur
- `get_match_ids_by_puuid()`: Liste des matchs d'un joueur
- `get_match_details()`: Détails complets d'un match
- `get_match_timeline()`: Timeline événementielle

**Gestion des erreurs**:
- Rate limiting
- Retry avec backoff exponentiel
- Timeout handling

#### `toornament_api.py`
**Responsabilité**: Client pour l'API Toornament (futur)

**Statut**: Placeholder pour v1.1

---

### 2. Parsers (`src/parsers/`)

#### `opgg_parser.py`
**Responsabilité**: Extraction des Riot IDs depuis les URLs OP.GG

**Flux**:
1. Validation de l'URL
2. Parsing des paramètres (région, summoners)
3. Extraction des noms d'invocateurs
4. Conversion en format Riot ID (Name#TAG)

**Format d'entrée**:
```
https://www.op.gg/multisearch/euw?summoners=Player1,Player2,Player3
```

**Format de sortie**:
```python
[
    {"game_name": "Player1", "tag_line": "EUW"},
    {"game_name": "Player2", "tag_line": "EUW"},
    ...
]
```

#### `csv_parser.py`
**Responsabilité**: Import de données d'équipes depuis CSV

**Format CSV attendu**:
```csv
team_name,player1,player2,player3,player4,player5,opgg_link
Team Alpha,Top1,Jgl1,Mid1,Adc1,Sup1,https://op.gg/...
```

**Validation**:
- Présence des colonnes requises
- Nombre de joueurs (5 par équipe)
- Validité des liens OP.GG

---

### 3. Database (`src/database/`)

#### `db_manager.py`
**Responsabilité**: Gestion des connexions et opérations DB

**Choix technique**: DuckDB
- Performances excellentes pour l'analytique
- Support SQL complet
- Fichier unique (portable)
- Pas de serveur requis

**API**:
```python
with DatabaseManager() as db:
    results = db.fetch_df("SELECT * FROM player_stats")
```

#### `models.py`
**Responsabilité**: Définition des structures de données

**Modèles principaux**:
- `Edition`: Édition du tournoi
- `Team`: Équipe
- `Player`: Joueur avec infos Riot
- `Match`: Partie
- `Participant`: Performance individuelle
- `PlayerStats`: Stats agrégées joueur
- `TeamStats`: Stats agrégées équipe

#### `schema.sql`
**Responsabilité**: Définition du schéma de base de données

**Tables principales**: 10 tables + 3 vues
**Relations**: Clés étrangères avec CASCADE
**Index**: Optimisés pour les requêtes fréquentes

---

### 4. Analysis (`src/analysis/`)

#### `stats_calculator.py` (à créer)
**Responsabilité**: Calculs de KPIs

**Métriques calculées**:
- **KDA**: (Kills + Assists) / Deaths
- **CS/min**: Creep Score par minute
- **Gold/min**: Or gagné par minute
- **Damage/min**: Dégâts infligés par minute
- **Kill Participation**: (Kills + Assists) / Team Kills
- **Damage Share**: Dégâts du joueur / Dégâts de l'équipe
- **Gold Share**: Or du joueur / Or de l'équipe

#### `aggregator.py` (à créer)
**Responsabilité**: Agrégation des données

**Fonctions**:
- Agrégation par joueur
- Agrégation par équipe
- Agrégation par champion
- Agrégation par phase (Swiss/Playoffs)

---

### 5. Streamlit App (`src/streamlit_app/`)

#### Structure des pages

```
src/streamlit_app/
├── app.py                    # Point d'entrée principal
├── pages/
│   ├── 1_📊_Overview.py      # Stats globales
│   ├── 2_👥_Teams.py         # Performance des équipes
│   ├── 3_🏆_Players.py       # Stats des joueurs
│   ├── 4_⚔️_Matches.py       # Historique des matchs
│   └── 5_🔧_Admin.py         # Gestion des données
└── components/
    ├── charts.py             # Composants de graphiques
    ├── tables.py             # Tableaux de données
    └── filters.py            # Filtres et sélecteurs
```

#### Navigation Streamlit
- **Multi-page app** avec `pages/`
- **State management** via `st.session_state`
- **Caching** avec `@st.cache_data` et `@st.cache_resource`

---

### 6. Utils (`src/utils/`)

#### `logger.py`
**Responsabilité**: Configuration du logging

**Fonctionnalités**:
- Logs console (niveau INFO)
- Logs fichier avec rotation (1 jour, 7 jours de rétention)
- Format structuré
- Compression automatique

#### `validators.py` (à créer)
**Responsabilité**: Validation des données

**Validateurs**:
- Validation Riot ID
- Validation URL OP.GG
- Validation CSV
- Validation dates de tournoi

---

## Flux de données

### 1. Import d'équipes

```
CSV File → CSVParser → Database (team + player)
                    ↓
              OP.GG Link → OPGGParser → Riot IDs
                                      ↓
                                   Riot API → PUUID
                                            ↓
                                      Database (update)
```

### 2. Récupération de matchs

```
PUUID → Riot API (match_ids) → Match IDs
                              ↓
                        Riot API (match_details)
                              ↓
                        Match Data + Participants
                              ↓
                        Database (match + participant)
```

### 3. Calcul de statistiques

```
Database (participants) → StatsCalculator → Aggregated Stats
                                          ↓
                                    Database (player_stats, team_stats)
```

### 4. Affichage

```
Streamlit Page → Database Query → Pandas DataFrame
                                ↓
                            Data Transformation
                                ↓
                          Plotly/Altair Charts
                                ↓
                            User Interface
```

---

## Gestion du cache

### Stratégie de cache

1. **Match Data**: Cache de 24h
2. **Player Stats**: Recalcul à la demande
3. **Team Stats**: Recalcul à la demande

### Invalidation
- Manuel (bouton "Refresh" dans Admin)
- Automatique après import de nouvelles données

---

## Gestion des erreurs

### Niveaux d'erreurs

1. **API Errors**
   - Rate limit → Retry avec backoff
   - 404 → Log + skip
   - 5xx → Retry jusqu'à 3 fois

2. **Data Errors**
   - Invalid format → Log + user notification
   - Missing data → Default values
   - Duplicate data → Update ou skip

3. **Database Errors**
   - Connection → Retry
   - Constraint violation → Rollback + log

---

## Performance

### Optimisations

1. **Database**
   - Index sur clés fréquemment recherchées
   - Vues matérialisées pour requêtes complexes
   - Batch inserts

2. **API Calls**
   - Rate limiting respecté (20 req/s)
   - Parallélisation avec asyncio (futur)
   - Cache local des réponses

3. **Streamlit**
   - `@st.cache_data` pour requêtes DB
   - `@st.cache_resource` pour connexions
   - Pagination des tableaux

---

## Sécurité

### Bonnes pratiques

1. **API Keys**
   - Stockées dans `.env`
   - Jamais committées
   - Rotation régulière

2. **Données**
   - Validation de toutes les entrées
   - Sanitization des requêtes SQL
   - Pas de données sensibles

3. **Compliance**
   - Respect des CGU Riot
   - Respect des CGU OP.GG
   - Usage interne uniquement

---

## Évolutivité

### v1.0 → v1.1
- Intégration Toornament complète
- Analyse par phase de tournoi
- Webhook Discord

### v1.1 → v2.0
- Multi-édition avec comparaisons
- API REST publique
- Système de prédictions
- Authentification utilisateurs

---

## Tests

### Structure (à implémenter)

```
tests/
├── unit/
│   ├── test_parsers.py
│   ├── test_api_clients.py
│   └── test_calculators.py
├── integration/
│   ├── test_data_flow.py
│   └── test_database.py
└── e2e/
    └── test_streamlit_app.py
```

### Coverage attendu
- Unit tests: 80%+
- Integration tests: critiques paths
- E2E: happy paths

---

## Déploiement

### Options

1. **Local** (actuel)
   - Streamlit local
   - Database fichier

2. **Cloud** (futur)
   - Streamlit Cloud / Heroku
   - PostgreSQL / DuckDB cloud
   - CI/CD avec GitHub Actions

---

## Diagramme de classes

```
Edition
  └─ has many → Team
                  └─ has many → Player
                  └─ has many → TeamStats

Match
  ├─ belongs to → Edition
  ├─ has one → Team (blue)
  ├─ has one → Team (red)
  └─ has many → Participant
                  └─ belongs to → Player
                  └─ belongs to → Team

PlayerStats
  ├─ belongs to → Player
  └─ belongs to → Edition

PlayerChampionStats
  ├─ belongs to → Player
  ├─ belongs to → Edition
  └─ has one → Champion (ID)
```

---

**Dernière mise à jour**: 2025-10-17
