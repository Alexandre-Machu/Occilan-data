"""
Generate team_stats.json from general_stats.json
This creates the team aggregated stats needed by Stats Équipes page
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def generate_team_stats(edition_id: int):
    """Generate team_stats.json from general_stats.json"""
    
    edition_path = Path(__file__).parent.parent / "data" / "editions" / f"edition_{edition_id}"
    
    # Load files
    general_stats_path = edition_path / "general_stats.json"
    teams_with_puuid_path = edition_path / "teams_with_puuid.json"
    output_path = edition_path / "team_stats.json"
    
    if not general_stats_path.exists():
        print(f"❌ {general_stats_path} not found")
        return
    
    if not teams_with_puuid_path.exists():
        print(f"❌ {teams_with_puuid_path} not found")
        return
    
    # Load data
    with open(general_stats_path, "r", encoding="utf-8") as f:
        general_stats = json.load(f)
    
    with open(teams_with_puuid_path, "r", encoding="utf-8") as f:
        teams_with_puuid = json.load(f)
    
    # Create player_to_team mapping
    player_to_team = {}
    for team_name, team_data in teams_with_puuid.items():
        for player in team_data.get("players", []):
            riot_id = f"{player.get('gameName')}#{player.get('tagLine')}"
            player_to_team[riot_id] = team_name
    
    # Group player stats by team
    team_stats = defaultdict(lambda: {
        "team_stats": {
            "games": 0,
            "wins": 0,
            "losses": 0,
            "kills": 0,
            "deaths": 0,
            "assists": 0,
            "cs": 0,
            "gold": 0,
            "damage": 0,
            "vision_score": 0,
            "game_duration": 0
        },
        "players": {}
    })
    
    # Aggregate stats
    for riot_id, player_stats in general_stats.items():
        team_name = player_to_team.get(riot_id)
        if not team_name:
            print(f"⚠️  Player {riot_id} not found in teams_with_puuid.json")
            continue
        
        # Add player stats
        team_stats[team_name]["players"][riot_id] = player_stats
        
        # Aggregate team stats
        ts = team_stats[team_name]["team_stats"]
        ts["games"] += player_stats.get("games", 0)
        ts["wins"] += player_stats.get("wins", 0)
        ts["losses"] += player_stats.get("losses", 0)
        ts["kills"] += player_stats.get("kills", 0)
        ts["deaths"] += player_stats.get("deaths", 0)
        ts["assists"] += player_stats.get("assists", 0)
        ts["cs"] += player_stats.get("cs", 0)
        ts["gold"] += player_stats.get("gold", 0)
        ts["damage"] += player_stats.get("damage", 0)
        ts["vision_score"] += player_stats.get("vision_score", 0)
        
        # Sum duration for average calculation
        for match in player_stats.get("matches", []):
            ts["game_duration"] += match.get("duration", 0)
    
    # Calculate averages for each team
    for team_name, data in team_stats.items():
        ts = data["team_stats"]
        num_players = len(data["players"])
        
        if num_players > 0:
            # Average games per player
            ts["avg_games_per_player"] = ts["games"] / num_players
            
            # Win rate
            if ts["games"] > 0:
                ts["winrate"] = (ts["wins"] / ts["games"]) * 100
            else:
                ts["winrate"] = 0
            
            # KDA
            if ts["deaths"] > 0:
                ts["kda"] = (ts["kills"] + ts["assists"]) / ts["deaths"]
            else:
                ts["kda"] = ts["kills"] + ts["assists"]
            
            # Per game averages
            if ts["games"] > 0:
                ts["kills_per_game"] = ts["kills"] / ts["games"]
                ts["deaths_per_game"] = ts["deaths"] / ts["games"]
                ts["assists_per_game"] = ts["assists"] / ts["games"]
                ts["cs_per_game"] = ts["cs"] / ts["games"]
                ts["gold_per_game"] = ts["gold"] / ts["games"]
                ts["damage_per_game"] = ts["damage"] / ts["games"]
                ts["vision_per_game"] = ts["vision_score"] / ts["games"]
    
    # Save team_stats.json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dict(team_stats), f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated {output_path}")
    print(f"   Teams: {len(team_stats)}")
    print(f"   Total players: {sum(len(data['players']) for data in team_stats.values())}")
    
    # Display team summary
    for team_name, data in sorted(team_stats.items()):
        ts = data["team_stats"]
        print(f"   • {team_name}: {len(data['players'])} players, {ts['games']} games, {ts['winrate']:.1f}% WR")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_team_stats.py <edition_id>")
        print("Example: python generate_team_stats.py 999")
        sys.exit(1)
    
    edition_id = int(sys.argv[1])
    generate_team_stats(edition_id)
