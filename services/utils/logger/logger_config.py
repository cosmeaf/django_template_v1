import logging
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../logs')
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str, filename="default.log", level="DEBUG"):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter('[{levelname}] {asctime} - {name} - {message}', style='{')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(os.path.join(LOG_DIR, filename))
    file_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger
