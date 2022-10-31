"""Demonstrates default logging behavior in Python."""
import logging
from pathlib import Path

# Basic logging settings
filename = f'{Path(__file__).stem}.log'
logging.basicConfig(filename=filename)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.debug('this is my debugging message')
    logger.info('this is my info message')
    logger.warning('this is my warning message')
    logger.error('this is my error message')
    logger.critical('now it is to late !!!')
