import streamlit as st
from datetime import datetime

def get_role_icon_url(role: str, size: int = 24) -> str:
    role_norm = role.upper()
    if role_norm in ["TOP"]:
        key = "position-top.svg"
    elif role_norm in ["JGL", "JUNGLE"]:
        key = "position-jungle.svg"
    elif role_norm in ["MID", "MIDDLE"]:
        key = "position-middle.svg"
    elif role_norm in ["ADC", "BOTTOM"]:
        key = "position-bottom.svg"
    elif role_norm in ["SUP", "SUPP", "UTILITY"]:
        key = "position-utility.svg"
    else:
        key = "position-top.svg"
    return f"https://raw.communitydragon.org/pbe/plugins/rcp-fe-lol-static-assets/global/default/svg/{key}"

def get_champion_icon_url(champion_name: str) -> str:
    champion_mapping = {
        "MonkeyKing": "Wukong",
        "Belveth": "Belveth",
        "RenataGlasc": "Renata"
    }
    display_name = champion_mapping.get(champion_name, champion_name)
    return f"https://ddragon.leagueoflegends.com/cdn/15.20.1/img/champion/{display_name}.png"

def format_duration(seconds):
    minutes = int(seconds / 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def sort_players_by_role(participants):
    role_order = {"TOP": 1, "JUNGLE": 2, "MIDDLE": 3, "BOTTOM": 4, "UTILITY": 5}
    return sorted(participants, key=lambda p: role_order.get(p.get("teamPosition", "UTILITY"), 6))

def get_display_name_and_aliases(team_name, player, teams_with_puuid=None):
    is_adc_obli = team_name == "Donne ta jungle" and player.get("teamPosition", "").upper() in ["ADC", "BOTTOM"]
    display_name = player.get('riotIdGameName', 'Unknown')
    aliases = [f"{player.get('riotIdGameName', 'Unknown')}#{player.get('riotIdTagline', '???')}"]
    if is_adc_obli and teams_with_puuid:
        team_info = teams_with_puuid.get(team_name, {})
        adc = next((p for p in team_info.get("players", []) if p.get("role") == "ADC"), None)
        if adc and "oldAccounts" in adc:
            for acc in adc["oldAccounts"]:
                aliases.append(f"{acc['gameName']}#{acc['tagLine']}")
            display_name = "Obli"
    return display_name, aliases

def get_team_name_from_players(participants, player_to_team, tournament_matches=None, match_id=None):
    for p in participants:
        names_to_try = []
        game_name = p.get('riotIdGameName', '')
        tag_line = p.get('riotIdTagline', '')
        if game_name and tag_line:
            names_to_try.append(f"{game_name}#{tag_line}")
        if game_name:
            names_to_try.append(game_name)
        if game_name and tag_line:
            names_to_try.append(f"{game_name.replace(' ', '').lower()}#{tag_line.lower()}")
        if game_name:
            names_to_try.append(game_name.replace(' ', '').lower())
        for name in names_to_try:
            for key in player_to_team.keys():
                if name == key or name == key.replace(' ', '').lower():
                    return player_to_team[key]
    if tournament_matches and match_id:
        for team, matches in tournament_matches.items():
            if match_id in matches:
                return team
    return "Équipe Inconnue"

def display_match_card(match_id, match_data, player_to_team, teams_with_puuid=None, tournament_matches=None):
    info = match_data.get("info", {})
    participants = info.get("participants", [])
    teams = info.get("teams", [])
    duration = info.get("gameDuration", 0)
    duration_str = format_duration(duration)
    game_creation = info.get("gameCreation", 0)
    if game_creation:
        game_date = datetime.fromtimestamp(game_creation / 1000)
        date_str = game_date.strftime("%d/%m/%Y %H:%M")
    else:
        date_str = "Date inconnue"
    team_100 = [p for p in participants if p.get("teamId") == 100]
    team_200 = [p for p in participants if p.get("teamId") == 200]
    team_100 = sort_players_by_role(team_100)
    team_200 = sort_players_by_role(team_200)
    team_100_info = next((t for t in teams if t.get("teamId") == 100), {})
    team_200_info = next((t for t in teams if t.get("teamId") == 200), {})
    team_100_win = team_100_info.get("win", False)
    team_200_win = team_200_info.get("win", False)
    team_100_name = get_team_name_from_players(team_100, player_to_team, tournament_matches, match_id)
    team_200_name = get_team_name_from_players(team_200, player_to_team, tournament_matches, match_id)
    if team_100_win:
        match_title = f"🎮 {team_100_name} 🏆 vs {team_200_name}"
    elif team_200_win:
        match_title = f"🎮 {team_100_name} vs {team_200_name} 🏆"
    else:
        match_title = f"🎮 {team_100_name} vs {team_200_name}"
    with st.expander(f"{match_title} - {date_str} ({duration_str})", expanded=False):
        col1, col_vs, col2 = st.columns([5, 1, 5])
        with col1:
            if team_100_win:
                st.markdown(f"### 🔵 **{team_100_name}** ✅ VICTOIRE")
            else:
                st.markdown(f"### 🔵 **{team_100_name}** ❌ DÉFAITE")
            total_kills_100 = sum(p.get("kills", 0) for p in team_100)
            total_gold_100 = sum(p.get("goldEarned", 0) for p in team_100)
            st.metric("Kills", total_kills_100)
            st.metric("Gold total", f"{total_gold_100:,}")
            st.markdown("#### Joueurs")
            for p in team_100:
                display_name, aliases = get_display_name_and_aliases(team_100_name, p, teams_with_puuid)
                champion = p.get("championName", "Unknown")
                # Always display 'Wukong' for MonkeyKing
                if champion in ["MonkeyKing", "Wukong"]:
                    champion_display = "Wukong"
                else:
                    champion_display = champion
                kills = p.get("kills", 0)
                deaths = p.get("deaths", 0)
                assists = p.get("assists", 0)
                cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
                role = p.get("teamPosition", "UNKNOWN")
                kda = f"{kills}/{deaths}/{assists}"
                icon_url = get_champion_icon_url(champion_display)
                role_icon_url = get_role_icon_url(role)
                col_card, col_button = st.columns([5, 1])
                with col_card:
                    player_html = f'''
                    <div style="display: flex; align-items: center; gap: 12px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px; margin-bottom: 6px;">
                        <img src="{icon_url}" style="width: 40px; height: 40px; border-radius: 6px; border: 2px solid rgba(100,150,255,0.3);" title="{champion_display}">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: #e6eef6; font-size: 14px;">
                                <img src="{role_icon_url}" style="width:18px;vertical-align:middle;margin-right:4px;" title="{role}">{display_name}
                            </div>
                            <div style="color: #9fb0c6; font-size: 12px;">{champion_display}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #e6eef6; font-weight: 600;">{kda}</div>
                            <div style="color: #9fb0c6; font-size: 11px;">{cs} CS</div>
                        </div>
                    </div>
                    '''
                    st.markdown(player_html, unsafe_allow_html=True)
                with col_button:
                    if st.button(f"👤 Profil", key=f"profile_{match_id}_100_{display_name}", help=f"Voir les stats de {display_name}"):
                        st.session_state["search_player"] = display_name
                        st.switch_page("pages/6_🔍_Recherche.py")
        with col_vs:
            st.markdown("### VS")
            st.markdown(f"**{duration_str}**")
        with col2:
            if team_200_win:
                st.markdown(f"### 🔴 **{team_200_name}** ✅ VICTOIRE")
            else:
                st.markdown(f"### 🔴 **{team_200_name}** ❌ DÉFAITE")
            total_kills_200 = sum(p.get("kills", 0) for p in team_200)
            total_gold_200 = sum(p.get("goldEarned", 0) for p in team_200)
            st.metric("Kills", total_kills_200)
            st.metric("Gold total", f"{total_gold_200:,}")
            st.markdown("#### Joueurs")
            for p in team_200:
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
                    if st.button(f"👤 Profil", key=f"profile_{match_id}_200_{display_name}", help=f"Voir les stats de {display_name}"):
                        st.session_state["search_player"] = display_name
                        st.switch_page("pages/6_🔍_Recherche.py")
