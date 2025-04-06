"""Centralized logging configuration."""
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(logger_name):
    """
    Configure logging to both console and file.
    
    Args:
        logger_name (str): Name of the logger
        
    Returns:
        logger: Configured logging object
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('../logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp for log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'{logger_name}_{timestamp}.log'
    
    # Configure logging
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f'Log file created at: {log_file}')
    return logger