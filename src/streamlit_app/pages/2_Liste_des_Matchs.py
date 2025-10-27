"""
Page des matchs du tournoi
Affiche la liste des matchs avec leurs détails
"""

import streamlit as st
from components.match_card import (
    display_match_card,
    get_display_name_and_aliases,
    get_champion_icon_url,
    get_role_icon_url,
    format_duration,
    sort_players_by_role
)
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.data_manager import EditionDataManager, MultiEditionManager

# Configuration de la page
st.set_page_config(
    page_title="Matchs - OcciLan Stats",
    page_icon="🎮",
    layout="wide"
)

                    # Bouton à droite de la carte
                    if st.button(f"👤 Profil", key=f"profile_{match_id}_100_{display_name}", help=f"Voir les stats de {display_name}"):
                        st.session_state["search_player"] = display_name
                        st.switch_page("pages/6_🔍_Recherche.py")
        
        with col_vs:
            st.markdown("### VS")
            st.markdown(f"**{duration_str}**")
        
        with col2:
            # Équipe 200 (Rouge)
            if team_200_win:
                st.markdown(f"### 🔴 **{team_200_name}** ✅ VICTOIRE")
            else:
                st.markdown(f"### 🔴 **{team_200_name}** ❌ DÉFAITE")
            
            # Statistiques de l'équipe
            total_kills_200 = sum(p.get("kills", 0) for p in team_200)
            total_gold_200 = sum(p.get("goldEarned", 0) for p in team_200)
            
            st.metric("Kills", total_kills_200)
            st.metric("Gold total", f"{total_gold_200:,}")
            
            # Joueurs
            st.markdown("#### Joueurs")
            for p in team_200:  # Déjà triés par rôle
                display_name, aliases = get_display_name_and_aliases(team_200_name, p, teams_with_puuid)
                champion = p.get("championName", "Unknown")
                kills = p.get("kills", 0)
                deaths = p.get("deaths", 0)
                assists = p.get("assists", 0)
                cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
                role = p.get("teamPosition", "UNKNOWN")
                kda = f"{kills}/{deaths}/{assists}"
                icon_url = get_champion_icon_url(champion)
                role_icon_url = get_role_icon_url(role)
                col_card, col_button = st.columns([5, 1])
                with col_card:
                    player_html = f'''
                    <div style="display: flex; align-items: center; gap: 12px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px; margin-bottom: 6px;">
                        <img src="{icon_url}" style="width: 40px; height: 40px; border-radius: 6px; border: 2px solid rgba(255,100,100,0.3);" title="{champion}">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: #e6eef6; font-size: 14px;">
                                <img src="{role_icon_url}" style="width:18px;vertical-align:middle;margin-right:4px;" title="{role}">{display_name}
                            </div>
                            <div style="color: #9fb0c6; font-size: 12px;">{champion}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #e6eef6; font-weight: 600;">{kda}</div>
                            <div style="color: #9fb0c6; font-size: 11px;">{cs} CS</div>
                        </div>
                    </div>
                    '''
                    st.markdown(player_html, unsafe_allow_html=True)
                
                with col_button:
                    # Bouton à droite de la carte
                    if st.button(f"👤 Profil", key=f"profile_{match_id}_200_{display_name}", help=f"Voir les stats de {display_name}"):
                        st.session_state["search_player"] = display_name
                        st.switch_page("pages/6_🔍_Recherche.py")


# Titre de la page
st.title("🎮 Matchs du Tournoi")

# Vérifier qu'une édition est sélectionnée
if not available_editions or not selected_edition:
    st.warning("⚠️ Veuillez d'abord sélectionner une édition")
    st.stop()

# Utiliser l'édition manager
edition_manager = EditionDataManager(selected_edition)
data_dir = Path(__file__).parent.parent.parent.parent / "data" / "editions" / f"edition_{selected_edition}"


# Charger les team_stats pour le mapping joueur->équipe
team_stats_path = data_dir / "team_stats.json"
player_to_team = {}

if team_stats_path.exists():
    with open(team_stats_path, "r", encoding="utf-8") as f:
        team_stats_data = json.load(f)
        # Créer le mapping joueur -> équipe
        for team_name, team_data in team_stats_data.items():
            players = team_data.get("players", {})
            for player_key, player_data in players.items():
                # Utiliser gameName et tagLine pour le mapping
                game_name = player_data.get("gameName") or player_data.get("player_name")
                tag_line = player_data.get("tagLine") or ""
                if game_name and tag_line:
                    player_to_team[f"{game_name}#{tag_line}"] = team_name
                    player_to_team[f"{game_name.replace(' ', '').lower()}#{tag_line.lower()}"] = team_name
                if game_name:
                    player_to_team[game_name] = team_name
                    player_to_team[game_name.replace(' ', '').lower()] = team_name

# Charger tournament_matches pour fallback équipe
tournament_matches_path = data_dir / "tournament_matches.json"
tournament_matches = None
if tournament_matches_path.exists():
    with open(tournament_matches_path, "r", encoding="utf-8") as f:
        tournament_matches = json.load(f)

# Charger teams_with_puuid pour l'accès aux oldAccounts
teams_with_puuid = edition_manager.load_teams_with_puuid() if 'edition_manager' in locals() else {}

# Charger les match_details
match_details_path = data_dir / "match_details.json"

if not match_details_path.exists():
    st.error("❌ Aucun match trouvé pour cette édition")
    st.info("💡 Allez dans l'onglet Admin pour lancer le traitement des données")
    st.stop()

with open(match_details_path, "r", encoding="utf-8") as f:
    match_details = json.load(f)

if not match_details:
    st.warning("⚠️ Aucun match disponible")
    st.stop()

    )
elif sort_by == "Durée (courte)":
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: x[1].get("info", {}).get("gameDuration", 0)
    )
elif sort_by == "Kills (plus)":
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: sum(p.get("kills", 0) for p in x[1].get("info", {}).get("participants", [])),
        reverse=True
    )
else:  # Kills (moins)
    sorted_matches = sorted(
        filtered_matches.items(),
        key=lambda x: sum(p.get("kills", 0) for p in x[1].get("info", {}).get("participants", []))
    )

# Afficher les matchs
st.markdown("---")
st.subheader(f"📋 Liste des matchs ({len(sorted_matches)} matchs)")

if sorted_matches:
    for match_id, match_data in sorted_matches:
          display_match_card(match_id, match_data, player_to_team, tournament_matches=tournament_matches)
else:
    st.info("Aucun match ne correspond aux filtres sélectionnés")
