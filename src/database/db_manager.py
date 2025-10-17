"""
Database Manager
Handles database connections and operations
"""

import duckdb
from pathlib import Path
from typing import Optional
import yaml


class DatabaseManager:
    """Manager for DuckDB database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to database file. If None, reads from config.
        """
        if db_path is None:
            # Load from config
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
            with open(config_path) as f:
                config = yaml.safe_load(f)
            db_path = config['database']['path']
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        self.connection = duckdb.connect(str(self.db_path))
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_schema(self):
        """Initialize database schema from SQL file"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        if not self.connection:
            self.connect()
        
        # Execute schema (split by semicolon for multiple statements)
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        for statement in statements:
            if statement and not statement.startswith('--'):
                self.connection.execute(statement)
        
        self.connection.commit()
    
    def execute(self, query: str, parameters: Optional[tuple] = None):
        """
        Execute a query
        
        Args:
            query: SQL query
            parameters: Query parameters
            
        Returns:
            Query result
        """
        if not self.connection:
            self.connect()
        
        if parameters:
            return self.connection.execute(query, parameters)
        return self.connection.execute(query)
    
    def fetch_one(self, query: str, parameters: Optional[tuple] = None):
        """Fetch one result"""
        result = self.execute(query, parameters)
        return result.fetchone()
    
    def fetch_all(self, query: str, parameters: Optional[tuple] = None):
        """Fetch all results"""
        result = self.execute(query, parameters)
        return result.fetchall()
    
    def fetch_df(self, query: str, parameters: Optional[tuple] = None):
        """Fetch results as pandas DataFrame"""
        result = self.execute(query, parameters)
        return result.df()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
