# OccilanStats

## Description
OccilanStats est un outil d'analyse de statistiques pour les tournois League of Legends de l'Occilan. Il collecte et analyse les données des matchs pour générer un rapport détaillé.

## Prérequis
- Python 3.10+
- Une clé API Riot Games
- Les dépendances listées dans `requirements.txt`

## Installation
1. Clonez le repository
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```
3. Créez un fichier `.env` avec votre clé API :
```env
API_KEY=RGAPI-your-api-key-here
```

## Structure du projet
```
OccilanStats/
├── data/                     # Données JSON et Excel
│   ├── pseudosOccilan#6.xlsx # Fichier des équipes
│   ├── teams.json           # Équipes formatées
│   ├── teams_with_puuid.json # Équipes avec PUUIDs
│   ├── tournament_matches.json # IDs des matchs
│   ├── match_details.json   # Détails des matchs
│   └── general_stats.json   # Statistiques finales
├── output/
│   └── OccilanStats.xlsx    # Rapport final
├── scripts/                 # Scripts Python
└── main.py                 # Point d'entrée
```

## Flux de données

### 1. Chargement des équipes
- **Script** : `load_teams.py`
- **Entrée** : `pseudosOccilan#6.xlsx`
- **Sortie** : `teams.json`
- **Description** : Conversion du fichier Excel en format JSON

### 2. Récupération des PUUIDs
- **Script** : `fetch_puuid.py`
- **Entrée** : `teams.json`
- **Sortie** : `teams_with_puuid.json`
- **Description** : Ajout des identifiants Riot (PUUID)

### 3. Récupération des matchs
- **Script** : `fetch_matches.py`
- **Entrée** : `teams_with_puuid.json`
- **Sortie** : `tournament_matches.json`
- **Description** : Liste des matchs du tournoi

### 4. Détails des matchs
- **Script** : `analyze_match_stats.py`
- **Entrée** : `tournament_matches.json`
- **Sortie** : `match_details.json`
- **Description** : Données complètes des matchs

### 5. Statistiques générales
- **Script** : `get_stats.py`
- **Entrée** : `match_details.json`
- **Sortie** : `general_stats.json`
- **Description** : Toutes les statistiques calculées

### 6. Rapport Excel
- **Script** : `create_excel.py`
- **Entrée** : `general_stats.json`
- **Sortie** : `OccilanStats.xlsx`
- **Description** : Rapport final formatté

## Statistiques calculées
- Statistiques par joueur
  - Kills/Deaths/Assists (total et moyenne)
  - KDA moyen
  - CS par minute
  - Score de vision
  - Champions joués
- Statistiques par match
  - Durée des parties
  - Nombre de kills
  - Vision score
  - CS par minute
- Statistiques des champions
  - Picks
  - Bans
  - Winrates

## Utilisation
```bash
python main.py
```

## Contribution
Les contributions sont les bienvenues via issues ou pull requests.

## Licence
[MIT](LICENSE)