"""Utility functions for formatting data in the SC-Esport-Stats application."""

def format_champion_name(name: str) -> str:
    """Format champion name for display."""
    if name == "MonkeyKing":
        return "Wukong"
    
    formatted = ""
    for i, char in enumerate(name):
        if i > 0 and char.isupper() and name[i-1].islower():
            formatted += " "
        formatted += char
    return formatted

def get_champion_icon_url(champion_name: str) -> str:
    """Get champion icon URL."""
    formatted_name = champion_name.replace(" ", "")
    if formatted_name == "Wukong":
        formatted_name = "MonkeyKing"
    return f"https://ddragon.leagueoflegends.com/cdn/15.11.1/img/champion/{formatted_name}.png"