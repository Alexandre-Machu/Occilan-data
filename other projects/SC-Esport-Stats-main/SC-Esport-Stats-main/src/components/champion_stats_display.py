import streamlit as st
import pandas as pd
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from utils.formatters import format_champion_name, get_champion_icon_url

def get_template():
    template_dir = Path(__file__).parent.parent.parent / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    return env.get_template('champion_stats.html')

def display_champion_stats(df: pd.DataFrame):
    """Display champion statistics table."""
    # Calculate champion statistics
    champion_stats = {}
    for champ in df['SKIN'].unique():
        champ_data = df[df['SKIN'] == champ]
        games = len(champ_data)
        wins = len(champ_data[champ_data['Win'] == 'Win'])
        winrate = (wins / games) * 100 if games > 0 else 0
        
        # Calculate KDA
        kda_parts = champ_data['KDA'].str.split('/', expand=True)
        kills = kda_parts[0].astype(float).mean()
        deaths = kda_parts[1].astype(float).mean()
        assists = kda_parts[2].astype(float).mean()
        kda = (kills + assists) / max(1, deaths)
        
        # Convert KP to float before calculating mean
        kp = champ_data['KP'].astype(float).mean()
        
        champion_stats[champ] = {
            'name': format_champion_name(champ),
            'icon_url': get_champion_icon_url(champ),
            'games': games,
            'winrate': winrate,
            'kda': kda,
            'kp': kp,
            'wr_color': '#2ECC71' if winrate >= 50 else '#E74C3C'
        }

    # Sort and prepare champions data
    champions_data = sorted(champion_stats.values(), key=lambda x: x['games'], reverse=True)
    
    # Render template
    template = get_template()
    html = template.render(champions=champions_data)
    
    # Add CSS
    css_path = Path(__file__).parent.parent.parent / 'static/css/champion_stats.css'
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Display content
    st.markdown(html, unsafe_allow_html=True)
