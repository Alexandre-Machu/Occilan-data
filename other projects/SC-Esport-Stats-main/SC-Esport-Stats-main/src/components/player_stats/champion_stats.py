from dataclasses import dataclass
from src.utils.formatters import format_champion_name, get_champion_icon_url

@dataclass
class ChampionStats:
    name: str
    games: int
    winrate: float
    kda: float
    kp: float

    @property
    def icon_url(self) -> str:
        return get_champion_icon_url(self.name)

    @property
    def wr_color(self) -> str:
        return "#4CAF50" if self.winrate >= 50 else "#F44336"

def get_champion_stats(player_id: str) -> list[ChampionStats]:
    # Logique pour récupérer les stats
    pass
