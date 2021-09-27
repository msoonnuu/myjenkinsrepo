#!/usr/bin/python

import os
import os.path
import logging


def get_logger(name='', level='DEBUG',file=''):
    """ Get the Python logger. By default, the level is set to DEBUG but can be changed as needed.\n
    ``name``: Set it to the filename you are calling it from\n
    ``level``: Text logging level for the message ('DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL')
    """
    logging.basicConfig(filename=file,level=logging.DEBUG,format='%(asctime)s - %(name)s: %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger(name)
    levelname = logging.getLevelName(level)
    logger.setLevel(levelname)
    if logger.handlers:
        logger.handlers = []

    # add file handlers
    file_handler = logging.FileHandler(file, mode='w')
    file_handler.setLevel(levelname)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # add Stream Handlers
    console = logging.StreamHandler()
    console.setLevel(levelname)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.propagate = False
    return logger

#logger = get_logger(name='Testing',file='test.log')
#logger.info('Testing one')
