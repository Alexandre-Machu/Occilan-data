"""
Generate team_stats.json from general_stats.json for Edition 999
"""

import json
from pathlib import Path

def generate_team_stats(edition_id: int):
    """Generate team_stats.json from general_stats.json"""
    
    edition_path = Path(f"data/editions/edition_{edition_id}")
    general_stats_path = edition_path / "general_stats.json"
    team_stats_path = edition_path / "team_stats.json"
    
    # Load general_stats
    if not general_stats_path.exists():
        print(f"❌ {general_stats_path} not found")
        return
    
    with open(general_stats_path, 'r', encoding='utf-8') as f:
        general_stats = json.load(f)
    
    # Check structure
    print(f"Keys in general_stats: {list(general_stats.keys())}")
    
    # Check if team_stats exists in general_stats
    if "team_stats" in general_stats:
        team_stats = general_stats["team_stats"]
        print(f"\n✅ Found team_stats in general_stats ({len(team_stats)} teams)")
        
        # Save to team_stats.json
        with open(team_stats_path, 'w', encoding='utf-8') as f:
            json.dump(team_stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to {team_stats_path}")
        
        # Display teams
        for team_name, team_data in team_stats.items():
            print(f"\nTeam: {team_name}")
            print(f"  Games: {team_data.get('games_played', 0)}")
            print(f"  Wins: {team_data.get('wins', 0)}")
            print(f"  Winrate: {team_data.get('winrate', 0):.1f}%")
    
    else:
        print("\n❌ team_stats not found in general_stats")
        print("   Run the pipeline again to recalculate stats")


if __name__ == "__main__":
    generate_team_stats(999)
