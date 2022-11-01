"""Demonstrates handler logging behavior in Python."""
import logging
from pathlib import Path

fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Logging to file
filename = f'{Path(__file__).stem}.log'
file_handler = logging.FileHandler(filename=filename)
file_handler.setFormatter(fmt=fmt)
file_handler.setLevel(level='WARNING')

# Logging to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(fmt=fmt)
console_handler.setLevel(level='DEBUG')

# Set the basic config for all the subsequent loggers.
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.debug('this is my debugging message')
    logger.info('this is my info message')
    logger.warning('this is my warning message')
    logger.error('this is my error message')
    logger.critical('now it is to late !!!')
