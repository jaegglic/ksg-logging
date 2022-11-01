"""Demonstrates rotating logging behavior in Python."""
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(level=logging.DEBUG)

filename = f'{Path(__file__).stem}.log'
fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
rh = RotatingFileHandler(filename=filename, maxBytes=300, backupCount=10)
rh.setLevel('DEBUG')
rh.setFormatter(fmt)
logger.addHandler(rh)

if __name__ == '__main__':
    for i in range(100):
        logger.debug(f"Hello, World! (count: {i:3})")
