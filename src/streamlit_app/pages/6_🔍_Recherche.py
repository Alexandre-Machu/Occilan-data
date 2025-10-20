"""
Page: Recherche de Joueur/Équipe
Permet de rechercher un joueur ou une équipe et afficher ses statistiques détaillées
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.data_manager import EditionDataManager, MultiEditionManager

st.set_page_config(page_title="Recherche - OcciLan Stats", page_icon="🔍", layout="wide")

# Helper function for champion icons
def get_champion_icon_url(champion_name: str) -> str:
    """Get Data Dragon champion icon URL"""
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
        "DrMundo": "DrMundo",
        "MonkeyKing": "MonkeyKing"
    }
    corrected_name = champion_name_mapping.get(champion_name, champion_name)
    return f"https://ddragon.leagueoflegends.com/cdn/15.20.1/img/champion/{corrected_name}.png"

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* KPI Cards */
    .stat-card {
        background: linear-gradient(135deg, #1a1d24 0%, #0f1116 100%);
        border: 1px solid rgba(255,75,75,0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .stat-label {
        color: #9fb0c6;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .stat-value {
        color: #e6eef6;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .stat-subtitle {
        color: #9fb0c6;
        font-size: 14px;
    }
    
    /* Champion icon */
    .champion-icon {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        margin: 2px;
        border: 1px solid rgba(255,255,255,0.1);
        vertical-align: middle;
    }
    
    /* Win/Loss badges */
    .win-badge {
        background: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .lose-badge {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

multi_manager = MultiEditionManager()
available_editions = multi_manager.list_editions()

with st.sidebar:
    st.title("🎮 OcciLan Stats")
    
    with st.expander("📂 Sélection d'édition", expanded=True):
        if not available_editions:
            st.info("💡 Aucune édition disponible")
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
                key="edition_selector_search"
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

st.title("🔍 Recherche de Joueur/Équipe")

if not available_editions or not selected_edition:
    st.warning("⚠️ Veuillez d'abord sélectionner une édition")
    st.stop()

edition_manager = EditionDataManager(selected_edition)

# Load data
team_stats_path = edition_manager.edition_path / "team_stats.json"
match_details_path = edition_manager.edition_path / "match_details.json"

if not team_stats_path.exists():
    st.warning("⚠️ Fichier team_stats.json introuvable")
    st.stop()

with open(team_stats_path, "r", encoding="utf-8") as f:
    team_stats_data = json.load(f)

# Load match details if available
match_details = {}
if match_details_path.exists():
    with open(match_details_path, "r", encoding="utf-8") as f:
        match_details = json.load(f)

# Create player -> team mapping
player_to_team = {}
for team_name, team_data in team_stats_data.items():
    players = team_data.get("players", {})
    for player_name in players.keys():
        player_to_team[player_name] = team_name

# Extract all players and teams
all_players = []
all_teams = list(team_stats_data.keys())

for team_name, team_data in team_stats_data.items():
    players_dict = team_data.get("players", {})
    for player_name, pstats in players_dict.items():
        all_players.append({
            "name": player_name,
            "team": team_name,
            "stats": pstats
        })

# Search type selector
search_type = st.radio(
    "Type de recherche",
    options=["👤 Joueur", "🏆 Équipe"],
    horizontal=True
)

if search_type == "👤 Joueur":
    # Player search
    st.markdown("---")
    
    player_names = [p["name"] for p in all_players]
    
    # Vérifier si un joueur a été présélectionné depuis une autre page
    default_player = st.session_state.get("search_player", "")
    if default_player and default_player not in player_names:
        default_player = ""  # Reset si le joueur n'existe pas
    
    selected_player_name = st.selectbox(
        "Rechercher un joueur",
        options=[""] + sorted(player_names),
        format_func=lambda x: "Sélectionner un joueur..." if x == "" else x,
        index=sorted([""] + player_names).index(default_player) if default_player else 0
    )
    
    # Clear session state après utilisation
    if "search_player" in st.session_state:
        del st.session_state["search_player"]
    
    if selected_player_name:
        # Find player data
        player_data = next((p for p in all_players if p["name"] == selected_player_name), None)
        
        if player_data:
            pstats = player_data["stats"]
            team_name = player_data["team"]
            
            st.markdown("---")
            st.markdown(f"## 👤 Statistiques de {selected_player_name}")
            st.caption(f"**Équipe:** {team_name}")
            
            # Main stats KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                kda = pstats.get("average_kda", 0)
                kills = pstats.get("average_kills", 0)
                deaths = pstats.get("average_deaths", 0)
                assists = pstats.get("average_assists", 0)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">KDA</div>
                    <div class="stat-value">{kda:.2f}</div>
                    <div class="stat-subtitle">{kills:.1f}/{deaths:.1f}/{assists:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_kills = pstats.get("average_kills", 0)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">KILLS MOYEN</div>
                    <div class="stat-value">{avg_kills:.1f}</div>
                    <div class="stat-subtitle">par partie</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                cs_per_min = pstats.get("average_cs_per_minute", 0)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">CS/MIN</div>
                    <div class="stat-value">{cs_per_min:.1f}</div>
                    <div class="stat-subtitle">par partie</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                vision = pstats.get("average_vision_score", 0)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">VISION SCORE</div>
                    <div class="stat-value">{vision:.1f}</div>
                    <div class="stat-subtitle">par partie</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Champions section
            st.markdown("---")
            st.markdown("### 🎮 Champions les plus joués")
            
            champions = pstats.get("champions_played", [])
            if champions:
                st.markdown("#### Pool de champions")
                
                # Display all champions in rows of 10
                champs_html = '<div style="margin: 20px 0;">'
                for i, champ in enumerate(champions):
                    if i > 0 and i % 10 == 0:
                        champs_html += '<br/>'
                    icon_url = get_champion_icon_url(champ)
                    champs_html += f'<img src="{icon_url}" class="champion-icon" title="{champ}" alt="{champ}">'
                champs_html += '</div>'
                
                st.markdown(champs_html, unsafe_allow_html=True)
                st.caption(f"**{len(champions)} champions** joués")
                
                # Champion statistics from match details
                if match_details:
                    # Collect champion stats
                    champion_stats = {}
                    for match_id, match_data in match_details.items():
                        participants = match_data.get("info", {}).get("participants", [])
                        for participant in participants:
                            player_name = participant.get("riotIdGameName") or participant.get("summonerName", "")
                            if player_name == selected_player_name:
                                champ = participant.get("championName", "Unknown")
                                if champ not in champion_stats:
                                    champion_stats[champ] = {"wins": 0, "losses": 0, "games": 0, "kills": 0, "deaths": 0, "assists": 0, "kda_values": []}
                                
                                champion_stats[champ]["games"] += 1
                                if participant.get("win"):
                                    champion_stats[champ]["wins"] += 1
                                else:
                                    champion_stats[champ]["losses"] += 1
                                
                                champion_stats[champ]["kills"] += participant.get("kills", 0)
                                champion_stats[champ]["deaths"] += participant.get("deaths", 0)
                                champion_stats[champ]["assists"] += participant.get("assists", 0)
                                
                                kills = participant.get("kills", 0)
                                deaths = participant.get("deaths", 0)
                                assists = participant.get("assists", 0)
                                kda = ((kills + assists) / deaths) if deaths > 0 else kills + assists
                                champion_stats[champ]["kda_values"].append(kda)
                                
                                # Calculate KP: (player kills + assists) / team total kills
                                team_id = participant.get("teamId")
                                team_kills = sum(p.get("kills", 0) for p in participants if p.get("teamId") == team_id)
                                kp = ((kills + assists) / team_kills * 100) if team_kills > 0 else 0
                                if "kp_values" not in champion_stats[champ]:
                                    champion_stats[champ]["kp_values"] = []
                                champion_stats[champ]["kp_values"].append(kp)
                                
                                break
                    
                    if champion_stats:
                        import plotly.graph_objects as go
                        import plotly.express as px
                        
                        # Prepare data for chart
                        champ_data = []
                        for champ, stats in champion_stats.items():
                            avg_kp = sum(stats.get("kp_values", [])) / len(stats.get("kp_values", [])) if stats.get("kp_values") else 0
                            champ_data.append({
                                "champion": champ,
                                "wins": stats["wins"],
                                "losses": stats["losses"],
                                "games": stats["games"],
                                "winrate": (stats["wins"] / stats["games"] * 100) if stats["games"] > 0 else 0,
                                "kda": sum(stats["kda_values"]) / len(stats["kda_values"]) if stats["kda_values"] else 0,
                                "kp": avg_kp
                            })
                        
                        # Sort by games played
                        champ_data = sorted(champ_data, key=lambda x: x["games"], reverse=True)
                        
                        # Winrate bar chart
                        st.markdown("#### Nombre de games par champion")
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            name='Victoires',
                            x=[c["champion"] for c in champ_data],
                            y=[c["wins"] for c in champ_data],
                            marker_color='#4caf50'
                        ))
                        fig.add_trace(go.Bar(
                            name='Défaites',
                            x=[c["champion"] for c in champ_data],
                            y=[c["losses"] for c in champ_data],
                            marker_color='#f44336'
                        ))
                        fig.update_layout(
                            barmode='stack',
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            height=400,
                            xaxis_title="",
                            yaxis_title="Nombre de parties",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Champion stats table - Style DataFrame like SC-Esport-Stats
                        st.markdown("#### CHAMPIONS STATS")
                        
                        import pandas as pd
                        
                        # Prepare DataFrame with HTML formatting
                        df_data = []
                        for champ in champ_data:
                            icon_url = get_champion_icon_url(champ["champion"])
                            
                            # Color classes for WR
                            if champ["winrate"] >= 60:
                                wr_color = "#66bb6a"
                            elif champ["winrate"] >= 40:
                                wr_color = "#ffa726"
                            else:
                                wr_color = "#ef5350"
                            
                            df_data.append({
                                "CHAMPION": f'<img src="{icon_url}" width="30" height="30" style="border-radius: 50%; vertical-align: middle; margin-right: 8px;"> {champ["champion"]}',
                                "GAMES": champ["games"],
                                "WR": f'<span style="color: {wr_color}; font-weight: 600;">{champ["winrate"]:.1f}%</span>',
                                "KDA": f'<span style="color: #ffc107; font-weight: 600;">{champ["kda"]:.2f}</span>',
                                "KP": f'<span style="color: #ff9800; font-weight: 600;">{champ["kp"]:.1f}%</span>'
                            })
                        
                        df_champ = pd.DataFrame(df_data)
                        
                        # Custom CSS for the table
                        st.markdown("""
                        <style>
                            .dataframe {
                                width: 100%;
                                border-collapse: separate;
                                border-spacing: 0;
                                background: rgb(17, 23, 31);
                                border-radius: 8px;
                                overflow: hidden;
                            }
                            .dataframe th {
                                background: rgb(17, 23, 31) !important;
                                padding: 14px 16px !important;
                                color: rgb(136, 144, 160) !important;
                                font-size: 11px !important;
                                font-weight: 600 !important;
                                text-transform: uppercase;
                                letter-spacing: 0.5px;
                                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
                                text-align: left !important;
                            }
                            .dataframe td {
                                padding: 14px 16px !important;
                                font-size: 14px !important;
                                color: rgb(230, 234, 241) !important;
                                border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
                            }
                            .dataframe tbody tr:hover {
                                background: rgba(255, 255, 255, 0.03) !important;
                            }
                            .dataframe img {
                                vertical-align: middle;
                                margin-right: 10px;
                                border-radius: 50%;
                            }
                            .dataframe td:nth-child(2),
                            .dataframe td:nth-child(3),
                            .dataframe td:nth-child(4),
                            .dataframe td:nth-child(5),
                            .dataframe th:nth-child(2),
                            .dataframe th:nth-child(3),
                            .dataframe th:nth-child(4),
                            .dataframe th:nth-child(5) {
                                text-align: center !important;
                            }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Display as HTML table
                        st.markdown(df_champ.to_html(escape=False, index=False, classes='dataframe'), unsafe_allow_html=True)
            
            # Match history (if available)
            if match_details:
                st.markdown("---")
                st.markdown("### 📋 Historique des parties")
                
                # Filter matches for this player
                player_matches = []
                for match_id, match_data in match_details.items():
                    # Get participants from info section
                    participants = match_data.get("info", {}).get("participants", [])
                    
                    for participant in participants:
                        player_name = participant.get("riotIdGameName") or participant.get("summonerName", "")
                        if player_name == selected_player_name:
                            # Found the player in this match
                            player_matches.append({
                                "match_id": match_id,
                                "match_data": match_data,
                                "player_data": participant
                            })
                            break
                
                if player_matches:
                    # Sort by date (most recent first)
                    player_matches = sorted(
                        player_matches,
                        key=lambda x: x["match_data"].get("info", {}).get("gameCreation", 0),
                        reverse=True
                    )
                    
                    match_rows = []
                    for match_info in player_matches[:25]:  # Last 25 matches
                        player_data = match_info["player_data"]
                        match_data = match_info["match_data"]
                        info = match_data.get("info", {})
                        
                        champion = player_data.get("championName", "Unknown")
                        win = player_data.get("win", False)
                        kills = player_data.get("kills", 0)
                        deaths = player_data.get("deaths", 0)
                        assists = player_data.get("assists", 0)
                        kda_val = ((kills + assists) / deaths) if deaths > 0 else kills + assists
                        cs = player_data.get("totalMinionsKilled", 0) + player_data.get("neutralMinionsKilled", 0)
                        game_duration = info.get("gameDuration", 0)
                        cs_per_min_match = (cs / (game_duration / 60)) if game_duration > 0 else 0
                        vision_score = player_data.get("visionScore", 0)
                        gold = player_data.get("goldEarned", 0)
                        kp = player_data.get("challenges", {}).get("killParticipation", 0) * 100
                        damage = player_data.get("totalDamageDealtToChampions", 0)
                        
                        # Calculate gold efficiency: (damage / gold) * 1000
                        gold_efficiency = round((damage / gold) * 1000, 1) if gold > 0 else 0
                        
                        # Get game date
                        game_creation = info.get("gameCreation", 0)
                        from datetime import datetime
                        game_date = datetime.fromtimestamp(game_creation / 1000).strftime("%d/%m/%Y") if game_creation > 0 else "N/A"
                        
                        # Find opponent team
                        opponent = "N/A"
                        player_team_id = player_data.get("teamId")
                        if player_team_id:
                            # Find an opponent player (different teamId)
                            participants = info.get("participants", [])
                            for participant in participants:
                                if participant.get("teamId") != player_team_id:
                                    opponent_name = participant.get("riotIdGameName") or participant.get("summonerName", "")
                                    if opponent_name in player_to_team:
                                        opponent = player_to_team[opponent_name]
                                        break
                        
                        match_rows.append({
                            "date": game_date,
                            "champion": champion,
                            "win": win,
                            "opponent": opponent,
                            "kills": kills,
                            "deaths": deaths,
                            "assists": assists,
                            "kda": kda_val,
                            "kp": kp,
                            "cs_per_min": cs_per_min_match,
                            "vision": vision_score,
                            "gold": gold,
                            "duration": game_duration,
                            "damage": damage,
                            "gold_efficiency": gold_efficiency
                        })
                    
                    if match_rows:
                        # Create DataFrame like SC-Esport-Stats
                        df_matches = []
                        for match in match_rows:
                            icon_url = get_champion_icon_url(match["champion"])
                            duration_min = int(match["duration"] // 60)
                            duration_sec = int(match["duration"] % 60)
                            vision_per_min = round(match["vision"] / duration_min, 1) if duration_min > 0 else 0
                            
                            # Color classes
                            kp_color = "#66bb6a" if match["kp"] >= 60 else "#ffa726" if match["kp"] >= 40 else "#ef5350"
                            cs_color = "#42a5f5" if match["cs_per_min"] >= 7 else "#90caf9"
                            gold_color = "#ffc107"
                            
                            df_matches.append({
                                "DATE": match["date"],
                                "CHAMPION": f'<img src="{icon_url}" width="30" height="30" style="border-radius: 50%; vertical-align: middle; margin-right: 8px;"> {match["champion"]}',
                                "W/L": "✅ Win" if match["win"] else "❌ Lose",
                                "VS": match["opponent"],
                                "GAME": 1,
                                "DURÉE": f"{duration_min}:{duration_sec:02d}",
                                "KDA": f'{match["kills"]}/{match["deaths"]}/{match["assists"]} <span style="color: #ffc107; font-weight: 600;">[{match["kda"]:.2f}]</span>',
                                "KP": f'<span style="color: {kp_color}; font-weight: 600;">{match["kp"]:.1f}%</span>',
                                "CS/MIN": f'<span style="color: {cs_color}; font-weight: 600;">{match["cs_per_min"]:.1f}</span>',
                                "VISION": f'{match["vision"]} <span style="color: #888; font-size: 11px;">({vision_per_min}/{duration_min})</span> <span style="color: #4caf50; font-size: 11px;">100%</span>',
                                "GOLD EFF": f'<span style="color: {gold_color}; font-weight: 600;">{match["gold_efficiency"]:.1f}</span>'
                            })
                        
                        df = pd.DataFrame(df_matches)
                        
                        # Display with custom CSS (same as champion stats table)
                        st.markdown(df.to_html(escape=False, index=False, classes='dataframe'), unsafe_allow_html=True)
                    else:
                        st.info("Aucune partie trouvée dans les détails")
                else:
                    st.info("Aucune partie trouvée pour ce joueur")
            else:
                st.info("Les détails des matchs ne sont pas disponibles")

else:
    # Team search
    st.markdown("---")
    
    selected_team = st.selectbox(
        "Rechercher une équipe",
        options=[""] + sorted(all_teams),
        format_func=lambda x: "Sélectionner une équipe..." if x == "" else x
    )
    
    if selected_team:
        team_data = team_stats_data.get(selected_team, {})
        
        st.markdown("---")
        st.markdown(f"## 🏆 Statistiques de {selected_team}")
        
        # Team stats
        team_wins = team_data.get("wins", 0)
        team_losses = team_data.get("losses", 0)
        total_games = team_wins + team_losses
        win_rate = (team_wins / total_games * 100) if total_games > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Victoires", team_wins)
        with col2:
            st.metric("Défaites", team_losses)
        with col3:
            st.metric("Total Parties", total_games)
        with col4:
            st.metric("Winrate", f"{win_rate:.1f}%")
        
        # Players table
        st.markdown("---")
        st.markdown("### 👥 Roster de l'équipe")
        
        players_dict = team_data.get("players", {})
        if players_dict:
            player_rows = []
            for player_name, pstats in players_dict.items():
                player_rows.append({
                    "Joueur": player_name,
                    "KDA": f"{pstats.get('average_kda', 0):.2f}",
                    "Kills/G": f"{pstats.get('average_kills', 0):.1f}",
                    "Deaths/G": f"{pstats.get('average_deaths', 0):.1f}",
                    "Assists/G": f"{pstats.get('average_assists', 0):.1f}",
                    "CS/min": f"{pstats.get('average_cs_per_minute', 0):.1f}",
                    "Vision/G": f"{pstats.get('average_vision_score', 0):.1f}",
                    "Champions": len(pstats.get("champions_played", []))
                })
            
            df_players = pd.DataFrame(player_rows)
            st.dataframe(df_players, use_container_width=True, hide_index=True)
