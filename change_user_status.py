"""change_user_status"""
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

import sqlite3 as sql
import traceback
from logger_config import logging


def set_user_status(message, new_status):
    """изменение статуса пользователя для добавления товара"""
    try:
        with sql.connect('sqlite_price_info.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()
            cursor.execute("UPDATE users SET workstatus = ? WHERE chat_id = ?", (new_status, message.chat.id))
            sqlite_connection.commit()
    except Exception as e:
        logging.error(f"\nchange_user_status\ndef set_user_status(message, new_status)\n{e}\n{traceback.format_exc()}\n\n")


def set_user_editurlhash(product_hash, chat_id):
    """изменение hash url товара с которым работает пользователь"""
    try:
        with sql.connect('sqlite_price_info.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()
            cursor.execute("UPDATE users SET editurlhash = ? WHERE chat_id = ?", (product_hash, chat_id))
            sqlite_connection.commit()
    except Exception as e:
        logging.error(f"\nchange_user_status\ndef set_user_editurlhash(product_hash, chat_id)\n{e}\n{traceback.format_exc()}\n\n")
