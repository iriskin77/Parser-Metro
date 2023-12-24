import logging
from typing import Literal


def init_logger(name: str, level: int | Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = logging.INFO):


    if isinstance(level, str):
        level = getattr(logging, level)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    console_log = logging.StreamHandler()
    file_log = logging.FileHandler(filename='mparser\\logs.log', mode='a')
    console_log.setFormatter(logging.Formatter(
        '%(asctime)s, — %(levelname)s — module: %(name)s — %(message)s'))
    file_log.setFormatter(logging.Formatter(
        '%(asctime)s, — %(levelname)s — module: %(name)s — %(message)s'))
    logger.addHandler(console_log)
    logger.addHandler(file_log)

    return logger
