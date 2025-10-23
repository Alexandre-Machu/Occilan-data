"""
Update player: AdriFirst#EUW → BanSkyzoOrParano#SHACO
Fetch PUUID and rank for the new account
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.riot_client import RiotAPIClient
from dotenv import load_dotenv
import os

load_dotenv()

def update_player():
    """Update player and fetch new PUUID and rank"""
    
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        print("❌ RIOT_API_KEY not found in .env")
        return
    
    client = RiotAPIClient(api_key)
    
    # New player info
    new_game_name = "BanSkyzoOrParano"
    new_tag_line = "SHACO"
    
    print(f"\n🔄 Fetching PUUID for {new_game_name}#{new_tag_line}...")
    
    # Step 1: Get PUUID
    account_data = client.get_account_by_riot_id(new_game_name, new_tag_line)
    
    if not account_data:
        print(f"❌ Failed to fetch account data")
        return
    
    puuid = account_data.get("puuid")
    print(f"✅ PUUID: {puuid}")
    
    # Step 2: Get summoner info
    print(f"\n🔄 Fetching summoner info...")
    summoner_data = client.get_summoner_by_puuid(puuid)
    
    if not summoner_data:
        print(f"❌ Failed to fetch summoner data")
        return
    
    summoner_id = summoner_data.get("id")
    summoner_level = summoner_data.get("summonerLevel")
    profile_icon_id = summoner_data.get("profileIconId")
    
    print(f"✅ Summoner Level: {summoner_level}")
    print(f"✅ Profile Icon: {profile_icon_id}")
    
    # Step 3: Get rank
    print(f"\n🔄 Fetching rank...")
    league_data = client.get_league_entries_by_summoner_id(summoner_id)
    
    rank_info = {
        "tier": "UNRANKED",
        "rank": "",
        "leaguePoints": 0,
        "wins": 0,
        "losses": 0,
        "winrate": 0.0
    }
    
    if league_data:
        # Find RANKED_SOLO_5x5
        for entry in league_data:
            if entry.get("queueType") == "RANKED_SOLO_5x5":
                tier = entry.get("tier", "UNRANKED")
                rank = entry.get("rank", "")
                lp = entry.get("leaguePoints", 0)
                wins = entry.get("wins", 0)
                losses = entry.get("losses", 0)
                
                total_games = wins + losses
                winrate = (wins / total_games * 100) if total_games > 0 else 0.0
                
                rank_info = {
                    "tier": tier,
                    "rank": rank,
                    "leaguePoints": lp,
                    "wins": wins,
                    "losses": losses,
                    "winrate": round(winrate, 2)
                }
                
                print(f"✅ Rank: {tier} {rank} - {lp} LP")
                print(f"✅ W/L: {wins}/{losses} ({winrate:.1f}%)")
                break
    else:
        print(f"⚠️ No ranked data found (Unranked)")
    
    # Step 4: Update teams_with_puuid.json
    print(f"\n🔄 Updating teams_with_puuid.json...")
    
    file_path = Path("data/editions/edition_7/teams_with_puuid.json")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
    
    # Find and update the player
    team_name = "On aurait du y penser"
    
    if team_name in teams_data:
        players = teams_data[team_name]["players"]
        
        for player in players:
            if player["gameName"] == "AdriFirst" and player["tagLine"] == "EUW":
                # Update player info
                player["gameName"] = new_game_name
                player["tagLine"] = new_tag_line
                player["puuid"] = puuid
                player["summonerLevel"] = summoner_level
                player["profileIconId"] = profile_icon_id
                player["tier"] = rank_info["tier"]
                player["rank"] = rank_info["rank"]
                player["leaguePoints"] = rank_info["leaguePoints"]
                player["wins"] = rank_info["wins"]
                player["losses"] = rank_info["losses"]
                player["winrate"] = rank_info["winrate"]
                
                print(f"✅ Player updated in team '{team_name}'")
                break
        
        # Save the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(teams_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ File saved: {file_path}")
        
        # Display new player info
        print(f"\n📋 New Player Info:")
        print(f"   Name: {new_game_name}#{new_tag_line}")
        print(f"   Role: JGL")
        print(f"   PUUID: {puuid}")
        print(f"   Level: {summoner_level}")
        print(f"   Rank: {rank_info['tier']} {rank_info['rank']} ({rank_info['leaguePoints']} LP)")
        print(f"   W/L: {rank_info['wins']}/{rank_info['losses']} ({rank_info['winrate']:.1f}%)")
    
    else:
        print(f"❌ Team '{team_name}' not found")


if __name__ == "__main__":
    update_player()
