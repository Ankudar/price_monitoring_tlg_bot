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

import traceback
import sqlite3 as sql
from datetime import datetime
from main import bot
from config import ADMIN_ID
from logger_config import logging

def set_new_day_in_plots(sqlite_connection, cursor):
    """Добавляем новый день"""
    current_datetime = datetime.now()

    try:
        # Добавить новый столбец в базу данных
        last_date = cursor.execute('PRAGMA table_info(plots)').fetchall()[-1][1]
        now_date = f"{current_datetime.day}.{current_datetime.month}."
        if last_date != now_date:
            cursor.execute(f'alter table plots add column "{now_date}" "INTEGER"')
            transfer_data_to_new_day(now_date, cursor, sqlite_connection)
    except Exception as e:
        logging.error(f"\nwork_with_product_plots\ndef set_new_day_in_plots()\n{e}\n{traceback.format_exc()}\n\n")
    count = cursor.execute("""SELECT COUNT(*) FROM pragma_table_info('plots')""").fetchone()[0]
    if count > 34:
        old_data = cursor.execute('PRAGMA table_info(plots)').fetchall()[4][1]
        cursor.execute(f'alter table plots drop column "{old_data}"')


def transfer_data_to_new_day(now_date, cursor, sqlite_connection):
    """Перемещаем"""
    try:
        data = cursor.execute("""SELECT product_name, site, product_hash, new FROM price""").fetchall()
        for element in data:
            product_hash = str(element[2])
            site = str(element[1])

            info = cursor.execute(f'SELECT * FROM plots WHERE product_hash = "{product_hash}" AND site = "{site}"').fetchone()
            if info is None:
                cursor.execute(f'INSERT INTO plots (product_name, site, product_hash, "{now_date}") VALUES (?, ?, ?, ?)', (str(element[0]), str(element[1]), str(element[2]), str(element[3])))
            else:
                cursor.execute(f'UPDATE plots SET "{now_date}" = "{str(element[3])}" WHERE product_hash = "{product_hash}" AND site = "{site}"')
        sqlite_connection.commit()

        cursor.execute(f'UPDATE plots SET "{now_date}" = NULL WHERE "{now_date}" = "null"')
        sqlite_connection.commit()

    except Exception as e:
        logging.error(f"\nwork_with_product_plots\ndef transfer_data_to_new_day()\n{e}\n{traceback.format_exc()}\n\n")

def send_plots(product_name, chat_id, inline_hash):
    import matplotlib.pyplot as plt

    current_datetime = datetime.now()
    now_date = f"{current_datetime.day}.{current_datetime.month}."

    sqlite_connection = sql.connect('sqlite_price_info.db')
    cursor = sqlite_connection.cursor()

    all_days = cursor.execute('PRAGMA table_info(plots)').fetchall()
    x = []
    for days in all_days[4:]:
        x.append(f"{days[1]}")

    product_plot = cursor.execute(f'SELECT * FROM plots WHERE product_hash = "{inline_hash}" ORDER BY "{now_date}"').fetchall()

    for element in product_plot:
        site = element[2]
        y = element[4:]
        if any(val is not None for val in y):
            plt.plot(x, y, marker=".", label=f'{site}')

    plt.legend(ncol=4, facecolor='oldlace', loc='center', bbox_to_anchor=(0.48, 1.08))
    plt.ylabel(f'{product_name}')
    plt.xticks(rotation=90)
    plt.grid()
    plt.savefig('temp_pot.png')
    plt.close()
    bot.send_photo(chat_id, photo=open('temp_pot.png', 'rb'))

    sqlite_connection.close()
