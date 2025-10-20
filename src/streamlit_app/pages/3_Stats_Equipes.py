"""
Page: Stats Équipes
Affiche les statistiques détaillées de chaque équipe avec des cartes KPI et un tableau des joueurs
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.data_manager import EditionDataManager, MultiEditionManager

st.set_page_config(page_title="Stats Équipes - OcciLan Stats", page_icon="🏆", layout="wide")

# Helper function for champion icons
def get_champion_icon_url(champion_name: str, size: int = 48) -> str:
    """Get Data Dragon champion icon URL"""
    # Champion name corrections for Data Dragon API
    champion_name_mapping = {
        "MonkeyKing": "Wukong",  # API retourne MonkeyKing, DataDragon attend Wukong
        "FiddleSticks": "Fiddlesticks",
        "Nunu": "Nunu",
        "RekSai": "RekSai",
        "KSante": "KSante",
        "Renata": "Renata",
        "BelVeth": "Belveth",
        "KhaZix": "Khazix",
        "VelKoz": "Velkoz",
        "ChoGath": "Chogath",
        "KaiSa": "Kaisa",
        "LeBlanc": "Leblanc",
        "JarvanIV": "JarvanIV",
        "XinZhao": "XinZhao",
        "MasterYi": "MasterYi",
        "MissFortune": "MissFortune",
        "TahmKench": "TahmKench",
        "TwistedFate": "TwistedFate",
        "AurelionSol": "AurelionSol",
        "DrMundo": "DrMundo"
    }
    
    # Use the mapping if champion name exists in it, otherwise use as-is
    corrected_name = champion_name_mapping.get(champion_name, champion_name)
    
    # Latest version - updated to 14.24.1 to include Ambessa
    return f"https://ddragon.leagueoflegends.com/cdn/14.24.1/img/champion/{corrected_name}.png"

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* KPI Cards */
    .kpi-grid { 
        display: grid; 
        grid-template-columns: repeat(4, minmax(0, 1fr)); 
        gap: 12px; 
        margin-bottom: 20px;
    }
    .kpi-grid.three { 
        grid-template-columns: repeat(3, minmax(0, 1fr)); 
    }
    .kpi-card { 
        background: linear-gradient(180deg, #0f1116 0%, #0b0d10 100%); 
        border: 1px solid rgba(255,255,255,0.06); 
        border-radius: 12px; 
        padding: 16px; 
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255,75,75,0.3);
    }
    .kpi-title { 
        color: #9fb0c6; 
        font-size: 13px; 
        margin-bottom: 6px; 
        font-weight: 500;
    }
    .kpi-value { 
        color: #e6eef6; 
        font-size: 28px; 
        font-weight: 800; 
        letter-spacing: 0.2px; 
    }
    .kpi-emoji { 
        margin-right: 6px; 
        font-size: 18px;
    }
    
    /* Player Table */
    .player-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', 'Helvetica', 'Arial', sans-serif;
        margin-top: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border-radius: 8px;
        overflow: hidden;
    }
    .player-table thead tr {
        background: #0b1220;
        color: #9fb0c6;
    }
    .player-table th {
        padding: 16px 14px;
        text-align: left;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .player-table tbody tr:nth-child(even) {
        background: #0f1113;
    }
    .player-table tbody tr:nth-child(odd) {
        background: #0b0d10;
    }
    .player-table tbody tr {
        border-top: 1px solid rgba(255,255,255,0.05);
        transition: background 0.2s;
    }
    .player-table tbody tr:hover {
        background: #1a1d24 !important;
    }
    .player-table td {
        padding: 16px 14px;
        color: #e6eef6;
    }
    
    /* Role badges */
    .role-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 12px;
        color: #071019;
    }
    .role-top { background: #ff6b6b; }
    .role-jgl { background: #2ecc71; }
    .role-mid { background: #f39c12; }
    .role-adc { background: #f1c40f; }
    .role-sup { background: #3498db; }
    
    /* KDA colors */
    .kda-excellent { color: #2ecc71; font-weight: 700; }
    .kda-good { color: #a3e635; font-weight: 700; }
    .kda-average { color: #facc15; font-weight: 700; }
    .kda-poor { color: #ef4444; font-weight: 700; }
    
    /* Champion icons */
    .champion-icon {
        width: 28px;
        height: 28px;
        border-radius: 4px;
        border: 1px solid rgba(255,255,255,0.1);
        margin: 2px;
        transition: all 0.2s;
        vertical-align: middle;
    }
    .champion-icon:hover {
        border-color: rgba(255,75,75,0.5);
        transform: scale(1.15);
    }
    .champion-pool {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        padding: 10px;
        background: rgba(0,0,0,0.2);
        border-radius: 6px;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

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
        # Initialiser selected_edition dans session_state si pas déjà fait
        if "selected_edition" not in st.session_state:
            st.session_state.selected_edition = available_editions[0] if available_editions else None
        
        # Trouver l'index de l'édition sélectionnée
        default_index = 0
        if st.session_state.selected_edition in available_editions:
            default_index = available_editions.index(st.session_state.selected_edition)
        
        selected_edition = st.selectbox(
            "Édition",
            available_editions,
            index=default_index,
            format_func=lambda x: f"Edition {x}",
            label_visibility="collapsed",
            key="edition_selector_teams"
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
    st.page_link("pages/3_Stats_Equipes.py", label="🏆 Stats Équipes")
    st.page_link("pages/4_Stats_Joueurs.py", label="👤 Stats Joueurs")
    st.page_link("pages/5_Recherche.py", label="🔍 Recherche")
    st.page_link("pages/9_🔧_Admin.py", label="🔧 Admin")
    st.markdown("---")
    st.caption("🎮 OcciLan Stats v2.0")
    st.markdown("---")
    st.caption("🎮 OcciLan Stats v2.0")

# ============================================================================
# MAIN
# ============================================================================

st.title("🏆 Statistiques par Équipe")

if not available_editions or not selected_edition:
    st.warning("⚠️ Veuillez d'abord sélectionner une édition")
    st.stop()

edition_manager = EditionDataManager(selected_edition)

# Load data
teams_with_puuid = edition_manager.load_teams_with_puuid()

# Try to load team_stats.json (old format from edition 6)
import json
data_dir = Path(__file__).parent.parent.parent.parent / "data" / "editions" / f"edition_{selected_edition}"
team_stats_path = data_dir / "team_stats.json"

if not team_stats_path.exists():
    st.warning("⚠️ Fichier team_stats.json introuvable")
    st.info("💡 Ce fichier est nécessaire pour afficher les statistiques par équipe")
    st.stop()

with open(team_stats_path, "r", encoding="utf-8") as f:
    team_stats_data = json.load(f)

if not team_stats_data:
    st.warning("⚠️ Aucune statistique d'équipe disponible")
    st.stop()

# Team selector
team_names = sorted(team_stats_data.keys())
selected_team = st.selectbox("🏆 Sélectionnez une équipe", team_names, key="team_selector")

if not selected_team:
    st.stop()

# Get team data from team_stats.json structure
team_entry = team_stats_data.get(selected_team, {})
team_data = team_entry.get("team_stats", {})
player_stats_dict = team_entry.get("players", {})
team_info = teams_with_puuid.get(selected_team, {})

# ============================================================================
# TEAM KPIs
# ============================================================================

st.markdown("---")
st.markdown("### 📊 Stats Équipe")

def kpi_card(title, value, emoji):
    return f'''
    <div class="kpi-card">
        <div class="kpi-title">
            <span class="kpi-emoji">{emoji}</span>{title}
        </div>
        <div class="kpi-value">{value}</div>
    </div>
    '''

# Format duration helper
def format_duration(seconds):
    if not seconds:
        return "—"
    minutes = int(seconds / 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

# Main KPIs (adapté au format team_stats.json)
games_played = team_data.get("total_games", 0)
wins = team_data.get("wins", 0)
losses = team_data.get("losses", 0)
winrate = team_data.get("winrate", 0)
avg_duration = team_data.get("average_game_duration", 0) * 60  # Convert minutes to seconds

# Main KPIs row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎮 Matchs joués", games_played or "—")
with col2:
    st.metric("🏆 Victoires", wins or "—")
with col3:
    st.metric("❌ Défaites", losses or "—")
with col4:
    st.metric("🔥 Winrate", f"{winrate:.1f}%" if winrate else "—")

st.markdown("<br>", unsafe_allow_html=True)

# Duration KPIs (calculate totals from players)
total_kills = sum(p.get("total_kills", 0) for p in player_stats_dict.values())
total_deaths = sum(p.get("total_deaths", 0) for p in player_stats_dict.values())

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⏱️ Durée moyenne", format_duration(avg_duration))
with col2:
    st.metric("⚔️ Total kills", total_kills or "—")
with col3:
    st.metric("💀 Total deaths", total_deaths or "—")

# ============================================================================
# PLAYER STATS TABLE
# ============================================================================

st.markdown("---")
st.markdown("### 👥 Statistiques des Joueurs")

# Get players for this team
team_players = team_info.get("players", [])

if not team_players:
    st.warning("⚠️ Aucun joueur trouvé pour cette équipe")
    st.stop()

# Role mapping for badges
role_badges = {
    "TOP": {"label": "🗻 Top", "class": "role-top"},
    "JGL": {"label": "🐾 Jungle", "class": "role-jgl"},
    "MID": {"label": "🎯 Mid", "class": "role-mid"},
    "ADC": {"label": "🏹 ADC", "class": "role-adc"},
    "SUP": {"label": "🛡️ Supp", "class": "role-sup"},
}

def get_kda_class(kda):
    """Return CSS class based on KDA value"""
    try:
        kda_val = float(kda)
        if kda_val >= 5:
            return "kda-excellent"
        elif kda_val >= 3:
            return "kda-good"
        elif kda_val >= 2:
            return "kda-average"
        else:
            return "kda-poor"
    except:
        return ""

# Build HTML table
table_html = '<table class="player-table">'
table_html += '<thead><tr>'
headers = ["Position", "Joueur", "KDA", "Kills/G", "Deaths/G", "Assists/G", "CS/min", "Vision/G", "Champions"]
for h in headers:
    table_html += f'<th>{h}</th>'
table_html += '</tr></thead><tbody>'

# Get player stats
for player in team_players:
    player_full_name = f"{player.get('gameName', 'Unknown')}#{player.get('tagLine', '???')}"
    player_short_name = player.get('gameName', 'Unknown')
    role = player.get("role", "")
    
    # Find player stats (try both full name and short name)
    pstats = player_stats_dict.get(player_short_name, player_stats_dict.get(player_full_name, {}))
    
    if not pstats:
        continue
    
    # Role badge
    badge_info = role_badges.get(role, {"label": role, "class": "role-badge"})
    role_html = f'<span class="role-badge {badge_info["class"]}">{badge_info["label"]}</span>'
    
    # Stats (adapted to team_stats.json format)
    kda = pstats.get("average_kda", 0)
    kda_class = get_kda_class(kda)
    kills_per_game = pstats.get("average_kills", 0)
    deaths_per_game = pstats.get("average_deaths", 0)
    assists_per_game = pstats.get("average_assists", 0)
    cs_per_min = pstats.get("average_cs_per_minute", 0)  # Note: different field name
    vision_per_game = pstats.get("average_vision_score", 0)
    
    # Get champions - Display ALL champions in rows of 5
    champions = pstats.get("champions_played", [])
    champions_html = ''
    if champions:
        # Create rows of 5 champions each
        for i, champ in enumerate(champions):
            # Add line break after every 5 champions (except the first row)
            if i > 0 and i % 5 == 0:
                champions_html += '<br/>'
            
            icon_url = get_champion_icon_url(champ)
            champions_html += f'<img src="{icon_url}" class="champion-icon" title="{champ}" alt="{champ}">'
    
    table_html += '<tr>'
    table_html += f'<td>{role_html}</td>'
    table_html += f'<td><strong>{player.get("gameName", "Unknown")}</strong><br/><span style="color:#9fb0c6;font-size:11px">#{player.get("tagLine", "???")}</span></td>'
    table_html += f'<td><span class="{kda_class}">{kda:.2f}</span></td>'
    table_html += f'<td>{kills_per_game:.1f}</td>'
    table_html += f'<td>{deaths_per_game:.1f}</td>'
    table_html += f'<td>{assists_per_game:.1f}</td>'
    table_html += f'<td>{cs_per_min:.1f}</td>'
    table_html += f'<td>{vision_per_game:.1f}</td>'
    table_html += f'<td>{champions_html}</td>'
    table_html += '</tr>'

table_html += '</tbody></table>'

st.markdown(table_html, unsafe_allow_html=True)

# Boutons cliquables pour voir les profils des joueurs de l'équipe
st.markdown("---")
st.markdown("#### 👁️ Voir le profil des joueurs")
cols = st.columns(5)
for idx, player in enumerate(team_players):
    player_short_name = player.get('gameName', 'Unknown')
    col_idx = idx % 5
    with cols[col_idx]:
        if st.button(f"👤 {player_short_name}", key=f"view_profile_team_1_{selected_team}_{idx}", use_container_width=True):
            st.session_state["search_player"] = player_short_name
            st.switch_page("pages/5_Recherche.py")

