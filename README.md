# 🎮 OcciLan Stats

**Système de statistiques pour le tournoi OcciLan**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Table des matières

- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Technologies](#technologies)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## 🎯 À propos

**OcciLan Stats** est un outil interne de collecte et d'analyse des statistiques pour le tournoi **OcciLan**, un événement étudiant League of Legends organisé chaque année.

### Public cible
- 🎮 **Joueurs** : Suivi de leurs performances individuelles
- 🎪 **Organisateurs** : Vue d'ensemble et gestion du tournoi

### Périmètre
- 16 équipes de 5 joueurs (~80 joueurs)
- ~100 matchs par édition
- Format : Swiss + Playoffs (BO3/BO5)

---

## ✨ Fonctionnalités

### 📊 Analyse des données
- ✅ Import automatique depuis **Toornament** ou CSV
- ✅ Extraction des Riot IDs via liens **OP.GG**
- ✅ Récupération des matchs via **Riot API**
- ✅ Calcul automatique des KPIs et statistiques

### 📈 Visualisation
- 🌍 **Overview** : Statistiques globales du tournoi
- 👥 **Teams** : Performances par équipe
- 🏆 **Players** : Stats détaillées par joueur
- ⚔️ **Matches** : Historique complet des parties
- 🔧 **Admin** : Rafraîchissement et exports

### 💾 Gestion des données
- Cache local (DuckDB/SQLite)
- Exports CSV/JSON
- Historique multi-édition (à venir)

---

## 🏗️ Architecture

```
┌─────────────────┐
│ Toornament API  │
│    ou CSV       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parser OP.GG   │
│  (Riot IDs)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Riot API      │
│ (Match History) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Analysis Engine │
│  (Calculs KPIs) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DuckDB Cache   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Streamlit App   │
│ (Visualisation) │
└─────────────────┘
```

---

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- Clé API Riot Games (gratuite)
- Git

### Étapes

1. **Cloner le repository**
```bash
git clone https://github.com/Alexandre-Machu/Occilan-data.git
cd Occilan-data
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec votre clé API Riot
```

---

## ⚙️ Configuration

### 1. Clé API Riot Games

Obtenez votre clé sur [Riot Developer Portal](https://developer.riotgames.com/)

Ajoutez-la dans `.env` :
```env
RIOT_API_KEY=RGAPI-votre-clé-ici
```

### 2. Configuration du tournoi

Éditez `config/config.yaml` :
```yaml
edition:
  name: "OcciLan 2025"
  year: 2025
  start_date: "2025-01-15"
  end_date: "2025-01-17"
  
tournament:
  format: "swiss_playoffs"
  num_teams: 16
  team_size: 5
```

### 3. Import des équipes

Placez votre fichier CSV dans `data/raw/` :
```csv
team_name,player1,player2,player3,player4,player5,opgg_link
Team Alpha,Player1,Player2,Player3,Player4,Player5,https://www.op.gg/multi/...
```

---

## 🎮 Utilisation

### Lancer l'application Streamlit

```bash
streamlit run src/streamlit_app/app.py
```

L'application sera accessible sur `http://localhost:8501`

### Workflow typique

1. **Importer les équipes** (Admin > Import)
2. **Analyser les liens OP.GG** (extraire les Riot IDs)
3. **Récupérer les matchs** (via Riot API)
4. **Calculer les statistiques**
5. **Consulter les résultats** (pages Overview, Teams, Players)

### Scripts utilitaires

```bash
# Rafraîchir toutes les données
python scripts/refresh_data.py

# Exporter les statistiques
python scripts/export_stats.py --format csv

# Initialiser la base de données
python scripts/init_db.py
```

---

## 📁 Structure du projet

```
Occilan-data/
├── src/                        # Code source
│   ├── api/                    # Intégrations API
│   │   ├── riot_api.py         # Client Riot API
│   │   └── toornament_api.py   # Client Toornament
│   ├── parsers/                # Analyseurs de données
│   │   ├── opgg_parser.py      # Parser OP.GG
│   │   └── csv_parser.py       # Parser CSV
│   ├── database/               # Gestion BDD
│   │   ├── models.py           # Modèles de données
│   │   ├── schema.sql          # Schéma SQL
│   │   └── db_manager.py       # Gestionnaire BDD
│   ├── analysis/               # Calculs statistiques
│   │   ├── stats_calculator.py # Calculs KPIs
│   │   └── aggregator.py       # Agrégation données
│   ├── streamlit_app/          # Interface utilisateur
│   │   ├── app.py              # Application principale
│   │   ├── pages/              # Pages Streamlit
│   │   └── components/         # Composants réutilisables
│   └── utils/                  # Utilitaires
│       ├── logger.py           # Logging
│       └── validators.py       # Validation données
├── data/                       # Données
│   ├── raw/                    # Données brutes (CSV, JSON)
│   ├── processed/              # Données traitées
│   ├── cache/                  # Cache BDD (DuckDB)
│   └── exports/                # Exports finaux
├── docs/                       # Documentation
│   ├── API_GUIDE.md            # Guide API
│   ├── ARCHITECTURE.md         # Architecture détaillée
│   └── CONTRIBUTING.md         # Guide contribution
├── tests/                      # Tests unitaires
├── config/                     # Fichiers de configuration
│   └── config.yaml
├── scripts/                    # Scripts utilitaires
├── requirements.txt            # Dépendances Python
├── .env.example                # Template variables d'env
├── .gitignore
└── README.md
```

---

## 🛠️ Technologies

| Catégorie | Technologies |
|-----------|--------------|
| **Backend** | Python 3.10+, Pandas, Requests |
| **Base de données** | DuckDB, SQLite |
| **API** | Riot Games API, Toornament API |
| **Frontend** | Streamlit, Plotly, Altair |
| **Parsing** | BeautifulSoup4, Regex |
| **Tests** | Pytest |

---

## 📚 Documentation

- 📖 [Documentation complète](OcciLan_Stats_Documentation.md)
- 🏗️ [Architecture détaillée](docs/ARCHITECTURE.md)
- 🔌 [Guide API](docs/API_GUIDE.md)
- 🤝 [Guide de contribution](docs/CONTRIBUTING.md)

---

## 🗺️ Roadmap

### v1.0 (Actuel)
- [x] Import CSV manuel
- [x] Parser OP.GG
- [x] Intégration Riot API
- [x] Interface Streamlit basique
- [x] Cache DuckDB

### v1.1 (Prochain)
- [ ] Intégration complète Toornament
- [ ] Analyse par phase (Swiss/Playoffs)
- [ ] Exports automatiques
- [ ] Webhook Discord

### v2.0 (Futur)
- [ ] Historique multi-édition
- [ ] Comparaisons inter-éditions
- [ ] Système de prédictions
- [ ] API REST publique

---

## 🤝 Contributing

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](docs/CONTRIBUTING.md) pour plus de détails.

### Process
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📝 License

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.

---

## 👤 Auteur

**Alexandre (Colfeo)**
- GitHub: [@Alexandre-Machu](https://github.com/Alexandre-Machu)

---

## 🙏 Remerciements

- [Riot Games](https://developer.riotgames.com/) pour l'API
- [OP.GG](https://op.gg) pour les données publiques
- [Toornament](https://www.toornament.com/) pour l'organisation
- La communauté OcciLan 🎮

---

## ⚠️ Disclaimer

Ce projet est un outil interne non officiel. Il n'est pas affilié à Riot Games ou OP.GG. Toutes les données sont utilisées conformément aux CGU respectives.

---

**Made with ❤️ for the OcciLan community**
