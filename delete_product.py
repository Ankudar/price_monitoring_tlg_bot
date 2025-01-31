"""delete_old_product"""
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
from config import ADMIN_ID
from logger_config import logging

def delete_product(product_name, chat_id, user_name, product_hash):
    """Удаление позиций из мониторинга"""
    from main import bot
    try:
        with sql.connect('sqlite_price_info.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()
            cursor.execute("DELETE from products where product_hash = ?", (product_hash,))
            cursor.execute("DELETE from price where product_hash = ?", (product_hash,))
            cursor.execute("DELETE from plots where product_hash = ?", (product_hash,))
            sqlite_connection.commit()
            bot.send_message(chat_id, f"<code>{product_name}</code> - позиция удалена, что удалить? Если вы закончили - нажмитие кнопку <code>назад</code>.")
            bot.send_message(ADMIN_ID, f"Удалили - {product_name} (@{user_name}, {chat_id})")
    except Exception as e:
        logging.error(f"\ndelete_product\ndef delete_product(product_name, chat_id, user_name, product_hash)\n{e}\n{traceback.format_exc()}\n\n")
