"""
Database Models
Defines data classes for database entities
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Edition:
    """Tournament edition"""
    name: str
    year: int
    start_date: str
    end_date: str
    region: str = "EUW"
    format: str = "swiss_playoffs"
    num_teams: int = 16
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Team:
    """Tournament team"""
    edition_id: int
    name: str
    tag: Optional[str] = None
    opgg_link: Optional[str] = None
    seed: Optional[int] = None
    final_rank: Optional[int] = None
    swiss_record: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Player:
    """Player with Riot account info"""
    team_id: int
    role: str
    riot_id: Optional[str] = None
    game_name: Optional[str] = None
    tag_line: Optional[str] = None
    puuid: Optional[str] = None
    summoner_id: Optional[str] = None
    account_id: Optional[str] = None
    nickname: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Match:
    """Match/Game data"""
    match_id: str
    edition_id: int
    game_creation: int
    game_start: int
    game_end: int
    game_duration: int
    game_mode: str
    game_type: str
    game_version: str
    map_id: int
    platform_id: str
    queue_id: int
    phase: str
    winning_team: str
    blue_team_id: Optional[int] = None
    red_team_id: Optional[int] = None
    tournament_code: Optional[str] = None
    match_number: Optional[int] = None
    first_blood_team: Optional[str] = None
    first_tower_team: Optional[str] = None
    first_baron_team: Optional[str] = None
    first_dragon_team: Optional[str] = None
    first_inhibitor_team: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Participant:
    """Player performance in a match"""
    match_id: int
    player_id: int
    team_id: int
    participant_id: int
    team_position: str
    champion_id: int
    champion_name: str
    
    # Combat
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    
    # Farming
    total_minions_killed: int = 0
    neutral_minions_killed: int = 0
    
    # Gold
    gold_earned: int = 0
    gold_spent: int = 0
    
    # Damage
    total_damage_to_champions: int = 0
    damage_dealt_to_objectives: int = 0
    damage_dealt_to_turrets: int = 0
    
    # Vision
    vision_score: int = 0
    wards_placed: int = 0
    wards_killed: int = 0
    
    # Outcome
    win: bool = False
    
    # Derived stats
    kda: Optional[float] = None
    cs_per_min: Optional[float] = None
    gold_per_min: Optional[float] = None
    damage_per_min: Optional[float] = None
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class PlayerStats:
    """Aggregated player statistics"""
    player_id: int
    edition_id: int
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    
    avg_kills: float = 0.0
    avg_deaths: float = 0.0
    avg_assists: float = 0.0
    avg_kda: float = 0.0
    
    total_kills: int = 0
    total_deaths: int = 0
    total_assists: int = 0
    
    avg_cs_per_min: float = 0.0
    avg_gold_per_min: float = 0.0
    avg_damage_per_min: float = 0.0
    avg_vision_score_per_min: float = 0.0
    
    avg_kill_participation: float = 0.0
    
    most_played_champion: Optional[str] = None
    most_played_champion_games: int = 0
    
    id: Optional[int] = None
    updated_at: Optional[datetime] = None


@dataclass
class TeamStats:
    """Aggregated team statistics"""
    team_id: int
    edition_id: int
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    
    avg_kills: float = 0.0
    avg_deaths: float = 0.0
    avg_assists: float = 0.0
    
    first_blood_rate: float = 0.0
    first_tower_rate: float = 0.0
    
    avg_game_duration: float = 0.0
    
    id: Optional[int] = None
    updated_at: Optional[datetime] = None
