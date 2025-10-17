import streamlit as st
import pandas as pd
from utils.formatters import format_champion_name, get_champion_icon_url

def display_match_history(df: pd.DataFrame):
    """Display match history table."""
    st.subheader("Historique des parties")
    
    # Format date
    df['date'] = pd.to_datetime(df['date'], format='%d%m%Y')
    df = df.sort_values(['date', 'numero_game'], ascending=[False, False])
    df['date'] = df['date'].dt.strftime('%d/%m/%Y')
    
    # Calculate CS/min
    df['CS/min'] = df.apply(lambda row: 
        float(row['Missions_CreepScore']) / (float(row['gameDuration']) / 60000) 
        if row['Missions_CreepScore'] and row['gameDuration'] 
        else 0.0, 
        axis=1
    )
    
    # Add champion icons
    df['Champion'] = df['SKIN'].apply(
        lambda x: f'<img src="{get_champion_icon_url(x)}" width="30" height="30" style="vertical-align:middle"> {format_champion_name(x)}'
    )
    
    # Format display data
    display_df = pd.DataFrame()
    display_df['DATE'] = df['date']
    display_df['CHAMPION'] = df['Champion']
    display_df['W/L'] = df['Win'].apply(lambda x: "✅ Win" if x == "Win" else "❌ Lose")
    display_df['TYPE'] = df['type_partie'].map({'Scrim': '⚔️ Scrim', 'Tournoi': '🛡️ Tournoi'})
    display_df['VS'] = df['equipe_adverse']
    display_df['GAME'] = df.apply(
        lambda row: row['game_tournoi'].replace('GameTournoi', '') 
        if row['type_partie'] == 'Tournoi' and pd.notnull(row.get('game_tournoi'))
        else row['numero_game'],
        axis=1
    )
    display_df['DURÉE'] = pd.to_numeric(df['gameDuration']).apply(
        lambda x: f"{int(x/60000):02d}:{int((x%60000)/1000):02d}"
    )
    display_df['KDA'] = df['KDA']
    display_df['KILLS'] = df['KDA'].str.split('/').str[0]
    display_df['DEATHS'] = df['KDA'].str.split('/').str[1]
    display_df['ASSISTS'] = df['KDA'].str.split('/').str[2]
    display_df['CS/MIN'] = df['CS/min'].round(1)
    display_df['VISION SCORE'] = df['VISION_SCORE']
    display_df['KP'] = df['KP'].apply(lambda x: f"{float(x):.1f}%")

    # Add table style
    st.markdown("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: rgb(17, 23, 31);
            border-radius: 4px;
        }
        .dataframe th {
            background: rgb(17, 23, 31) !important;
            padding: 12px !important;
            color: rgb(136, 144, 160) !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .dataframe td {
            padding: 12px !important;
            font-size: 13px !important;
            color: rgb(255, 255, 255) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .dataframe img {
            vertical-align: middle;
            margin-right: 10px;
            border-radius: 50%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.write(
        display_df.to_html(
            escape=False,
            index=False,
            classes='dataframe'
        ),
        unsafe_allow_html=True
    )
