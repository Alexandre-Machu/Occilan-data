"""
Recalculate stats for Edition 999 to test the fixed team_stats logic
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.edition_processor import EditionProcessor
from dotenv import load_dotenv
import os

load_dotenv()

def calculate_stats(edition_id: int):
    """Calculate stats for edition"""
    
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        print("❌ RIOT_API_KEY not found in .env")
        return
    
    print(f"\n🔄 Calculating stats for Edition {edition_id}...")
    
    processor = EditionProcessor(edition_id, api_key)
    
    # Step 6: Calculate stats
    stats = processor.step6_calculate_stats()
    
    if not stats:
        print("❌ Failed to calculate stats")
        return
    
    print(f"\n✅ Stats calculated successfully!")
    print(f"   Players: {stats['metadata']['total_players']}")
    print(f"   Matches: {stats['metadata']['total_matches_processed']}")
    print(f"   Teams: {len(stats['team_stats'])}")
    
    # Display team stats
    print(f"\n📊 Team Statistics:")
    for team_name, team_data in stats['team_stats'].items():
        print(f"\n   🏆 {team_name}")
        print(f"      Games: {team_data['games_played']}")
        print(f"      Wins: {team_data['wins']}")
        print(f"      Losses: {team_data['losses']}")
        print(f"      Winrate: {team_data['winrate']:.1f}%")
        print(f"      Total Kills: {team_data['total_kills']}")
        print(f"      Total Deaths: {team_data['total_deaths']}")
    
    # Check if team_stats.json was created
    team_stats_path = Path(f"data/editions/edition_{edition_id}/team_stats.json")
    if team_stats_path.exists():
        print(f"\n✅ team_stats.json created successfully")
    else:
        print(f"\n⚠️ team_stats.json not found")


if __name__ == "__main__":
    calculate_stats(999)
