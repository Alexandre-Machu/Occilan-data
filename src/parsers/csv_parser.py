"""
CSV Parser
Handles CSV file imports for team and player data
"""

import pandas as pd
from typing import List, Dict
from pathlib import Path


class CSVParser:
    """Parser for CSV team imports"""
    
    @staticmethod
    def parse_teams_csv(csv_path: str) -> List[Dict]:
        """
        Parse teams CSV file
        
        Expected CSV format:
        team_name,player1,player2,player3,player4,player5,opgg_link
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of team dictionaries
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        # Validate required columns
        required_columns = ['team_name', 'opgg_link']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        teams = []
        for _, row in df.iterrows():
            team = {
                'name': row['team_name'],
                'opgg_link': row['opgg_link'],
                'players': []
            }
            
            # Extract player names (player1, player2, etc.)
            for i in range(1, 6):
                player_col = f'player{i}'
                if player_col in row and pd.notna(row[player_col]):
                    team['players'].append({
                        'nickname': row[player_col],
                        'role': CSVParser._get_role_from_position(i)
                    })
            
            teams.append(team)
        
        return teams
    
    @staticmethod
    def _get_role_from_position(position: int) -> str:
        """Map position number to role"""
        role_map = {
            1: 'TOP',
            2: 'JUNGLE',
            3: 'MID',
            4: 'ADC',
            5: 'SUPPORT'
        }
        return role_map.get(position, 'UNKNOWN')
    
    @staticmethod
    def validate_csv_format(csv_path: str) -> tuple[bool, List[str]]:
        """
        Validate CSV file format
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            df = pd.read_csv(csv_path)
            
            # Check required columns
            required_columns = ['team_name', 'opgg_link']
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")
            
            # Check for at least some player columns
            player_columns = [f'player{i}' for i in range(1, 6)]
            has_player_columns = any(col in df.columns for col in player_columns)
            if not has_player_columns:
                errors.append("No player columns found (player1, player2, etc.)")
            
            # Check for empty rows
            if df.empty:
                errors.append("CSV file is empty")
            
            return len(errors) == 0, errors
        
        except Exception as e:
            errors.append(f"Failed to read CSV: {str(e)}")
            return False, errors
