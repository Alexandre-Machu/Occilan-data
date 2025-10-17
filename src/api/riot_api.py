"""
Riot API Client
Handles all interactions with Riot Games API
"""

import os
from typing import Optional, Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()


class RiotAPIClient:
    """Client for Riot Games API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RIOT_API_KEY")
        if not self.api_key:
            raise ValueError("RIOT_API_KEY not found in environment variables")
        
        self.base_urls = {
            "europe": "https://europe.api.riotgames.com",
            "euw1": "https://euw1.api.riotgames.com",
        }
        
        self.headers = {
            "X-Riot-Token": self.api_key
        }
    
    def get_account_by_riot_id(self, game_name: str, tag_line: str, region: str = "europe") -> Dict:
        """
        Get account information by Riot ID
        
        Args:
            game_name: Player's game name
            tag_line: Player's tag line
            region: Region (default: europe)
            
        Returns:
            Account information including PUUID
        """
        url = f"{self.base_urls[region]}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_summoner_by_puuid(self, puuid: str, platform: str = "euw1") -> Dict:
        """
        Get summoner information by PUUID
        
        Args:
            puuid: Player's PUUID
            platform: Platform (default: euw1)
            
        Returns:
            Summoner information
        """
        url = f"{self.base_urls[platform]}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_match_ids_by_puuid(
        self, 
        puuid: str, 
        start: int = 0, 
        count: int = 20,
        queue: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        region: str = "europe"
    ) -> List[str]:
        """
        Get list of match IDs for a player
        
        Args:
            puuid: Player's PUUID
            start: Start index
            count: Number of matches to retrieve
            queue: Queue ID filter
            start_time: Start timestamp (epoch seconds)
            end_time: End timestamp (epoch seconds)
            region: Region (default: europe)
            
        Returns:
            List of match IDs
        """
        url = f"{self.base_urls[region]}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"start": start, "count": count}
        
        if queue:
            params["queue"] = queue
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_match_details(self, match_id: str, region: str = "europe") -> Dict:
        """
        Get detailed match information
        
        Args:
            match_id: Match ID
            region: Region (default: europe)
            
        Returns:
            Complete match data
        """
        url = f"{self.base_urls[region]}/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_match_timeline(self, match_id: str, region: str = "europe") -> Dict:
        """
        Get match timeline (detailed events)
        
        Args:
            match_id: Match ID
            region: Region (default: europe)
            
        Returns:
            Match timeline data
        """
        url = f"{self.base_urls[region]}/lol/match/v5/matches/{match_id}/timeline"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
