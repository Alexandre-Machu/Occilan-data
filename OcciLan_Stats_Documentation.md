# Documentation du Projet — OcciLan Stats

_Last updated: aujourd’hui_

---

## 1. Présentation générale
OcciLan Stats est un projet interne destiné à centraliser et visualiser les statistiques du tournoi **OcciLan**, un événement étudiant organisé chaque année. Il s’adresse avant tout aux **joueurs** et **organisateurs** de l’OcciLan, afin de suivre les performances, les résultats et les statistiques de chaque équipe et joueur pendant et après le tournoi.

**Objectif principal :**
Automatiser la récupération et l’analyse des statistiques des matchs de la LAN à partir de liens OP.GG ou d’un export Toornament.

**Public cible :**
- Joueurs de l’OcciLan
- Organisateurs du tournoi

**Périmètre :**
- 16 équipes de 5 joueurs
- Environ 100 matchs par édition
- Format : Swiss + Playoffs (BO3/BO5)

---

## 2. Description fonctionnelle
1. L’organisateur choisit une édition.
2. L’app charge les équipes (Toornament ou CSV).
3. Les liens Multi‑OP.GG sont analysés.
4. Les joueurs sont identifiés via Riot API.
5. Les matchs sont collectés et analysés.
6. Les résultats s’affichent dans Streamlit.

### Pages principales
- **Overview** : stats globales du tournoi
- **Teams** : stats par équipe
- **Players** : stats détaillées par joueur
- **Matches** : historique complet
- **Admin** : rafraîchissement et exports

---

## 3. Données et sources
| Source | Utilisation |
|---------|-------------|
| Toornament API | Liste des équipes |
| CSV | Import manuel |
| OP.GG | Extraction des Riot IDs |
| Riot API | Matchs, stats et profils |

---

## 4. Processus global
```
[Toornament / CSV] → [Parser OP.GG] → [Riot API]
                                   ↓
                           [Calculs & KPIs]
                                   ↓
                         [Cache + Visualisation]
```

---

## 5. Données principales
| Table | Description |
|--------|--------------|
| edition | Informations tournoi |
| team | Équipe et membres |
| player | PUUID, Riot ID, rôle |
| match | Partie (durée, score) |
| participant | Stats individuelles |
| player_stats | Moyennes par joueur |
| player_champ_stats | Moyennes par champion |
| team_stats | Moyennes par équipe |

---

## 6. Technologies
- Python, Pandas, Streamlit
- DuckDB / SQLite (cache)
- Riot API officielle

---

## 7. Sécurité
- Clé Riot API privée (serveur)
- Respect CGU Riot / OP.GG
- Données publiques, usage interne

---

## 8. Limites et risques
| Type | Description |
|------|-------------|
| Technique | Rate limit Riot API |
| Données | Matchs customs incomplets |
| Performance | Temps de chargement initial |
| Maintenance | Changements d’API |

---

## 9. Évolutions prévues
- Intégration complète Toornament
- Analyse par phase (Swiss / Playoffs)
- Historique multi‑édition
- Export auto + intégration Discord

---

## 10. Gouvernance
- Responsable : Alexandre (Colfeo)
- 1‑2 éditions par an
- ~80 joueurs, ~100 matchs
- Livrables : tableaux, graphiques, exports

---

**Conclusion :**
OcciLan Stats fournit un outil clair et automatisé pour suivre les performances des joueurs et équipes pendant la LAN, tout en préparant les bases pour un suivi multi‑édition à long terme.
