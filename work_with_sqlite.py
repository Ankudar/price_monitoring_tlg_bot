"""work_with_sqlite"""
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
import datetime
import traceback
import work_with_product_plots
import edit_product_urls
from config import ADMIN_ID
from logger_config import logging


now_date = datetime.datetime.now()
now_day = now_date.strftime("%d")
now_date = now_date.strftime("%d-%m-%Y")


def drop_user_workstatus(message):
    """сбросить workstatus и editurlhash пользователя"""
    from main import bot
    try:
        sqlite_connection = sql.connect('sqlite_price_info.db')
        cursor = sqlite_connection.cursor()

        sql_update_query = """UPDATE users set workstatus = ? where chat_id = ?"""
        workstatus = "nothing"
        chat_id = message.chat.id
        data = (workstatus, chat_id)
        cursor.execute(sql_update_query, data)
        sqlite_connection.commit()
        cursor.close()
    except Exception as e:
        logging.error(f"\nwork_with_sqlite\ndef drop_user_workstatus(message)\n{e}\n{traceback.format_exc()}\n\n")
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def sql_set_tables_users_default(chat_id, user_name):
    """создание таблицы sql"""
    from main import bot
    try:
        sqlite_connection = sql.connect('sqlite_price_info.db')
        sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS users (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                chat_id INTEGER NOT NULL UNIQUE,
                                user_name TEXT,
                                workstatus TEXT,
                                editurlhash TEXT,
                                product_limit INTEGER);'''
        cursor = sqlite_connection.cursor()
        cursor.execute(sqlite_create_table_query)
        info = cursor.execute("""SELECT * FROM users WHERE chat_id = ?""", (chat_id, ))
        if info.fetchone() is None:
            cursor.execute("""INSERT INTO users (chat_id, user_name, workstatus, editurlhash, product_limit) VALUES (?, ?, ?, ?, ?)""", (chat_id, user_name, "nothing", "nothing", 3))
            sqlite_connection.commit()
            cursor.close()
    except Exception as e:
        logging.error(f"\nwork_with_sqlite\nsql_set_tables_users_default(chat_id, user_name)\n{e}\n{traceback.format_exc()}\n\n")
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def sql_delete_old_products(sqlite_connection, cursor): #datetime.strptime("01.02.2017", "%d.%m.%Y")
    """удаление позиций старше 6 месяцев и если не было 3 месяца обновления цен"""
    from main import bot
    now_date = datetime.datetime.today()
    try:
        products = cursor.execute("""SELECT * FROM products""").fetchall()
        for element in products:
            add_date = datetime.datetime.strptime(f"{element[3]}", "%Y-%m-%d")
            change_date = datetime.datetime.strptime(f"{element[4]}", "%Y-%m-%d")
            product_hash = element[5]
            if (now_date - add_date).days > 180 or (now_date - change_date).days > 60:
                cursor.execute("""DELETE from products where product_hash = ?""", (product_hash,))
                cursor.execute("""DELETE from price where product_hash = ?""", (product_hash,))
                cursor.execute("""DELETE from plots where product_hash = ?""", (product_hash,))
            else:
                cursor.execute(f'UPDATE products set delete_old = "{180 - (now_date - add_date).days}", delete_without_change = "{60 - (now_date - change_date).days}" where product_hash = "{product_hash}"')
            sqlite_connection.commit()
    except Exception as e:
        logging.error(f"\nwork_with_sqlite\ndef sql_delete_old_products()\n{e}\n{traceback.format_exc()}\n\n")

def sql_delete_banned_users(chat_id, product_hash, cursor):
    """удаление позиций и юзера который заблочил бота"""
    cursor.execute("""DELETE from users where chat_id = ?""", (chat_id,))
    cursor.execute("""DELETE from products where chat_id = ?""", (chat_id,))
    cursor.execute("""DELETE from price where product_hash = ?""", (product_hash,))
    cursor.execute("""DELETE from plots where product_hash = ?""", (product_hash,))
    return
