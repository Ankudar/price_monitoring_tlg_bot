"""send_products_list"""
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
import time
import work_with_sqlite
import traceback
from telebot import types
from config import ADMIN_ID
from logger_config import logging

def send_list(chat_id, message: types.Message):
    """отправляет список мониторинга юзеру"""
    from main import bot
    sqlite_connection = sql.connect('sqlite_price_info.db')
    cursor = sqlite_connection.cursor()
    count = cursor.execute("""SELECT COUNT(chat_id) FROM products WHERE chat_id = ? group by product_name""", (chat_id, )).fetchone()
    if count == 0:
        bot.send_message(chat_id, "Вы ничего не мониторите")
    else:
        all_list = cursor.execute("""SELECT * FROM products WHERE chat_id = ?""", (chat_id, )).fetchall()
        product_number = 1
        keyboard = types.InlineKeyboardMarkup()
        for row in all_list:
            keyboard.add(types.InlineKeyboardButton(text=f"{product_number}) {str(row[1])}", callback_data=f"{str(row[5])}"))
            product_number += 1
        bot.send_message(message.chat.id, "Ваш лист мониторинга", reply_markup=keyboard)
    cursor.close()

def send_price_info(product_name, chat_id, product_hash):
    """отправляет юзеру детализациб цен по товару"""
    from main import bot
    sqlite_connection = sql.connect('sqlite_price_info.db')
    cursor = sqlite_connection.cursor()
    info_list = cursor.execute("""SELECT * FROM price WHERE product_hash = ? ORDER BY new""", (product_hash, )).fetchall()
    count = 1
    price = ""
    for element in info_list:
        product_url = element[2] if element[3] == "null" else element[3]
        new = 0 if element[4] == "null" else element[4]
        if element[11] == 'true':
            in_stock = '\u2705'
        elif element[11] == 'false':
            in_stock = '\u274C'
        else:
            in_stock = '\u2753'
        price1 = str(f"{count}) {in_stock} <a href=\"{product_url}\">{element[2]}</a>: new - {new}, old - {element[5]} ({int(new - element[5])}, min: {element[6]}, max: {element[7]})\n")
        count += 1
        price = price + price1
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f"Динамика цен", callback_data=f"plot {product_hash}"))
    keyboard.add(types.InlineKeyboardButton(text=f"Удалить", callback_data=f"delete {product_hash}"))
    bot.send_message(chat_id, f"<b><i>{product_name}</i></b>\n{price}", disable_web_page_preview = True, reply_markup=keyboard)
    cursor.close()

def auto_send_price_info(sqlite_connection, cursor):
    """отправляет юзеру детализациб цен по товару если есть изменения"""
    from main import bot
    try:
        list1 = cursor.execute("""SELECT * FROM products""").fetchall()
        for elements1 in list1:
            product_hash = str(elements1[5])
            chat_id = elements1[2]
            list2 = cursor.execute("""SELECT COUNT(*) FROM price WHERE product_hash = ? AND change = 'true'""", (product_hash, )).fetchall()
            if list2[0][0] > 0:
                list2 = cursor.execute("""SELECT * FROM price WHERE product_hash = ? ORDER BY new""", (product_hash, )).fetchall()
                count = 1
                price = ""
                for elements2 in list2:
                    product_name = elements2[1]
                    product_url = elements2[2] if elements2[3] == "null" else elements2[3]
                    change = "" if elements2[8] == "false" else '\U0001F503'
                    new = 0 if elements2[4] == "null" else int(elements2[4])
                    if elements2[11] == 'true':
                        in_stock = '\u2705'
                    elif elements2[11] == 'false':
                        in_stock = '\u274C'
                    else:
                        in_stock = '\u2753'
                    price1 = str(f"{count}) {change} {in_stock}<a href=\"{product_url}\">{elements2[2]}</a>: new - {new}, old - {elements2[5]} ({int(new - elements2[5])}, min: {elements2[6]}, max: {elements2[7]})\n")
                    count += 1
                    price = price + price1
                cursor.execute("""UPDATE price set change = 'false' WHERE product_hash = ?""", (product_hash, ))
                time.sleep(1)
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text=f"Динамика цен", callback_data=f"plot {product_hash}"))
                keyboard.add(types.InlineKeyboardButton(text=f"Удалить", callback_data=f"delete {product_hash}"))
                bot.send_message(chat_id, f"<b><i>{product_name}</i></b>\n{price}", disable_web_page_preview = True, reply_markup=keyboard)
    except Exception as e:
        if "400" in str(e):
            bot.send_message(ADMIN_ID, f"слишком длинное сообщение для бота (400) - {chat_id}, {product_hash}")
        elif "403" in str(e):
            bot.send_message(ADMIN_ID, f"заблочили бота (403) - {chat_id}, {product_hash}")
            work_with_sqlite.sql_delete_banned_users(chat_id, product_hash, cursor)
        else:
            bot.send_message(ADMIN_ID, f"auto_send_price_info -> {e}")
        logging.error(f"\nsend_product_list\ndef auto_send_price_info()\n{e}\n{traceback.format_exc()}\n\n")
        # auto_send_price_info()
    sqlite_connection.commit()
