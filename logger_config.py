# # """logger_config.py"""
# pylint: disable-msg=too-many-locals
# pylint: disable-msg=too-many-statements
# pylint: disable-msg=line-too-long
# pylint: disable-msg=maybe-no-member
# pylint: disable-msg=import-outside-toplevel
# pylint: disable-msg=too-many-branches
# pylint: disable-msg=wrong-import-order
# pylint: disable-msg=bare-except
# pylint: disable-msg=unnecessary-pass
# pylint: disable-msg=broad-except
# pylint: disable-msg=too-many-nested-blocks
# pylint: disable-msg=logging-fstring-interpolation

import logging
import traceback
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s %(funcName)15s:%(lineno)-3d %(message)s')

file_handler = logging.FileHandler('errors.log', mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.NOTSET)
logger.addHandler(file_handler)


def log_exception(ex, level=logging.ERROR):
    logger.log(level, 'Exception caught:', exc_info=ex)


def log_message(msg, level=logging.INFO):
    logger.log(level, msg)


def log_file_info(filename, level=logging.WARNING):
    logger.log(level, f"File {filename} doesn't exist")


try:
    log_message('Программа запущена.')
except Exception as ex:
    log_exception(ex)
