# 🏆 OcciLan Stats

Application Streamlit pour analyser et visualiser les statistiques des tournois OcciLan de League of Legends.

## ✨ Fonctionnalités

- 📊 **Stats Générales**: Vue d'ensemble, distribution des rangs, ELO moyen
- 📋 **Liste des Matchs**: Historique complet, compositions, résultats
- 🐉 **Stats Champions**: Top picks/bans, winrates, KDA moyens
- 🏆 **Stats Équipes**: Performances, pool de champions
- 👤 **Stats Joueurs**: Classement, performances individuelles
- 🔍 **Recherche**: Filtres avancés
- 🔧 **Admin**: Gestion éditions, fetch API Riot

## 🚀 Installation

`ash
git clone https://github.com/Alexandre-Machu/Occilan-data.git
cd Occilan-data
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
`

Éditer .env et ajouter votre clé API Riot.

## �� Utilisation

`ash
streamlit run src/streamlit_app/app.py
`

Application accessible sur http://localhost:8501

## 📁 Structure

`
Occilan-data/
├── src/streamlit_app/    # Application Streamlit
├── src/api/              # Clients API (Riot, Toornament)
├── src/core/             # Logique métier
├── src/pipeline/         # Pipeline de traitement
├── data/editions/        # Données par édition
└── scripts/              # Scripts utilitaires
`

## 📄 Licence

MIT License
