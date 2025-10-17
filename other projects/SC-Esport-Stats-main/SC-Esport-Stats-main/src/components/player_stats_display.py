import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import format_champion_name, get_champion_icon_url

def load_css():
    css_path = Path(__file__).parent.parent.parent / 'static/css/player_stats.css'
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_champion_graph(df: pd.DataFrame):
    """Display the champion statistics graph."""
    champion_stats = {}
    for _, row in df.iterrows():
        champ = row['SKIN']
        result = row['Win']
        if champ not in champion_stats:
            champion_stats[champ] = {'total': 0, 'wins': 0}
        champion_stats[champ]['total'] += 1
        if result == 'Win':
            champion_stats[champ]['wins'] += 1

    # Sort champions by total games
    sorted_champions = sorted(champion_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    champions = [format_champion_name(champ) for champ, _ in sorted_champions]
    wins = [stats['wins'] for _, stats in sorted_champions]
    losses = [stats['total'] - stats['wins'] for _, stats in sorted_champions]

    # Create figure
    fig = go.Figure(data=[
        go.Bar(name='Victoires', x=champions, y=wins, marker_color='#2ECC71', width=0.5),
        go.Bar(name='Défaites', x=champions, y=losses, marker_color='#E74C3C', width=0.5)
    ])

    # Update layout
    fig.update_layout(
        barmode='stack',
        title={
            'text': "Nombre de games par champion",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        )
    )

    # Update axes
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor='rgba(255,255,255,0.2)',
        tickangle=45
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255,255,255,0.1)',
        showline=True,
        linewidth=2,
        linecolor='rgba(255,255,255,0.2)'
    )

    st.plotly_chart(fig, use_container_width=True)

def display_player_grid(stats: dict):
    """Display the main player statistics grid."""
    grid_html = f"""
    <div class="player-stats-grid">
        <div class="player-stat-card">
            <div class="stat-label">KDA</div>
            <div class="stat-value">{stats.get('kda', 0):.2f}</div>
            <div class="stat-subtext">{stats.get('avg_kills', 0):.1f}/{stats.get('avg_deaths', 0):.1f}/{stats.get('avg_assists', 0):.1f}</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">KILLS MOYEN</div>
            <div class="stat-value">{stats.get('avg_kills', 0):.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">CS/MIN</div>
            <div class="stat-value">{stats.get('cs_per_min', 0):.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">VISION SCORE</div>
            <div class="stat-value">{stats.get('avg_vision', 0):.1f}</div>
            <div class="stat-subtext">par partie</div>
        </div>
        <div class="player-stat-card">
            <div class="stat-label">KP</div>
            <div class="stat-value">{stats.get('kp', 0):.1f}%</div>
            <div class="stat-subtext">participation aux kills</div>
        </div>
    </div>
    """
    st.markdown(grid_html, unsafe_allow_html=True)

def display_player_stats(analyzer, player_name: str, game_type: str = "Global"):
    load_css()

    # Récupération des stats
    stats = analyzer.get_player_stats(player_name, game_type)
    
    if not stats['match_history']:
        st.error("Aucune donnée disponible")
        return
        
    df = pd.DataFrame(stats['match_history'])
    
    # Calculate CS/min for the entire dataset
    df['cs_per_min'] = df.apply(
        lambda row: float(row['Missions_CreepScore']) / (float(row['gameDuration']) / 60000),
        axis=1
    )

    # Calculate stats before displaying
    stats['cs_per_min'] = df['cs_per_min'].mean()
    stats['kp'] = df['KP'].astype(float).mean()

    # Display sections in order
    sections = [
        ("Statistiques du joueur", lambda: display_player_grid(stats)),
        ("Champions les plus joués", lambda: display_champion_graph(df)),
        ("Champions Stats", lambda: display_champion_stats(df)),
        ("Historique des parties", lambda: display_match_history(df))
    ]
    
    for title, display_func in sections:
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
        display_func()

def display_match_history(df: pd.DataFrame):
    # Sort by date
    df['DATE'] = pd.to_datetime(df['date'], format='%d%m%Y')
    df = df.sort_values('DATE', ascending=False)
    
    # Ensure vision columns exist and convert to numeric
    vision_columns = ['VISION_SCORE', 'VISION_WARDS_BOUGHT_IN_GAME', 'Missions_PlaceUsefulControlWards']
    for col in vision_columns:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Convert other numeric columns
    for col in ['GOLD_EARNED', 'TOTAL_DAMAGE_DEALT_TO_CHAMPIONS']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Create derived columns for vision
    df['vision_score_value'] = df['VISION_SCORE']
    df['vision_useful_wards'] = df['Missions_PlaceUsefulControlWards']
    df['vision_bought_wards'] = df['VISION_WARDS_BOUGHT_IN_GAME']
    
    # Calculate vision efficiency percentage
    df['vision_efficiency_pct'] = df.apply(
        lambda row: 100 * row['vision_useful_wards'] / row['vision_bought_wards']
                    if row['vision_bought_wards'] > 0 else 0,
        axis=1
    )
    
    # Format vision data for display
    df['VISION_FORMATTED'] = df.apply(
        lambda row: format_vision_data(
            row['vision_score_value'],
            row['vision_useful_wards'],
            row['vision_bought_wards'],
            row['vision_efficiency_pct']
        ),
        axis=1
    )
    
    # Calculate gold efficiency - fixing the error by ensuring values exist
    try:
        if all(col in df.columns for col in ['TOTAL_DAMAGE_DEALT_TO_CHAMPIONS', 'GOLD_EARNED']):
            # Store raw values for tooltip and ensure they're numeric
            df['dmg_dealt'] = pd.to_numeric(df['TOTAL_DAMAGE_DEALT_TO_CHAMPIONS'], errors='coerce').fillna(0)
            df['gold'] = pd.to_numeric(df['GOLD_EARNED'], errors='coerce').fillna(0)
            
            # Calculate gold efficiency safely
            df['gold_efficiency'] = df.apply(
                lambda row: (
                    row['dmg_dealt'] / row['gold'] * 1000
                    if row['gold'] > 0 else 0
                ),
                axis=1
            )
        else:
            # Ensure safe fallback if columns are missing
            df['cs_per_min'] = df['cs_per_min'] if 'cs_per_min' in df.columns else 0
            df['gold_efficiency'] = df['cs_per_min'] * 50
            df['dmg_dealt'] = 0
            df['gold'] = 0
    except Exception as e:
        # If anything goes wrong, provide placeholder values
        df['gold_efficiency'] = 0
        df['dmg_dealt'] = 0
        df['gold'] = 0
    
    # Prepare display DataFrame
    display_df = pd.DataFrame()
    display_df['DATE'] = df['DATE'].dt.strftime('%d/%m/%Y')
    display_df['CHAMPION'] = df['SKIN'].apply(
        lambda x: f'<img src="{get_champion_icon_url(x)}" width="30" height="30"> {format_champion_name(x)}'
    )
    display_df['W/L'] = df['Win'].apply(lambda x: "✅ Win" if x == "Win" else "❌ Lose")
    
    # Correction du type de partie
    if 'type_partie' in df.columns:
        display_df['TYPE'] = df['type_partie'].map({'Scrim': '⚔️ Scrim', 'Tournoi': '🛡️ Tournoi'})
    else:
        display_df['TYPE'] = "-"
    
    # Ajouter les colonnes de base
    display_df['VS'] = df['equipe_adverse'] 
    display_df['GAME'] = df['numero_game']
    display_df['DURÉE'] = pd.to_numeric(df['gameDuration']).apply(
        lambda x: f"{int(x/60000):02d}:{int((x%60000)/1000):02d}"
    )
    
    # KDA avec score numérique
    df['kda_numeric'] = df['KDA'].apply(lambda kda_str: calculate_kda_from_string(kda_str))
    display_df['KDA'] = df.apply(
        lambda row: f"{row['KDA']} <span class='{get_kda_class(row['kda_numeric'])}'>[{row['kda_numeric']:.2f}]</span>",
        axis=1
    )
    
    # Kill Participation avec tooltip expliquant le calcul
    if 'KP' in df.columns:
        # Stocker les valeurs brutes pour le calcul
        df['player_contribution'] = df.apply(
            lambda row: int(row['CHAMPIONS_KILLED']) + int(row['ASSISTS']),
            axis=1
        )
        
        # Créer le tooltip avec explication du calcul
        display_df['KP'] = df.apply(
            lambda row: f"<span title='Calcul: {int(row['player_contribution'])} (kills+assists) ÷ {int(row['player_contribution']/row['KP']*100 if row['KP'] > 0 else 0)} kills équipe = {float(row['KP']):.1f}%'>{float(row['KP']):.1f}%</span>",
            axis=1
        )
    
    # CS/MIN with tooltip, updated color classes and star for excellent values
    display_df['CS/MIN'] = df.apply(
        lambda row: f"<span class='{get_cs_class(row['cs_per_min'])}' title='Calcul: {int(row['Missions_CreepScore'])} cs ÷ {(float(row['gameDuration'])/60000):.1f} minutes = {row['cs_per_min']:.1f}'>{row['cs_per_min']:.1f}{' ⭐' if float(row['cs_per_min']) >= 9 else ''}</span>",
        axis=1
    )
    
    # VISION: utiliser la colonne formatée sans ajouter CONTROL WARDS
    display_df['VISION'] = df['VISION_FORMATTED']
    
    # Gold efficiency with tooltip showing calculation details
    display_df['GOLD EFF'] = df.apply(
        lambda row: f"<span class='{get_gold_efficiency_class(float(row['gold_efficiency']))}' title='Calcul: {int(max(0, row['dmg_dealt'])):,} dégâts ÷ {int(max(1, row['gold'])):,} or = {float(row['gold_efficiency']):.2f} dégâts par 1000 or'>{float(row['gold_efficiency']):.1f}</span>",
        axis=1
    )
    
    # Prepare HTML table with tooltips
    html_table = display_df.to_html(escape=False, index=False)
    
    # Add tooltips to headers - removing CONTROL WARDS tooltip
    tooltips = {
        "<th>KDA</th>": "<th title='Kills+Assists / Deaths - Score d&#39;efficacité combative'>KDA</th>",
        "<th>CS/MIN</th>": "<th title='Creep Score par minute - Mesure l&#39;efficacité du farming'>CS/MIN</th>",
        "<th>KP</th>": "<th title='Kill Participation - % de participation aux éliminations de l&#39;équipe'>KP</th>",
        "<th>VISION</th>": "<th title='Score de vision (Efficacité en % = wards utiles/wards achetées)'>VISION</th>",
        "<th>GOLD EFF</th>": "<th title='Dégâts infligés par 1000 or - Mesure l&#39;efficacité de l&#39;or dépensé'>GOLD EFF</th>",
    }
    
    for original, tooltipped in tooltips.items():
        html_table = html_table.replace(original, tooltipped)
    
    st.markdown(html_table, unsafe_allow_html=True)

# Fonction pour calculer le KDA numérique à partir de la chaîne KDA
def calculate_kda_from_string(kda_str):
    """Calculate KDA score from a string in the format 'kills/deaths/assists'"""
    try:
        parts = kda_str.split('/')
        kills = float(parts[0])
        deaths = float(parts[1])
        assists = float(parts[2])
        return (kills + assists) / max(1, deaths)  # Avoid division by zero
    except (IndexError, ValueError):
        return 0

# Function to determine CSS class based on KDA - updated with pastel colors and new thresholds
def get_kda_class(value):
    """Return color class based on KDA value."""
    if value >= 5: return 'kda-gold'       # Gold for exceptional KDA (5+)
    if value >= 2.5: return 'kda-high'     # Pastel violet for excellent KDA (2.5-4.99)
    if value >= 1.5: return 'kda-medium'   # Cyan blue for good KDA (1.5-2.49)
    return 'kda-low'                       # Gray for low KDA (<1.5)

# Function to determine CSS class based on vision efficiency
def get_vision_class(value):
    """Return color class based on vision efficiency percentage."""
    if value >= 75: return 'color-high'     # Gold for excellent vision (75%+)
    if value >= 50: return 'color-good'     # Green for good vision (50-75%)
    if value >= 30: return 'color-medium'   # Orange for medium vision (30-50%)
    return 'color-low'                      # Red for poor vision (<30%)

# Function to determine CSS class based on CS/min with added star for excellent values
def get_cs_class(value):
    """Return color class based on CS per minute."""
    try:
        value = float(value)
        if value >= 9: return 'color-high'      # Gold + star for excellent CS (9+)
        if value >= 8: return 'color-good'      # Green for good CS (8-9)
        if value >= 6: return 'color-medium'    # Orange for okay CS (6-8)
        return 'color-low'                      # Red for poor CS (<6)
    except (ValueError, TypeError):
        return 'color-low'

# Get CSS class for winrate
def get_wr_class(value):
    """Return color class based on winrate percentage."""
    try:
        value = float(value)
        if value >= 60: return 'wr-high'      # Gold for high winrate (60%+)
        if value >= 50: return 'wr-medium'    # Green for decent winrate (50-60%)
        return 'wr-low'                       # Gray for low winrate (<50%)
    except (ValueError, TypeError):
        return 'wr-low'

def get_color_class(value: float, thresholds: dict) -> str:
    """Return color class based on value and thresholds."""
    if value >= thresholds['high']:
        return 'color-high'    # Gold for high values
    elif 'good' in thresholds and value >= thresholds['good']:
        return 'color-good'    # Green for good values
    elif value >= thresholds['medium']:
        return 'color-medium'  # Orange for medium values
    return 'color-low'         # Red for low values

def display_champion_stats(df: pd.DataFrame):
    """Display the champion statistics table."""
    champion_stats = {}
    
    for champ in df['SKIN'].unique():
        champ_data = df[df['SKIN'] == champ]
        games = len(champ_data)
        wins = len(champ_data[champ_data['Win'] == 'Win'])
        
        # Calculate KDA
        kda_parts = champ_data['KDA'].str.split('/', expand=True)
        kills = kda_parts[0].astype(float).mean()
        deaths = kda_parts[1].astype(float).mean()
        assists = kda_parts[2].astype(float).mean()
        kda = (kills + assists) / max(1, deaths)
        
        # Calculate KP
        kp = champ_data['KP'].astype(float).mean()
        
        champion_stats[champ] = {
            'name': format_champion_name(champ),
            'icon_url': get_champion_icon_url(champ),
            'games': games,
            'winrate': (wins / games) * 100,
            'kda': kda,
            'kp': kp
        }
    
    # Define thresholds for colors with new tiers
    thresholds = {
        'winrate': {'high': 60, 'good': 50, 'medium': 0},  # Updated thresholds for winrate
        'kda': {'high': 4, 'good': 3, 'medium': 0},
        'kp': {'high': 70, 'good': 60, 'medium': 50}
    }
    
    # Convert to DataFrame for display
    display_df = pd.DataFrame()
    display_df['CHAMPION'] = [
        f'<img src="{stats["icon_url"]}" width="30" height="30"> {stats["name"]}' 
        for stats in champion_stats.values()
    ]
    display_df['GAMES'] = [stats['games'] for stats in champion_stats.values()]
    display_df['WR'] = [
        f'<span class="{get_wr_class(stats["winrate"])}">{stats["winrate"]:.1f}%</span>'
        for stats in champion_stats.values()
    ]
    display_df['KDA'] = [
        f'<span class="{get_kda_class(stats["kda"])}">{stats["kda"]:.2f}</span>'
        for stats in champion_stats.values()
    ]
    display_df['KP'] = [
        f'<span class="{get_color_class(stats["kp"], thresholds["kp"])}">{stats["kp"]:.1f}%</span>'
        for stats in champion_stats.values()
    ]
    
    # Sort by number of games
    display_df = display_df.sort_values('GAMES', ascending=False)
    
    # Display table
    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

# Nouvelle fonction simplifiée pour formater les données de vision
def format_vision_data(vision_score, useful_wards, bought_wards, efficiency_pct):
    """Format vision data into a string with efficiency percentage"""
    if bought_wards > 0:
        tooltip = f"Wards utiles: {useful_wards}, Wards achetées: {bought_wards}, Ratio: {useful_wards}/{bought_wards} = {efficiency_pct:.0f}%"
        return f"{vision_score} ({useful_wards}/{bought_wards}) <span title='{tooltip}' class='{get_vision_class(efficiency_pct)}'>{efficiency_pct:.0f}%</span>"
    else:
        return f"{vision_score} (0/0) <span class='color-low'>0%</span>"

# Function to determine CSS class based on gold efficiency
def get_gold_efficiency_class(value):
    """Return color class based on damage per 1000 gold."""
    try:
        value = float(value)  
        if value >= 1600: return 'color-high'     # Gold for excellent ratio (>1600)
        if value >= 1300: return 'color-good'     # Green for good ratio (1300-1600)
        if value >= 1000: return 'color-medium'   # Orange for okay ratio (1000-1300)
        return 'color-low'                        # Red for poor ratio (<1000)
    except (ValueError, TypeError):
        return 'color-low'                        # Default if conversion fails