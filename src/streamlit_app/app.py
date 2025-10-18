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
        /* Masquer la section "app" par défaut de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none;
        }
        
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
        
        # Vérifier si l'utilisateur est admin
        is_admin = st.session_state.get("authenticated", False)
        
        # Lister les éditions (privées uniquement si admin)
        editions = multi_manager.list_editions(include_private=is_admin)
        
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
        st.page_link("pages/1_📊_Stats_Generales.py", label="📊 Stats Générales")
        st.page_link("pages/9_🔧_Admin.py", label="🔧 Admin")
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
            
            # Charger les données avec PUUID pour avoir les ranks
            teams_with_puuid = edition_manager.load_teams_with_puuid()
            
            # Afficher TOUTES les équipes
            for team in teams_list:
                team_name = team.get('name', 'Unknown')
                opgg_link = team.get('opgg_link', '')
                
                with st.expander(f"🏆 {team_name}"):
                    # Afficher le lien Multi OP.GG
                    if opgg_link:
                        st.markdown(
                            f'<a href="{opgg_link}" target="_blank" style="text-decoration: none;">'
                            f'<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                            f'color: white; padding: 10px 20px; border-radius: 8px; text-align: center; '
                            f'font-size: 0.95rem; font-weight: bold; margin-bottom: 15px; '
                            f'cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2); '
                            f'transition: transform 0.2s;">'
                            f'🔗 Multi OP.GG</div></a>',
                            unsafe_allow_html=True
                        )
                    
                    # Sort players by role order
                    role_order = {"TOP": 0, "JGL": 1, "MID": 2, "ADC": 3, "SUP": 4}
                    
                    # Essayer de récupérer les données avec rank depuis teams_with_puuid
                    if teams_with_puuid and team_name in teams_with_puuid:
                        players = teams_with_puuid[team_name].get('players', [])
                    else:
                        players = team.get('players', [])
                    
                    sorted_players = sorted(players, key=lambda p: role_order.get(p.get("role", "SUP"), 5))
                    
                    cols = st.columns(5)
                    for idx, player in enumerate(sorted_players):
                        with cols[idx]:
                            role = player.get('role', 'N/A')
                            game_name = player.get('gameName', 'Unknown')
                            tag_line = player.get('tagLine', '0000')
                            tier = player.get('tier', 'UNRANKED')
                            rank = player.get('rank', '')
                            lp = player.get('leaguePoints', 0)
                            
                            # Couleurs par tier
                            tier_colors = {
                                "CHALLENGER": "#FCA5A5",    # Rose pastel
                                "GRANDMASTER": "#FCA5A5",   # Rose pastel
                                "MASTER": "#C4B5FD",        # Violet pastel
                                "DIAMOND": "#93C5FD",       # Bleu pastel
                                "EMERALD": "#86EFAC",       # Vert pastel
                                "PLATINUM": "#67E8F9",      # Cyan pastel
                                "GOLD": "#FCD34D",          # Jaune pastel
                                "SILVER": "#D1D5DB",        # Gris pastel
                                "BRONZE": "#FDBA74",        # Orange pastel
                                "IRON": "#A8A29E",          # Gris foncé
                                "UNRANKED": "#4B5563"       # Gris très foncé
                            }
                            
                            color = tier_colors.get(tier, "#4B5563")
                            
                            # Créer le lien OP.GG du joueur
                            player_opgg = f"https://www.op.gg/summoners/euw/{game_name}-{tag_line}"
                            
                            st.markdown(f"**{role}**")
                            st.markdown(
                                f'<a href="{player_opgg}" target="_blank" style="color: #93C5FD; text-decoration: none;">'
                                f'{game_name}#{tag_line}</a>',
                                unsafe_allow_html=True
                            )
                            
                            # Afficher l'élo avec couleur
                            if tier != "UNRANKED":
                                if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
                                    elo_text = f"{tier} ({lp} LP)"
                                else:
                                    elo_text = f"{tier} {rank}"
                                
                                st.markdown(
                                    f'<div style="background-color: {color}; color: #1F2937; '
                                    f'padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; '
                                    f'font-weight: bold; text-align: center; margin-top: 4px;">'
                                    f'{elo_text}</div>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    f'<div style="background-color: {color}; color: white; '
                                    f'padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; '
                                    f'font-weight: bold; text-align: center; margin-top: 4px;">'
                                    f'❌ Unranked</div>',
                                    unsafe_allow_html=True
                                )
                    
                    # Ajouter un espace en bas de l'expander
                    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
            # Bouton pour replier/déplier toutes les équipes
            if len(teams_list) > 10:
                st.caption(f"📋 {len(teams_list)} équipes au total")
        else:
            st.info("ℹ️ Aucune équipe inscrite. Ajoutez des équipes dans la page Admin.")
        
        # Encart informations supplémentaires (placeholder pour plus tard)
        st.markdown("---")
        st.markdown("### 📢 Informations du tournoi")
        
        info_col1, info_col2 = st.columns([2, 1])
        
        with info_col1:
            st.info("""
            **🎯 Format du tournoi**
            - Phase de poules (BO1)
            - Playoffs (BO3)
            - Finale (BO5)
            
            _Plus d'informations à venir..._
            """)
        
        with info_col2:
            st.success("""
            **📊 Statistiques disponibles**
            - Classement des équipes
            - Stats par joueur
            - Historique des matchs
            
            _Consultez les pages dédiées_ →
            """)
    
    st.markdown("---")
    st.caption("Made with ❤️ for OcciLan | Data by Riot Games API")


if __name__ == "__main__":
    main()
