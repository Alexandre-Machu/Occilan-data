import json
from pathlib import Path

# Load match details
data = json.load(open('data/editions/edition_999/match_details.json', encoding='utf-8'))
match = list(data.values())[0]
participants = match['info']['participants']

print('\nPositions for first match:')
for i, p in enumerate(participants[:10], 1):
    name = p.get('summonerName', 'Unknown')
    team_pos = p.get('teamPosition', 'N/A')
    ind_pos = p.get('individualPosition', 'N/A')
    team_id = p.get('teamId', 0)
    print(f"  {i}. {name:20} Team {team_id} - teamPosition: {team_pos:10} individualPosition: {ind_pos}")
