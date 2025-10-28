"""
Page des matchs du tournoi
Affiche la liste des matchs avec leurs détails
"""

"""
Page des matchs du tournoi
Affiche la liste des matchs avec leurs détails
"""

import streamlit as st
from components.match_card import display_match_card
import json
from pathlib import Path
import sys
from src.core.data_manager import EditionDataManager, MultiEditionManager

# Configuration de la page
st.set_page_config(
    page_title="Matchs - OcciLan Stats",
    page_icon="🎮",
    layout="wide"
)

# Masquer la navigation native Streamlit
st.markdown("""
<style>
    [data-testid='stSidebarNav'] { display: none; }
</style>
""", unsafe_allow_html=True)

# Sidebar: Edition selector and navigation
with st.sidebar:
    st.markdown("### 📂 Sélection d'édition")
    multi_manager = MultiEditionManager()
    is_admin = st.session_state.get("authenticated", False)
    available_editions = multi_manager.list_editions(include_private=is_admin)
    if not available_editions:
        st.warning("⚠️ Aucune édition disponible")
        st.info("💡 Créez une édition dans la page Admin")
        selected_edition = None
    else:
        if "selected_edition" not in st.session_state:
            st.session_state.selected_edition = 7 if 7 in available_editions else (available_editions[0] if available_editions else None)
        default_index = 0
        if st.session_state.selected_edition in available_editions:
            default_index = available_editions.index(st.session_state.selected_edition)
        selected_edition = st.selectbox(
            "Édition",
            available_editions,
            index=default_index,
            format_func=lambda x: f"Edition {x}",
            label_visibility="collapsed",
            key="edition_selector_matches"
        )
        st.session_state.selected_edition = selected_edition
        if selected_edition:
            edition_manager = EditionDataManager(selected_edition)
            config = edition_manager.load_config()
            if config:
                st.markdown(f"**{config.get('name', 'N/A')}**")
                st.caption(f"📆 {config.get('start_date', 'N/A')} → {config.get('end_date', 'N/A')}")
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.page_link("app.py", label="🏠 Accueil")
    st.page_link("pages/1_📊_Stats_Generales.py", label="📊 Stats Générales")
    st.page_link("pages/2_Liste_des_Matchs.py", label="📋 Liste des Matchs")
    st.page_link("pages/3_🐉_Stats_Champions.py", label="🐉 Stats Champions")
    st.page_link("pages/4_🏆_Stats_Equipes.py", label="🏆 Stats Équipes")
    st.page_link("pages/5_👤_Stats_Joueurs.py", label="👤 Stats Joueurs")
    st.page_link("pages/6_🔍_Recherche.py", label="🔍 Recherche")
    st.page_link("pages/9_🔧_Admin.py", label="🔧 Admin")
    st.markdown("---")
    st.caption("🎮 OcciLan Stats v2.0")

# Titre de la page
st.title("🎮 Matchs du Tournoi")

# Vérifier qu'une édition est sélectionnée
if not available_editions or not selected_edition:
    st.warning("⚠️ Veuillez d'abord sélectionner une édition")
    st.stop()

# Utiliser l'édition manager
edition_manager = EditionDataManager(selected_edition)
data_dir = Path(__file__).parent.parent.parent.parent / "data" / "editions" / f"edition_{selected_edition}"

# Charger les team_stats pour le mapping joueur->équipe
team_stats_path = data_dir / "team_stats.json"
player_to_team = {}
if team_stats_path.exists():
    with open(team_stats_path, "r", encoding="utf-8") as f:
        team_stats_data = json.load(f)
        for team_name, team_data in team_stats_data.items():
            players = team_data.get("players", {})
            for player_key, player_data in players.items():
                game_name = player_data.get("gameName") or player_data.get("player_name")
                tag_line = player_data.get("tagLine") or ""
                if game_name and tag_line:
                    player_to_team[f"{game_name}#{tag_line}"] = team_name
                    player_to_team[f"{game_name.replace(' ', '').lower()}#{tag_line.lower()}"] = team_name
                if game_name:
                    player_to_team[game_name] = team_name
                    player_to_team[game_name.replace(' ', '').lower()] = team_name

# Charger tournament_matches pour fallback équipe
tournament_matches_path = data_dir / "tournament_matches.json"
tournament_matches = None
if tournament_matches_path.exists():
    with open(tournament_matches_path, "r", encoding="utf-8") as f:
        tournament_matches = json.load(f)

# Charger teams_with_puuid pour l'accès aux oldAccounts
teams_with_puuid = edition_manager.load_teams_with_puuid() if 'edition_manager' in locals() else {}

# Charger les match_details
match_details_path = data_dir / "match_details.json"
if not match_details_path.exists():
    st.error("❌ Aucun match trouvé pour cette édition")
    st.info("💡 Allez dans l'onglet Admin pour lancer le traitement des données")
    st.stop()
with open(match_details_path, "r", encoding="utf-8") as f:
    match_details = json.load(f)
if not match_details:
    st.warning("⚠️ Aucun match disponible")
    st.stop()

# Filtres
st.markdown("---")
st.subheader("🔍 Filtres")
col1, col2 = st.columns(2)
with col1:
    min_duration = st.slider("Durée minimale (minutes)", 0, 60, 0)
with col2:
    sort_by = st.selectbox(
        "Trier par",
        ["Date (récent)", "Date (ancien)", "Durée (longue)", "Durée (courte)", "Kills (plus)", "Kills (moins)"]
    )

# Appliquer les filtres
filtered_matches = {}
for match_id, match_data in match_details.items():
    info = match_data.get("info", {})
    duration = info.get("gameDuration", 0)
    if duration >= (min_duration * 60):
        filtered_matches[match_id] = match_data

# Tri
if sort_by == "Date (récent)":
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: x[1].get("info", {}).get("gameCreation", 0),
        reverse=True
    )
elif sort_by == "Date (ancien)":
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: x[1].get("info", {}).get("gameCreation", 0)
    )
elif sort_by == "Durée (longue)":
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: x[1].get("info", {}).get("gameDuration", 0),
        reverse=True
    )
elif sort_by == "Durée (courte)":
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: x[1].get("info", {}).get("gameDuration", 0)
    )
elif sort_by == "Kills (plus)":
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: sum(p.get("kills", 0) for p in x[1].get("info", {}).get("participants", [])),
        reverse=True
    )
else:  # Kills (moins)
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: sum(p.get("kills", 0) for p in x[1].get("info", {}).get("participants", []))
    )

# Afficher les matchs
st.markdown("---")
st.subheader(f"📋 Liste des matchs ({len(sorted_matches)} matchs)")
if sorted_matches:
    for match_id, match_data in sorted_matches:
        display_match_card(match_id, match_data, player_to_team)
else:
    st.info("Aucun match ne correspond aux filtres sélectionnés")
