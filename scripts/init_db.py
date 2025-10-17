"""
Database initialization script
Creates database and initializes schema
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import DatabaseManager
from src.utils.logger import log


def init_database():
    """Initialize the database with schema"""
    try:
        log.info("Initializing database...")
        
        db = DatabaseManager()
        db.connect()
        
        log.info("Creating schema...")
        db.initialize_schema()
        
        log.success("Database initialized successfully!")
        log.info(f"Database location: {db.db_path}")
        
        db.close()
        
    except Exception as e:
        log.error(f"Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
