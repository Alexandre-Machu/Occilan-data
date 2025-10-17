import streamlit as st
import plotly.graph_objects as go
from utils.formatters import format_champion_name

def display_champion_graph(df):
    """Display champion statistics graph."""
    st.subheader("Champions les plus joués")
    
    # Count games and wins per champion
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
    
    # Prepare data for plot
    champions = [format_champion_name(champ) for champ, _ in sorted_champions]
    wins = [stats['wins'] for _, stats in sorted_champions]
    losses = [stats['total'] - stats['wins'] for _, stats in sorted_champions]

    fig = go.Figure(data=[
        go.Bar(
            name='Victoires',
            x=champions,
            y=wins,
            marker_color='#2ECC71',
            width=0.5,
            hovertemplate="Victoires: %{y}<extra></extra>"
        ),
        go.Bar(
            name='Défaites',
            x=champions,
            y=losses,
            marker_color='#E74C3C',
            width=0.5,
            hovertemplate="Défaites: %{y}<extra></extra>"
        )
    ])

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
        xaxis_title="Champions",
        yaxis_title="Nombre de games",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
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
