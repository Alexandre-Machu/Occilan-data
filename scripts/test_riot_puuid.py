import requests
import urllib.parse
import os

RIOT_API_KEY = os.getenv("RIOT_API_KEY", "RGAPI-f8f5b850-daab-4812-98ec-b47d53882d69")

def get_puuid(game_name, tag_line):
    base_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
    # Encode game name and tag line for URL
    game_name_enc = urllib.parse.quote(game_name)
    tag_line_enc = urllib.parse.quote(tag_line)
    url = f"{base_url}{game_name_enc}/{tag_line_enc}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    resp = requests.get(url, headers=headers)
    try:
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e), "status_code": resp.status_code, "response": resp.text}

if __name__ == "__main__":
    test_cases = [
        ("eomer", "FEUR"),
        ("Eomer", "FEUR"),
        ("eomer ", "FEUR"),
        ("eomer", "feur"),
        ("vote yes", "2kis"),
        ("Vote Yes", "2kis"),
        ("vote%20yes", "2kis"),
        ("vote yes ", "2kis"),
        ("vote yes", "2KIS"),
        ("vote yes", "2kis "),
    ]
    for name, tag in test_cases:
        print(f"Testing '{name}#{tag}'...")
        result = get_puuid(name, tag)
        print(result)
