import os
import streamlit as st
from components.player_stats_display import display_player_stats
from components.stats_display import display_global_stats
from data_processing.stats_analyzer import StatsAnalyzer
from utils.image_utils import get_image_as_base64

st.set_page_config(page_title="SC-Esport-Stats", layout="wide")

# Initialize the analyzer
analyzer = StatsAnalyzer("data/")

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'global'
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = 'TOP'  # Default selection

# CSS to customize the navbar
st.markdown("""
    <style>
    .navbar {
        padding: 1rem;
        background-color: #1E1E1E;
        border-radius: 10px;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
    }
    .logo-title {
        display: flex;
        align-items: center;
        margin-right: 2rem;
    }
    .logo {
        width: 50px;
        height: 50px;
        margin-right: 1rem;
    }
    .title {
        color: #FFFFFF;
        font-size: 24px;
        font-weight: bold;
    }
    th.level0.row_heading {
        display: none;
    }
    th.blank.level0 {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Navbar with logo and title
logo_path = os.path.join(os.path.dirname(__file__), "..", "img", "logoequipe.jpg")
st.markdown(f"""
    <div class="navbar">
        <div class="logo-title">
            <img src="data:image/png;base64,{get_image_as_base64(logo_path)}" class="logo">
            <span class="title">SC Esport Stats</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, space = st.columns([2, 2, 8])

with col1:
    if st.button(
        "📊 Statistiques Globales", 
        key="btn_global",
        use_container_width=True,
        type="primary" if st.session_state.current_page == 'global' else "secondary"
    ):
        st.session_state.current_page = 'global'
        st.rerun()  # Force the page to reload

with col2:
    if st.button(
        "👤 Statistiques par Joueur", 
        key="btn_player",
        use_container_width=True,
        type="primary" if st.session_state.current_page == 'player' else "secondary"
    ):
        st.session_state.current_page = 'player'
        st.rerun()  # Force the page to reload

st.divider()

# Game type selector
game_types = ["Global", "Scrim", "Tournoi"]
selected_game_type = st.selectbox(
    "Type de parties",
    game_types,
    key="game_type_selector"
)

# Navigation handling
if st.session_state.current_page == 'player':
    st.header("Statistiques par joueur")
    
    # Custom CSS for more compact buttons
    st.markdown(""" 
        <style> 
        div.stButton > button { 
            padding: 0.2rem 1rem; 
            font-size: 0.8rem; 
            height: auto; 
        } 
        </style> 
    """, unsafe_allow_html=True)
    
    # Role buttons
    roles = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
    cols = st.columns(len(roles))
    
    for i, role in enumerate(roles):
        with cols[i]:
            if st.button(
                role,
                key=f"btn_{role}",
                type="primary" if st.session_state.selected_role == role else "secondary",
                use_container_width=True
            ):
                st.session_state.selected_role = role
                st.rerun()  # Force the page to reload
    
    # Update player stats display with selected game type
    role_to_player = {
        "TOP": "Claquette",
        "JUNGLE": "Spectros",
        "MID": "Futeyy",
        "ADC": "Tixty",
        "SUPPORT": "Dert"
    }
    display_player_stats(analyzer, role_to_player[st.session_state.selected_role], selected_game_type)
else:
    st.title("Statistiques Globales")
    display_global_stats(analyzer, selected_game_type)  # Added game type