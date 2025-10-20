"""
Page: Statistiques Champions
Affiche les stats des champions (picks, bans, winrates, KDA, etc.)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.data_manager import EditionDataManager, MultiEditionManager

st.set_page_config(page_title="Stats Champions - OcciLan Stats", page_icon="🐉", layout="wide")

# Custom CSS pour masquer la navigation par défaut
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Style pour les métriques */
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #7c3aed;
        margin-bottom: 1rem;
        min-height: 100px;
    }
    
    /* Colonnes de même hauteur */
    [data-testid="column"] {
        min-height: 650px;
    }
    
    /* Couleurs pour les stats */
    .winrate-high { color: #22c55e; font-weight: bold; }
    .winrate-low { color: #ef4444; font-weight: bold; }
    .kda-stat { color: #a78bfa; font-weight: bold; }
    .kp-stat { color: #34d399; font-weight: bold; }
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
            key="edition_selector_champions"
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
# CONFIGURATION
# ============================================================================

st.title("🐉 Statistiques des Champions")

if not available_editions or not selected_edition:
    st.info("👈 Sélectionnez une édition dans la sidebar")
    st.stop()

# Charger les données de l'édition
edition_manager = EditionDataManager(selected_edition)
general_stats = edition_manager.load_general_stats()

if not general_stats or "champion_stats" not in general_stats:
    st.warning("⚠️ Aucune donnée de champions disponible pour cette édition")
    st.stop()

# Extraire les stats champions
champion_data = general_stats["champion_stats"]

# Créer un DataFrame à partir des données JSON
# Structure: {"picks": {...}, "bans": {...}, "wins": {...}}
champions_list = []

all_champions = set()
all_champions.update(champion_data.get("picks", {}).keys())
all_champions.update(champion_data.get("bans", {}).keys())

for champion in all_champions:
    picks = champion_data.get("picks", {}).get(champion, 0)
    bans = champion_data.get("bans", {}).get(champion, 0)
    wins = champion_data.get("wins", {}).get(champion, 0)
    
    # Calculer le winrate
    winrate = (wins / picks * 100) if picks > 0 else 0
    
    champions_list.append({
        "Champion": champion,
        "Games": picks,
        "WR": round(winrate, 1),
        "Wins": wins,
        "Bans": bans
    })

df = pd.DataFrame(champions_list)
df = df.sort_values("Games", ascending=False).reset_index(drop=True)

# Fonction pour obtenir l'icône du champion
def get_champion_icon(champion_name):
    version = "14.23.1"
    # Nettoyer le nom du champion pour l'URL
    clean_name = champion_name.replace(" ", "").replace("'", "")
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{clean_name}.png"
    return url

st.markdown("---")

# === SECTION 1: TOP 5 STATS ===
st.header("📊 Top 5 des Champions")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🎮 Les Plus Joués")
    top_played = df.nlargest(5, 'Games')[['Champion', 'Games', 'WR']]
    
    for idx, row in top_played.iterrows():
        wr_color = "winrate-high" if row['WR'] >= 50 else "winrate-low"
        icon_url = get_champion_icon(row['Champion'])
        st.markdown(f"""
            <div class="metric-card">
                <img src="{icon_url}" class="champion-icon" style="width: 50px; height: 50px; border-radius: 50%; vertical-align: middle; margin-right: 10px;" onerror="this.style.display='none'">
                <h3 style="margin:0; color: #fff; display: inline-block;">{row['Champion']}</h3>
                <p style="margin:0.5rem 0 0 0; font-size: 1.2rem;">
                    <span style="color: #60a5fa;">{int(row['Games'])} games</span> • 
                    <span class="{wr_color}">{row['WR']}% WR</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("🚫 Les Plus Bannis")
    top_banned = df.nlargest(5, 'Bans')[['Champion', 'Bans', 'WR']]
    
    for idx, row in top_banned.iterrows():
        icon_url = get_champion_icon(row['Champion'])
        wr_color = "winrate-high" if row['WR'] >= 50 else "winrate-low"
        st.markdown(f"""
            <div class="metric-card">
                <img src="{icon_url}" class="champion-icon" style="width: 50px; height: 50px; border-radius: 50%; vertical-align: middle; margin-right: 10px;" onerror="this.style.display='none'">
                <h3 style="margin:0; color: #fff; display: inline-block;">{row['Champion']}</h3>
                <p style="margin:0.5rem 0 0 0; font-size: 1.2rem;">
                    <span style="color: #f87171;">{int(row['Bans'])} bans</span> • 
                    <span class="{wr_color}">{row['WR']}% WR</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

with col3:
    st.subheader("🏆 Meilleurs Winrates")
    # Filtre: minimum 5 games
    df_filtered = df[df['Games'] >= 5]
    
    if len(df_filtered) > 0:
        top_winrate = df_filtered.nlargest(5, 'WR')[['Champion', 'WR', 'Games']]
        
        for idx, row in top_winrate.iterrows():
            icon_url = get_champion_icon(row['Champion'])
            st.markdown(f"""
                <div class="metric-card">
                    <img src="{icon_url}" class="champion-icon" style="width: 50px; height: 50px; border-radius: 50%; vertical-align: middle; margin-right: 10px;" onerror="this.style.display='none'">
                    <h3 style="margin:0; color: #fff; display: inline-block;">{row['Champion']}</h3>
                    <p style="margin:0.5rem 0 0 0; font-size: 1.2rem;">
                        <span style="color: #94a3b8;">{int(row['Games'])} games</span> • 
                        <span class="winrate-high">{row['WR']}% WR</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Pas assez de données (min. 5 games)")

st.markdown("---")

# === SECTION 2: GRAPHIQUES ===
st.header("📈 Visualisations")

tab1, tab2, tab3 = st.tabs(["🎮 Picks", "🚫 Bans", "🏆 Winrates"])

with tab1:
    top_10_picks = df.nlargest(10, 'Games')
    fig_picks = px.bar(
        top_10_picks,
        x='Games',
        y='Champion',
        orientation='h',
        title="Top 10 Champions les Plus Joués",
        color='WR',
        color_continuous_scale=['#ef4444', '#fbbf24', '#22c55e'],
        labels={'Games': 'Nombre de Parties', 'WR': 'Winrate (%)'}
    )
    fig_picks.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_picks, use_container_width=True)

with tab2:
    top_10_bans = df.nlargest(10, 'Bans')
    fig_bans = px.bar(
        top_10_bans,
        x='Bans',
        y='Champion',
        orientation='h',
        title="Top 10 Champions les Plus Bannis",
        color='Bans',
        color_continuous_scale='Reds'
    )
    fig_bans.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_bans, use_container_width=True)

with tab3:
    if len(df_filtered) > 0:
        top_10_wr = df_filtered.nlargest(10, 'WR')
        fig_wr = px.bar(
            top_10_wr,
            x='WR',
            y='Champion',
            orientation='h',
            title="Top 10 Meilleurs Winrates (min. 5 games)",
            color='Games',
            color_continuous_scale='Viridis',
            labels={'WR': 'Winrate (%)', 'Games': 'Parties'}
        )
        fig_wr.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_wr, use_container_width=True)
    else:
        st.info("Pas assez de données (min. 5 games)")

st.markdown("---")

# === SECTION 3: TABLEAU COMPLET ===
st.header("📋 Tableau complet — Champions (détails)")

# Options de filtrage
col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    min_games = st.slider("Nombre minimum de parties", 0, int(df['Games'].max()), 0)
with col_filter2:
    search_champion = st.text_input("🔍 Rechercher un champion", "")

# Appliquer les filtres
df_filtered_display = df[df['Games'] >= min_games]
if search_champion:
    df_filtered_display = df_filtered_display[
        df_filtered_display['Champion'].str.contains(search_champion, case=False, na=False)
    ]

# Construire le tableau HTML
table_html = '''
<table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; margin-top: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden;">
    <thead>
        <tr style="background: #0b1220; color: #9fb0c6;">
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Champion</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Games</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">WR</th>
            <th style="padding: 16px 14px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase;">Bans</th>
        </tr>
    </thead>
    <tbody>
'''

for idx, (_, champ) in enumerate(df_filtered_display.iterrows(), 1):
    # Get WR color
    wr = champ.get('WR', 0)
    if wr >= 60:
        wr_color = "#22c55e"
    elif wr >= 50:
        wr_color = "#a3e635"
    elif wr >= 40:
        wr_color = "#facc15"
    else:
        wr_color = "#ef4444"
    
    # Background color
    bg_color = "#0f1113" if idx % 2 == 0 else "#0b0d10"
    
    # Champion icon
    icon_url = get_champion_icon(champ['Champion'])
    
    table_html += f'''
        <tr style="background: {bg_color}; border-top: 1px solid rgba(255,255,255,0.05); transition: background 0.2s;" onmouseover="this.style.background='#1a1d24'" onmouseout="this.style.background='{bg_color}'">
            <td style="padding: 16px 14px; color: #e6eef6;">
                <img src="{icon_url}" style="width: 32px; height: 32px; border-radius: 4px; margin-right: 8px; vertical-align: middle; border: 1px solid rgba(255,255,255,0.1);" onerror="this.style.display='none'">
                <strong>{champ['Champion']}</strong>
            </td>
            <td style="padding: 16px 14px; color: #e6eef6;">{int(champ['Games'])}</td>
            <td style="padding: 16px 14px; color: {wr_color}; font-weight: 700;">{champ['WR']:.1f}%</td>
            <td style="padding: 16px 14px; color: #e6eef6;">{int(champ['Bans'])}</td>
        </tr>
    '''

table_html += '''
    </tbody>
</table>
'''

# Use st.components for proper HTML rendering
import streamlit.components.v1 as components
components.html(table_html, height=600, scrolling=True)

# Stats globales
st.markdown("---")
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("Champions uniques", len(df))
with col_stat2:
    st.metric("Total parties", int(df['Games'].sum()))
with col_stat3:
    st.metric("Winrate moyen", f"{df['WR'].mean():.1f}%")
