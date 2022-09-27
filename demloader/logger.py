import logging

logger = logging
logger.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', 
                   datefmt='%Y-%m-%d %H:%M:%S',
                   level=logging.INFO)
