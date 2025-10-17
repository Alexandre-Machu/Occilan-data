# 🎮 OcciLan Stats - Hub Multi-Éditions

**Application Streamlit unifiée pour centraliser les statistiques de toutes les éditions de l'OcciLan (4 à 7+)**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Qu'est-ce que c'est ?

Un hub centralisé pour visualiser et comparer les statistiques de toutes les éditions de l'OcciLan, avec :
- 📊 **Multi-éditions** : Parcourir les éditions 4, 5, 6, 7+
- 📈 **Statistiques complètes** : Joueurs, équipes, matchs, champions
- 🔒 **Admin** : Interface pour ajouter de nouvelles éditions
- 🎯 **Comparaisons** : Comparer les performances entre éditions

---

## ✨ Fonctionnalités

### Pour les visiteurs
- Sélectionner une édition (4, 5, 6, 7...)
- Voir les statistiques globales du tournoi
- Explorer les performances par équipe
- Analyser les stats individuelles des joueurs
- Consulter l'historique des matchs

### Pour les admins
- Upload CSV (équipes + liens OP.GG)
- Extraction automatique des pseudos Riot
- Récupération des PUUIDs et elo via Riot API
- Fetch automatique des matchs du tournoi
- Génération des statistiques

---

## 🏗️ Architecture

### Structure des données (JSON)

```
data/
└── editions/
    ├── edition_4/
    │   ├── config.json          # Config de l'édition
    │   ├── teams.json           # Équipes et joueurs
    │   ├── matches.json         # Matchs récupérés
    │   └── stats.json           # Stats calculées
    ├── edition_5/
    ├── edition_6/
    └── edition_7/
```

### Workflow

```
┌──────────────┐
│  CSV Upload  │  team_name, opgg_link
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│  Parse OP.GG    │  Extract Riot IDs from multi-link
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│   Riot API       │  PUUID + Summoner Info + Ranked Elo
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Fetch Matches   │  Tournament custom games
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Calculate Stats │  KDA, CS/min, damage, etc.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Save JSON      │  Store in edition folder
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Streamlit View  │  Display in web interface
└──────────────────┘
```

---

## 🚀 Installation

### 1. Cloner le repository
```bash
git clone https://github.com/Alexandre-Machu/Occilan-data.git
cd Occilan-data
```

### 2. Créer l'environnement virtuel
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Installer les dépendances
```powershell
pip install -r requirements.txt
```

### 4. Configuration
```powershell
# Copier le template
copy .env.example .env

# Éditer .env et ajouter votre clé API Riot
# RIOT_API_KEY=RGAPI-your-key-here
```

---

## 🎮 Utilisation

### Lancer l'application

```powershell
streamlit run src/streamlit_app/app.py
```

L'app sera accessible sur `http://localhost:8501`

### Interface utilisateur

#### Page d'accueil
- Sélection de l'édition
- Stats rapides du tournoi

#### Overview
- Statistiques globales de l'édition
- Records (plus long match, plus de kills, etc.)
- Classement final

#### Teams
- Liste des équipes
- Stats par équipe (winrate, KDA moyen, etc.)
- Détail d'une équipe

#### Players
- Classements individuels (KDA, DPM, CS/min, etc.)
- Profil d'un joueur
- Stats par champion

#### Matches
- Historique complet
- Détails d'un match
- Scoreboard

#### Admin (protégé par mot de passe)
- **Nouvelle édition** : Upload CSV → Process → Generate
- **Refresh data** : Re-fetch matches et recalcul stats
- **Export** : Télécharger les données en CSV/Excel

---

## 📁 Structure du projet

```
Occilan-data/
├── src/
│   ├── api/
│   │   └── riot_client.py          # Client Riot API
│   ├── parsers/
│   │   ├── opgg_parser.py          # Parser liens OP.GG
│   │   └── csv_parser.py           # Parser CSV teams
│   ├── processors/
│   │   ├── data_fetcher.py         # Récupération données Riot
│   │   ├── stats_calculator.py     # Calculs statistiques
│   │   └── data_manager.py         # Gestion JSON par édition
│   ├── streamlit_app/
│   │   ├── app.py                  # Point d'entrée
│   │   └── pages/
│   │       ├── 1_📊_Overview.py
│   │       ├── 2_👥_Teams.py
│   │       ├── 3_🏆_Players.py
│   │       ├── 4_⚔️_Matches.py
│   │       └── 5_🔧_Admin.py
│   └── utils/
│       ├── constants.py            # Constantes (roles, etc.)
│       ├── formatters.py           # Formatage affichage
│       └── validators.py           # Validation données
├── data/
│   └── editions/                   # Données par édition
│       ├── edition_4/
│       ├── edition_5/
│       ├── edition_6/
│       └── edition_7/
├── config/
│   └── config.yaml                 # Config globale app
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📝 Format CSV attendu

```csv
team_name,opgg_link
Team Alpha,https://www.op.gg/multisearch/euw?summoners=Player1,Player2,Player3,Player4,Player5
Team Beta,https://www.op.gg/multisearch/euw?summoners=PlayerA,PlayerB,PlayerC,PlayerD,PlayerE
```

**Important** : 
- Le lien OP.GG doit contenir les 5 joueurs de l'équipe
- Format : `https://www.op.gg/multisearch/euw?summoners=...`
- Les rôles seront détectés automatiquement via l'API Riot

---

## 🔑 Authentification Admin

Par défaut, l'accès admin est protégé. Configurez le mot de passe dans `.env` :

```env
ADMIN_PASSWORD=your-secure-password-here
```

---

## 🛠️ Technologies

| Composant | Tech |
|-----------|------|
| **Frontend** | Streamlit, Plotly, Altair |
| **Backend** | Python 3.10+ |
| **Data** | JSON (pandas pour manipulation) |
| **API** | Riot Games API (EUW) |
| **Parsing** | BeautifulSoup, Regex, urllib |

---

## 📊 Données disponibles

### Par joueur
- KDA (Kills/Deaths/Assists)
- CS/min, Gold/min, Damage/min
- Vision score
- Kill participation
- Champions joués
- Winrate

### Par équipe
- Winrate
- Moyennes d'équipe (kills, gold, etc.)
- First objectives (blood, tower, dragon, baron)
- Records d'équipe

### Par match
- Durée, vainqueur
- Scoreboard complet
- Timeline objectives
- Performance individuelle

---

## 🗺️ Roadmap

### ✅ v1.0 (Actuel)
- [x] Merge des 3 projets existants
- [x] Architecture multi-édition
- [x] Upload CSV + parsing OP.GG
- [x] Interface Streamlit complète
- [x] Stats de base (KDA, CS, etc.)

### 🔄 v1.1 (En cours)
- [ ] Authentification admin robuste
- [ ] Comparaisons inter-éditions
- [ ] Graphiques avancés
- [ ] Export Excel amélioré

### 🔮 v2.0 (Futur)
- [ ] Analyse phase par phase (Swiss, Playoffs)
- [ ] Prédictions de matchs
- [ ] Intégration Discord (webhooks)
- [ ] API REST publique

---

## 🤝 Contribuer

Les contributions sont bienvenues ! Voir [CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

---

## 👨‍💻 Auteur

**Alexandre (Colfeo)**
- GitHub: [@Alexandre-Machu](https://github.com/Alexandre-Machu)
- Discord: Colfeo

---

## 🙏 Crédits

Ce projet unifie et améliore 3 projets précédents :
- **OccilanStats-6** : Génération Excel des stats
- **Occilan-data-scrapper** : Interface Streamlit initiale
- **SC-Esport-Stats** : Visualisations avancées

Merci à tous les contributeurs des projets originaux ! 🎮

---

**Made with ❤️ for the OcciLan community**
