import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

from shared import config

logger = None

def get_logger(name):
    global logger

    if logger:
        return logger

    load_dotenv()
    # Retrieve configuration valuessff
    log_level = config.get('LOG_LEVEL', 'debug')
    app_env = config.get('APP_ENV', 'development')
    log_filename = config.get('LOG_FILENAME', 'app.log')

    # Set the logging level
    level = logging.DEBUG if log_level.upper() == 'DEBUG' else logging.INFO

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


    if app_env == 'development':
        # Console handler for development environment
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        # File handler for other environments
        file_handler = RotatingFileHandler(log_filename, maxBytes=10000, backupCount=5)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Avoid duplicate logging
    logger.propagate = False

    return logger


