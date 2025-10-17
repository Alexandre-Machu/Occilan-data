"""
Logger configuration
Uses loguru for structured logging
"""

import sys
from pathlib import Path
from loguru import logger
import yaml


def setup_logger():
    """Configure logger based on config file"""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    log_config = config.get('logging', {})
    
    # Remove default logger
    logger.remove()
    
    # Console logger
    logger.add(
        sys.stderr,
        level=log_config.get('level', 'INFO'),
        format=log_config.get('format', "{time} | {level} | {message}")
    )
    
    # File logger
    log_file = Path(log_config.get('file', 'logs/occilan_stats.log'))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_file),
        level=log_config.get('level', 'INFO'),
        format=log_config.get('format', "{time} | {level} | {message}"),
        rotation=log_config.get('rotation', '1 day'),
        retention=log_config.get('retention', '7 days'),
        compression=log_config.get('compression', 'zip')
    )
    
    return logger


# Initialize logger
log = setup_logger()
