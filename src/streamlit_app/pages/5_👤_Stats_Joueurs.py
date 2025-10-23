"""
Page: Stats Joueurs
Affiche les statistiques individuelles des joueurs avec classements et comparaisons
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.data_manager import EditionDataManager, MultiEditionManager

st.set_page_config(page_title="Stats Joueurs - OcciLan Stats", page_icon="👤", layout="wide")

# Helper function for champion icons
def get_champion_icon_url(champion_name: str, size: int = 48) -> str:
    """Get Data Dragon champion icon URL"""
    # Champion name corrections for Data Dragon API
    # Data Dragon utilise les clés internes de Riot
    champion_name_mapping = {
        "Wukong": "MonkeyKing",  # Wukong → MonkeyKing pour Data Dragon
        "MonkeyKing": "MonkeyKing",  # Déjà correct
        "FiddleSticks": "Fiddlesticks",
        "Nunu": "Nunu",
        "Nunu & Willump": "Nunu",
        "RekSai": "RekSai",
        "Rek'Sai": "RekSai",
        "KSante": "KSante",
        "K'Sante": "KSante",
        "Renata": "Renata",
        "Renata Glasc": "Renata",
        "BelVeth": "Belveth",
        "Bel'Veth": "Belveth",
        "KhaZix": "Khazix",
        "Kha'Zix": "Khazix",
        "VelKoz": "Velkoz",
        "Vel'Koz": "Velkoz",
        "ChoGath": "Chogath",
        "Cho'Gath": "Chogath",
        "KaiSa": "Kaisa",
        "Kai'Sa": "Kaisa",
        "LeBlanc": "Leblanc",
        "JarvanIV": "JarvanIV",
        "Jarvan IV": "JarvanIV",
        "XinZhao": "XinZhao",
        "Xin Zhao": "XinZhao",
        "MasterYi": "MasterYi",
        "Master Yi": "MasterYi",
        "MissFortune": "MissFortune",
        "Miss Fortune": "MissFortune",
        "TahmKench": "TahmKench",
        "Tahm Kench": "TahmKench",
        "TwistedFate": "TwistedFate",
        "Twisted Fate": "TwistedFate",
        "AurelionSol": "AurelionSol",
        "Aurelion Sol": "AurelionSol",
        "DrMundo": "DrMundo",
        "Dr. Mundo": "DrMundo",
        "KogMaw": "KogMaw",
        "Kog'Maw": "KogMaw"
    }
    
    # Use the mapping if champion name exists in it, otherwise use as-is
    corrected_name = champion_name_mapping.get(champion_name, champion_name)
    
    # Latest version - updated to 15.20.1 to include Yunara
    return f"https://ddragon.leagueoflegends.com/cdn/15.20.1/img/champion/{corrected_name}.png"

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Player card */
    .player-card {
        background: linear-gradient(135deg, #1a1d24 0%, #0f1116 100%);
        border: 1px solid rgba(255,75,75,0.1);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .player-card:hover {
        border-color: rgba(255,75,75,0.3);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255,75,75,0.15);
    }
    .player-name {
        font-size: 20px;
        font-weight: 700;
        color: #e6eef6;
        margin-bottom: 8px;
    }
    .player-team {
        color: #9fb0c6;
        font-size: 14px;
        margin-bottom: 12px;
    }
    .stat-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 12px;
        margin-top: 12px;
    }
    .stat-item {
        text-align: center;
    }
    .stat-label {
        color: #9fb0c6;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .stat-value {
        color: #e6eef6;
        font-size: 18px;
        font-weight: 700;
    }
    
    /* Rankings */
    .rank-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 12px;
        margin-right: 8px;
    }
    .rank-1 { background: #FFD700; color: #000; }
    .rank-2 { background: #C0C0C0; color: #000; }
    .rank-3 { background: #CD7F32; color: #000; }
    .rank-other { background: #374151; color: #9fb0c6; }
    
    /* Champion icons */
    .champion-icon {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        border: 2px solid rgba(255,255,255,0.1);
        margin: 2px;
        transition: all 0.2s;
    }
    .champion-icon:hover {
        border-color: rgba(255,75,75,0.5);
        transform: scale(1.1);
    }
    .champion-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 12px;
        background: rgba(0,0,0,0.2);
        border-radius: 8px;
        margin-top: 8px;
    }
    
    /* Fix table rendering */
    div[data-testid="stMarkdownContainer"] pre {
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
    }
    div[data-testid="stMarkdownContainer"] code {
        background: transparent !important;
        color: inherit !important;
        padding: 0 !important;
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
            key="edition_selector_players"
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

# ============================================================================
# MAIN
# ============================================================================

st.title("👤 Statistiques par Joueur")

if not available_editions or not selected_edition:
    st.warning("⚠️ Veuillez d'abord sélectionner une édition")
    st.stop()

edition_manager = EditionDataManager(selected_edition)

# Load data
data_dir = Path(__file__).parent.parent.parent.parent / "data" / "editions" / f"edition_{selected_edition}"
team_stats_path = data_dir / "team_stats.json"

if not team_stats_path.exists():
    st.warning("⚠️ Fichier team_stats.json introuvable")
    st.stop()

with open(team_stats_path, "r", encoding="utf-8") as f:
    team_stats_data = json.load(f)

# Extract all players
all_players = []
for team_name, team_data in team_stats_data.items():
    players_dict = team_data.get("players", {})
    for player_name, pstats in players_dict.items():
        player_entry = {
            "name": player_name,
            "team": team_name,
            **pstats
        }
        all_players.append(player_entry)

if not all_players:
    st.warning("⚠️ Aucune statistique de joueur disponible")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(all_players)

# ============================================================================
# FILTERS AND SORTING
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    sort_by = st.selectbox(
        "📊 Trier par",
        ["KDA", "Kills/G", "Deaths/G", "Assists/G", "CS/min", "Vision/G", "Champions joués"],
        key="sort_selector"
    )

with col2:
    filter_team = st.selectbox(
        "🏆 Filtrer par équipe",
        ["Toutes les équipes"] + sorted(df["team"].unique().tolist()),
        key="team_filter"
    )

with col3:
    min_games = st.number_input(
        "🎮 Matchs minimum",
        min_value=0,
        max_value=int(df["total_kills"].count()) if "total_kills" in df.columns else 20,
        value=0,
        key="min_games_filter"
    )

# Apply filters
filtered_df = df.copy()
if filter_team != "Toutes les équipes":
    filtered_df = filtered_df[filtered_df["team"] == filter_team]

# Sort mapping
sort_mapping = {
    "KDA": "average_kda",
    "Kills/G": "average_kills",
    "Deaths/G": "average_deaths",
    "Assists/G": "average_assists",
    "CS/min": "average_cs_per_min",
    "Vision/G": "average_vision_score",
    "Champions joués": "unique_champions_played"
}

sort_column = sort_mapping.get(sort_by, "average_kda")
if sort_column in filtered_df.columns:
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=False)

# ============================================================================
# TOP PLAYERS PODIUM
# ============================================================================

st.markdown("---")
st.markdown(f"### 🏆 Top 3 - {sort_by}")

if len(filtered_df) >= 3:
    col1, col2, col3 = st.columns(3)
    
    for idx, (i, col) in enumerate(zip([1, 0, 2], [col2, col1, col3])):  # Gold in middle
        if i < len(filtered_df):
            player = filtered_df.iloc[i]
            rank_class = f"rank-{i+1}"
            
            with col:
                medal = ["🥇", "🥈", "🥉"][i]
                # Format the value properly
                stat_value = player.get(sort_column, 0)
                if isinstance(stat_value, (int, float)):
                    formatted_value = f"{stat_value:.2f}"
                else:
                    formatted_value = str(stat_value)
                
                st.markdown(f"""
                <div class="player-card">
                    <div style="text-align: center; font-size: 40px; margin-bottom: 8px;">{medal}</div>
                    <div class="player-name" style="text-align: center;">{player['name']}</div>
                    <div class="player-team" style="text-align: center;">{player['team']}</div>
                    <div style="text-align: center; margin-top: 12px;">
                        <div class="stat-label">{sort_by}</div>
                        <div class="stat-value" style="font-size: 28px; color: #FF4B4B;">
                            {formatted_value}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# FULL RANKINGS
# ============================================================================

st.markdown("---")
st.markdown("### 📋 Classement Complet")

# Build table HTML
table_html = '''
<table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; margin-top: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden;">
    <thead>
        <tr style="background: #0b1220; color: #9fb0c6;">
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Position</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Joueur</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">KDA</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Kills/G</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Deaths/G</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Assists/G</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">CS/min</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Vision/G</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Champions</th>
        </tr>
    </thead>
    <tbody>
'''

for idx, (_, player) in enumerate(filtered_df.iterrows(), 1):
    rank_class = "rank-other"
    if idx <= 3:
        rank_class = f"rank-{idx}"
    
    # Get KDA color
    kda = player.get('average_kda', 0)
    if kda >= 5:
        kda_color = "#2ecc71"
    elif kda >= 3:
        kda_color = "#a3e635"
    elif kda >= 2:
        kda_color = "#facc15"
    else:
        kda_color = "#ef4444"
    
    # Background color
    bg_color = "#0f1113" if idx % 2 == 0 else "#0b0d10"
    
    # Champions icons - Display ALL champions in rows of 5
    champions = player.get('champions_played', [])
    champions_html = ''
    if champions:
        # Create rows of 5 champions each
        for i, champ in enumerate(champions):
            # Add line break after every 5 champions (except the first row)
            if i > 0 and i % 5 == 0:
                champions_html += '<br/>'
            
            icon_url = get_champion_icon_url(champ)
            champions_html += f'<img src="{icon_url}" class="champion-icon" title="{champ}" alt="{champ}" style="width: 32px; height: 32px; border-radius: 4px; margin: 2px; border: 1px solid rgba(255,255,255,0.1);">'
    
    table_html += f'''
        <tr style="background: {bg_color}; border-top: 1px solid rgba(255,255,255,0.05); transition: background 0.2s;" onmouseover="this.style.background='#1a1d24'" onmouseout="this.style.background='{bg_color}'">
            <td style="padding: 16px 14px; color: #e6eef6;"><span class="rank-badge {rank_class}">#{idx}</span></td>
            <td style="padding: 16px 14px; color: #e6eef6;">
                <strong>{player['name']}</strong><br/>
                <span style="color: #9fb0c6; font-size: 11px;">{player['team']}</span>
            </td>
            <td style="padding: 16px 14px; color: {kda_color}; font-weight: 700;">{player.get('average_kda', 0):.2f}</td>
            <td style="padding: 16px 14px; color: #e6eef6;">{player.get('average_kills', 0):.1f}</td>
            <td style="padding: 16px 14px; color: #e6eef6;">{player.get('average_deaths', 0):.1f}</td>
            <td style="padding: 16px 14px; color: #e6eef6;">{player.get('average_assists', 0):.1f}</td>
            <td style="padding: 16px 14px; color: #e6eef6;">{player.get('average_cs_per_min', 0):.1f}</td>
            <td style="padding: 16px 14px; color: #e6eef6;">{player.get('average_vision_score', 0):.1f}</td>
            <td style="padding: 16px 14px;">{champions_html}</td>
        </tr>
    '''

table_html += '''
    </tbody>
</table>
'''

# Use st.components for proper HTML rendering
import streamlit.components.v1 as components
components.html(table_html, height=3500, scrolling=True)

# Boutons cliquables pour voir les profils des joueurs
st.markdown("---")
st.markdown("### 👁️ Voir le profil d'un joueur")
cols = st.columns(5)
for idx, (_, player) in enumerate(filtered_df.iterrows()):
    col_idx = idx % 5
    with cols[col_idx]:
        if st.button(f"👤 {player['name']}", key=f"view_profile_{idx}_{player['name']}", use_container_width=True):
            st.session_state["search_player"] = player['name']
            st.switch_page("pages/6_🔍_Recherche.py")

# ============================================================================
# STATISTICS SUMMARY
# ============================================================================

st.markdown("---")
st.markdown("### 📊 Statistiques Globales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_kda = filtered_df["average_kda"].mean()
    st.metric("KDA Moyen", f"{avg_kda:.2f}")

with col2:
    avg_kills = filtered_df["average_kills"].mean()
    st.metric("Kills/G Moyen", f"{avg_kills:.1f}")

with col3:
    avg_cs = filtered_df["average_cs_per_min"].mean()
    st.metric("CS/min Moyen", f"{avg_cs:.1f}")

with col4:
    total_players = len(filtered_df)
    st.metric("Joueurs", total_players)
