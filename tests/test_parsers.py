"""
Unit tests for parsers
"""

import pytest
from src.parsers.opgg_parser import OPGGParser
from src.parsers.csv_parser import CSVParser


class TestOPGGParser:
    """Tests for OP.GG parser"""
    
    def test_extract_riot_ids_valid_url(self):
        """Test extraction from valid OP.GG URL"""
        parser = OPGGParser()
        url = "https://www.op.gg/multisearch/euw?summoners=Player1,Player2,Player3"
        
        result = parser.extract_riot_ids_from_url(url)
        
        assert len(result) == 3
        assert result[0]['game_name'] == 'Player1'
        assert result[0]['tag_line'] == 'EUW'
    
    def test_extract_riot_ids_with_tags(self):
        """Test extraction with explicit tags"""
        parser = OPGGParser()
        url = "https://www.op.gg/multisearch/euw?summoners=Player1%23TAG1,Player2%23TAG2"
        
        result = parser.extract_riot_ids_from_url(url)
        
        assert len(result) == 2
        assert result[0]['game_name'] == 'Player1'
        assert result[0]['tag_line'] == 'TAG1'
    
    def test_validate_opgg_url_valid(self):
        """Test URL validation with valid URL"""
        parser = OPGGParser()
        assert parser.validate_opgg_url("https://www.op.gg/multisearch/euw?summoners=test") is True
    
    def test_validate_opgg_url_invalid(self):
        """Test URL validation with invalid URL"""
        parser = OPGGParser()
        assert parser.validate_opgg_url("https://google.com") is False


class TestCSVParser:
    """Tests for CSV parser"""
    
    def test_get_role_from_position(self):
        """Test role mapping from position"""
        assert CSVParser._get_role_from_position(1) == 'TOP'
        assert CSVParser._get_role_from_position(2) == 'JUNGLE'
        assert CSVParser._get_role_from_position(3) == 'MID'
        assert CSVParser._get_role_from_position(4) == 'ADC'
        assert CSVParser._get_role_from_position(5) == 'SUPPORT'
    
    # TODO: Add more tests with actual CSV files
