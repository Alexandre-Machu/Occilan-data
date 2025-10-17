"""
OcciLan Stats - Application Streamlit principale
Multi-édition hub pour les statistiques des tournois OcciLan
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.data_manager import MultiEditionManager, EditionDataManager
from dotenv import load_dotenv

load_dotenv()


def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="OcciLan Stats",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            color: #FF4B4B;
            margin-bottom: 2rem;
        }
        .subtitle {
            font-size: 1.2rem;
            text-align: center;
            color: #888;
            margin-bottom: 3rem;
        }
        .metric-card {
            background-color: #262730;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #FF4B4B;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar - Edition selector
    with st.sidebar:
        st.markdown("### 📂 Sélection d'édition")
        
        multi_manager = MultiEditionManager()
        editions = multi_manager.list_editions()
        
        if not editions:
            st.warning("⚠️ Aucune édition disponible")
            st.info("💡 Créez une édition dans la page Admin")
            selected_edition = None
        else:
            selected_edition = st.selectbox(
                "Édition",
                editions,
                format_func=lambda x: f"Edition {x}",
                label_visibility="collapsed"
            )
            
            if selected_edition:
                edition_manager = EditionDataManager(selected_edition)
                config = edition_manager.load_config()
                
                if config:
                    st.markdown(f"**{config.get('name', 'N/A')}**")
                    st.caption(f"📆 {config.get('start_date', 'N/A')} → {config.get('end_date', 'N/A')}")
        
        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        st.page_link("app.py", label="🏠 Accueil")
        st.page_link("pages/5_🔧_Admin.py", label="🔧 Admin")
        st.markdown("---")
        st.caption("🎮 OcciLan Stats v2.0")
    
    # Main content
    st.markdown('<h1 class="main-header">🎮 OcciLan Stats</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Statistiques et analyses des tournois League of Legends</p>', unsafe_allow_html=True)
    
    if not editions or not selected_edition:
        st.info("👈 Créez ou sélectionnez une édition dans la page Admin")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📊 Analyses détaillées
            - Statistiques par joueur
            - Performances par équipe
            - Records et classements
            """)
        
        with col2:
            st.markdown("""
            ### 🎮 Données en temps réel
            - Intégration Riot Games API
            - Historique des matchs
            - Rangs actuels
            """)
        
        with col3:
            st.markdown("""
            ### 🔧 Gestion facilitée
            - Interface admin
            - Import CSV ou formulaire
            - Multi-éditions
            """)
    else:
        # Edition selected - show summary
        edition_manager = EditionDataManager(selected_edition)
        config = edition_manager.load_config()
        summary = edition_manager.get_summary()
        
        st.subheader(f"📊 Résumé - Edition {selected_edition}")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏆 Équipes", summary.get('total_teams', 0))
        
        with col2:
            st.metric("👤 Joueurs", summary.get('total_players', 0))
        
        with col3:
            st.metric("🎮 Matchs", summary.get('total_matches', 0))
        
        with col4:
            st.metric("📊 Statut", summary.get('status', 'N/A'))
        
        st.markdown("---")
        
        # Teams list
        teams = edition_manager.load_teams()
        
        # Convert dict to list if needed (teams.json format is dict)
        if isinstance(teams, dict):
            teams_list = [{"name": name, **data} for name, data in teams.items()]
        elif isinstance(teams, list):
            teams_list = teams
        else:
            teams_list = []
        
        if teams_list:
            st.subheader("🏆 Équipes inscrites")
            
            teams_to_show = teams_list[:5] if len(teams_list) > 5 else teams_list
            
            for team in teams_to_show:
                with st.expander(f"{team.get('name', 'Unknown')}"):
                    # Sort players by role order
                    role_order = {"TOP": 0, "JGL": 1, "MID": 2, "ADC": 3, "SUP": 4}
                    players = team.get('players', [])
                    sorted_players = sorted(players, key=lambda p: role_order.get(p.get("role", "SUP"), 5))
                    
                    cols = st.columns(5)
                    for idx, player in enumerate(sorted_players):
                        with cols[idx]:
                            st.markdown(f"**{player.get('role', 'N/A')}**")
                            st.caption(f"{player.get('gameName', 'Unknown')}#{player.get('tagLine', '0000')}")
            
            if len(teams_list) > 5:
                st.info(f"➕ {len(teams_list) - 5} équipes supplémentaires")
        else:
            st.info("ℹ️ Aucune équipe inscrite. Ajoutez des équipes dans la page Admin.")
    
    st.markdown("---")
    st.caption("Made with ❤️ for OcciLan | Data by Riot Games API")


if __name__ == "__main__":
    main()
