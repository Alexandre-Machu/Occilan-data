"""
Page des matchs du tournoi
Affiche la liste des matchs avec leurs détails
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.data_manager import EditionDataManager, MultiEditionManager

# Configuration de la page
st.set_page_config(
    page_title="Matchs - OcciLan Stats",
    page_icon="🎮",
    layout="wide"
)

# Helper function for champion icons
def get_role_icon_url(role: str, size: int = 24) -> str:
    """Get Data Dragon role icon URL"""
    role_norm = role.upper()
    if role_norm in ["TOP"]:
        key = "position-top.svg"
    elif role_norm in ["JGL", "JUNGLE"]:
        key = "position-jungle.svg"
    elif role_norm in ["MID", "MIDDLE"]:
        key = "position-middle.svg"
    elif role_norm in ["ADC", "BOTTOM"]:
        key = "position-bottom.svg"
    elif role_norm in ["SUP", "SUPP", "UTILITY"]:
        key = "position-utility.svg"
    else:
        key = "position-top.svg"
    return f"https://raw.communitydragon.org/pbe/plugins/rcp-fe-lol-static-assets/global/default/svg/{key}"
def get_champion_icon_url(champion_name: str) -> str:
    """Get Data Dragon champion icon URL"""
    # Mapping pour les champions avec des noms spéciaux
    champion_mapping = {
        "MonkeyKing": "Wukong",
        "Belveth": "Belveth",
        "RenataGlasc": "Renata"
    }
    # Utiliser le mapping si disponible, sinon garder le nom original
    display_name = champion_mapping.get(champion_name, champion_name)
    return f"https://ddragon.leagueoflegends.com/cdn/15.20.1/img/champion/{display_name}.png"

# Custom CSS pour masquer la navigation par défaut
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - Navigation cohérente
# ============================================================================

with st.sidebar:
    st.markdown("### 📂 Sélection d'édition")
    
    multi_manager = MultiEditionManager()
    
    # Vérifier si l'utilisateur est admin
    is_admin = st.session_state.get("authenticated", False)
    
    # Lister les éditions (privées uniquement si admin)
    available_editions = multi_manager.list_editions(include_private=is_admin)
    
    if not available_editions:
        st.warning("⚠️ Aucune édition disponible")
        st.info("💡 Créez une édition dans la page Admin")
        selected_edition = None
    else:
        # Initialiser selected_edition dans session_state si pas déjà fait
        if "selected_edition" not in st.session_state:
            st.session_state.selected_edition = available_editions[0]
        
        # Trouver l'index de l'édition sélectionnée
        default_index = 0
        if st.session_state.selected_edition in available_editions:
            default_index = available_editions.index(st.session_state.selected_edition)
        
        # Sélecteur visible pour tous les utilisateurs
        selected_edition = st.selectbox(
            "Édition",
            available_editions,
            index=default_index,
            format_func=lambda x: f"Edition {x}",
            label_visibility="collapsed",
            key="edition_selector_matches"
        )
        
        # Sauvegarder dans session_state
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

def format_duration(seconds):
    """Convertit des secondes en format MM:SS"""
    minutes = int(seconds / 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def get_champion_icon_url(champion_name):
    """Retourne l'URL de l'icône du champion"""
    return f"https://ddragon.leagueoflegends.com/cdn/15.20.1/img/champion/{champion_name}.png"

def get_team_name_from_players(participants, player_to_team):
    """Trouve le nom de l'équipe à partir des joueurs"""
    for p in participants:
        player_name = p.get('riotIdGameName', 'Unknown')
        if player_name in player_to_team:
            return player_to_team[player_name]
    return "Équipe Inconnue"

def sort_players_by_role(participants):
    """Trie les joueurs par rôle: TOP, JGL, MID, ADC, SUP"""
    role_order = {"TOP": 1, "JUNGLE": 2, "MIDDLE": 3, "BOTTOM": 4, "UTILITY": 5}
    return sorted(participants, key=lambda p: role_order.get(p.get("teamPosition", "UTILITY"), 6))

def display_match_card(match_id, match_data, player_to_team):
    """Affiche une carte de match"""
    info = match_data.get("info", {})
    participants = info.get("participants", [])
    teams = info.get("teams", [])
    
    # Durée du match
    duration = info.get("gameDuration", 0)
    duration_str = format_duration(duration)
    
    # Date du match
    game_creation = info.get("gameCreation", 0)
    if game_creation:
        game_date = datetime.fromtimestamp(game_creation / 1000)
        date_str = game_date.strftime("%d/%m/%Y %H:%M")
    else:
        date_str = "Date inconnue"
    
    # Séparer les participants par équipe
    team_100 = [p for p in participants if p.get("teamId") == 100]
    team_200 = [p for p in participants if p.get("teamId") == 200]
    
    # Trier les joueurs par rôle
    team_100 = sort_players_by_role(team_100)
    team_200 = sort_players_by_role(team_200)
    
    # Récupérer les infos des équipes
    team_100_info = next((t for t in teams if t.get("teamId") == 100), {})
    team_200_info = next((t for t in teams if t.get("teamId") == 200), {})
    
    team_100_win = team_100_info.get("win", False)
    team_200_win = team_200_info.get("win", False)
    
    # Noms des équipes (mapping depuis team_stats)
    team_100_name = get_team_name_from_players(team_100, player_to_team)
    team_200_name = get_team_name_from_players(team_200, player_to_team)
    
    # Déterminer le gagnant pour l'affichage
    if team_100_win:
        match_title = f"🎮 {team_100_name} 🏆 vs {team_200_name}"
    elif team_200_win:
        match_title = f"🎮 {team_100_name} vs {team_200_name} 🏆"
    else:
        match_title = f"🎮 {team_100_name} vs {team_200_name}"
    
    # Afficher le match
    with st.expander(f"{match_title} - {date_str} ({duration_str})", expanded=False):
        col1, col_vs, col2 = st.columns([5, 1, 5])
        
        with col1:
            # Équipe 100 (Bleue)
            if team_100_win:
                st.markdown(f"### 🔵 **{team_100_name}** ✅ VICTOIRE")
            else:
                st.markdown(f"### 🔵 **{team_100_name}** ❌ DÉFAITE")
            
            # Statistiques de l'équipe
            total_kills_100 = sum(p.get("kills", 0) for p in team_100)
            total_gold_100 = sum(p.get("goldEarned", 0) for p in team_100)
            
            st.metric("Kills", total_kills_100)
            st.metric("Gold total", f"{total_gold_100:,}")
            
            # Joueurs
            st.markdown("#### Joueurs")
            for p in team_100:  # Déjà triés par rôle
                player_name = p.get('riotIdGameName', 'Unknown')
                champion = p.get("championName", "Unknown")
                kills = p.get("kills", 0)
                deaths = p.get("deaths", 0)
                assists = p.get("assists", 0)
                cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
                role = p.get("teamPosition", "UNKNOWN")
                kda = f"{kills}/{deaths}/{assists}"
                icon_url = get_champion_icon_url(champion)
                role_icon_url = get_role_icon_url(role)
                # Créer une ligne avec la carte du joueur et le bouton à droite
                col_card, col_button = st.columns([5, 1])
                with col_card:
                    # Player row with champion icon et icône du rôle
                    player_html = f'''
                    <div style="display: flex; align-items: center; gap: 12px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px; margin-bottom: 6px;">
                        <img src="{icon_url}" style="width: 40px; height: 40px; border-radius: 6px; border: 2px solid rgba(100,150,255,0.3);" title="{champion}">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: #e6eef6; font-size: 14px;">
                                <img src="{role_icon_url}" style="width:18px;vertical-align:middle;margin-right:4px;" title="{role}">{player_name}
                            </div>
                            <div style="color: #9fb0c6; font-size: 12px;">{champion}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #e6eef6; font-weight: 600;">{kda}</div>
                            <div style="color: #9fb0c6; font-size: 11px;">{cs} CS</div>
                        </div>
                    </div>
                    '''
                    st.markdown(player_html, unsafe_allow_html=True)
                
                with col_button:
                    # Bouton à droite de la carte
                    if st.button(f"👤 Profil", key=f"profile_{match_id}_100_{player_name}", help=f"Voir les stats de {player_name}"):
                        st.session_state["search_player"] = player_name
                        st.switch_page("pages/6_🔍_Recherche.py")
        
        with col_vs:
            st.markdown("### VS")
            st.markdown(f"**{duration_str}**")
        
        with col2:
            # Équipe 200 (Rouge)
            if team_200_win:
                st.markdown(f"### 🔴 **{team_200_name}** ✅ VICTOIRE")
            else:
                st.markdown(f"### 🔴 **{team_200_name}** ❌ DÉFAITE")
            
            # Statistiques de l'équipe
            total_kills_200 = sum(p.get("kills", 0) for p in team_200)
            total_gold_200 = sum(p.get("goldEarned", 0) for p in team_200)
            
            st.metric("Kills", total_kills_200)
            st.metric("Gold total", f"{total_gold_200:,}")
            
            # Joueurs
            st.markdown("#### Joueurs")
            for p in team_200:  # Déjà triés par rôle
                player_name = p.get('riotIdGameName', 'Unknown')
                champion = p.get("championName", "Unknown")
                kills = p.get("kills", 0)
                deaths = p.get("deaths", 0)
                assists = p.get("assists", 0)
                cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
                role = p.get("teamPosition", "UNKNOWN")
                kda = f"{kills}/{deaths}/{assists}"
                icon_url = get_champion_icon_url(champion)
                role_icon_url = get_role_icon_url(role)
                col_card, col_button = st.columns([5, 1])
                with col_card:
                    player_html = f'''
                    <div style="display: flex; align-items: center; gap: 12px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px; margin-bottom: 6px;">
                        <img src="{icon_url}" style="width: 40px; height: 40px; border-radius: 6px; border: 2px solid rgba(255,100,100,0.3);" title="{champion}">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: #e6eef6; font-size: 14px;">
                                <img src="{role_icon_url}" style="width:18px;vertical-align:middle;margin-right:4px;" title="{role}">{player_name}
                            </div>
                            <div style="color: #9fb0c6; font-size: 12px;">{champion}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #e6eef6; font-weight: 600;">{kda}</div>
                            <div style="color: #9fb0c6; font-size: 11px;">{cs} CS</div>
                        </div>
                    </div>
                    '''
                    st.markdown(player_html, unsafe_allow_html=True)
                
                with col_button:
                    # Bouton à droite de la carte
                    if st.button(f"👤 Profil", key=f"profile_{match_id}_200_{player_name}", help=f"Voir les stats de {player_name}"):
                        st.session_state["search_player"] = player_name
                        st.switch_page("pages/6_🔍_Recherche.py")


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
        # Créer le mapping joueur -> équipe
        for team_name, team_data in team_stats_data.items():
            players = team_data.get("players", {})
            for player_name in players.keys():
                player_to_team[player_name] = team_name

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

# Statistiques globales
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Nombre de matchs", len(match_details))

with col2:
    total_duration = sum(m.get("info", {}).get("gameDuration", 0) for m in match_details.values())
    avg_duration = total_duration / len(match_details) if len(match_details) > 0 else 0
    st.metric("Durée moyenne", format_duration(avg_duration))

with col3:
    total_kills = 0
    for match_data in match_details.values():
        participants = match_data.get("info", {}).get("participants", [])
        total_kills += sum(p.get("kills", 0) for p in participants)
    avg_kills = total_kills / len(match_details) if len(match_details) > 0 else 0
    st.metric("Kills moyens/match", f"{avg_kills:.1f}")

with col4:
    # Calculer le match le plus long
    longest_match = max(match_details.values(), key=lambda m: m.get("info", {}).get("gameDuration", 0))
    longest_duration = longest_match.get("info", {}).get("gameDuration", 0)
    st.metric("Match le plus long", format_duration(longest_duration))

st.markdown("---")

# Filtres
st.subheader("🔍 Filtres")

col1, col2 = st.columns(2)

with col1:
    # Filtre par durée minimale
    min_duration = st.slider("Durée minimale (minutes)", 0, 60, 0)

with col2:
    # Tri
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

# Trier les matchs
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
