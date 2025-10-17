# SC-Esport-Stats

Application d'analyse statistique pour l'esport League of Legends.

## Structure du projet

```
SC-Esport-Stats/
├── src/
│   ├── utils/
│   │   └── formatters.py
│   └── components/
│       └── player_stats/
│           └── champion_stats.py
├── static/
│   └── css/
│       ├── style.css
│       └── champion_stats.css
├── templates/
│   ├── base.html
│   └── champion_stats.html
└── app.py
```

## Installation

1. Cloner le repository
2. Installer les dépendances : `pip install -r requirements.txt`
3. Lancer l'application : `streamlit run src/app.py`

## Technologies utilisées

- Python 3.8+
- Streamlit
- Pandas
- Plotly