# Script pour détecter les joueurs non mappés à une équipe dans les matchs
import json
from pathlib import Path

data_dir = Path(__file__).parent.parent.parent / "data" / "editions" / "edition_7"

# Charger le mapping joueur -> équipe
tm_path = data_dir / "team_stats.json"
player_to_team = {}
if tm_path.exists():
    with open(tm_path, "r", encoding="utf-8") as f:
        team_stats_data = json.load(f)
        for team_name, team_data in team_stats_data.items():
            players = team_data.get("players", {})
            for player_key, player_data in players.items():
                game_name = player_data.get("gameName") or player_data.get("player_name")
                tag_line = player_data.get("tagLine") or ""
                if game_name and tag_line:
                    player_to_team[f"{game_name}#{tag_line}"] = team_name
                    player_to_team[f"{game_name.replace(' ', '').lower()}#{tag_line.lower()}"] = team_name
                if game_name:
                    player_to_team[game_name] = team_name
                    player_to_team[game_name.replace(' ', '').lower()] = team_name

# Charger les matchs
match_details_path = data_dir / "match_details.json"
not_found = set()
if match_details_path.exists():
    with open(match_details_path, "r", encoding="utf-8") as f:
        match_details = json.load(f)
        for match_id, match_data in match_details.items():
            for p in match_data.get("info", {}).get("participants", []):
                game_name = p.get('riotIdGameName', '')
                tag_line = p.get('riotIdTagline', '')
                names_to_try = []
                if game_name and tag_line:
                    names_to_try.append(f"{game_name}#{tag_line}")
                if game_name:
                    names_to_try.append(game_name)
                if game_name and tag_line:
                    names_to_try.append(f"{game_name.replace(' ', '').lower()}#{tag_line.lower()}")
                if game_name:
                    names_to_try.append(game_name.replace(' ', '').lower())
                found = False
                for name in names_to_try:
                    for key in player_to_team.keys():
                        if name == key or name == key.replace(' ', '').lower():
                            found = True
                            break
                    if found:
                        break
                if not found:
                    not_found.add(f"{game_name}#{tag_line}")

if not_found:
    print("Joueurs non mappés à une équipe :")
    for n in sorted(not_found):
        print(n)
else:
    print("Tous les joueurs sont mappés à une équipe.")
