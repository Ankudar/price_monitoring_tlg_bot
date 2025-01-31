# """main"""
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
import telebot
import schedule
import work_with_users_message
import add_new_product
import change_user_status
import edit_product_urls
import work_with_sqlite
import work_with_product_plots
import change_price
import send_products_list
import traceback
import os
import requests
import re
import backups
import multiprocessing
from bs4 import BeautifulSoup
from datetime import datetime
from selenium_driver import get_driver
from threading import Thread
from work_with_txt import write_to_logs
from config import TOKEN, ADMIN_ID
from logger_config import logging
from selenium.webdriver.common.by import By
from telebot import apihelper

bot = telebot.TeleBot(TOKEN, parse_mode='HTML', threaded=True)
work_with_users_message.register_commands_from_work_with_users_message(bot)
start_bot_time = datetime.now()


@bot.message_handler()
def check_user_workstatus(message):
    """Проверка ожидаемого действия от юзера"""
    import keyboard
    try:
        chat_id = str(message.chat.id)
        user_name = str(message.from_user.username)
        with sql.connect('sqlite_price_info.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()
            workstatus = cursor.execute("""SELECT * FROM users WHERE chat_id = ?""", (chat_id,)).fetchone()[3]
            if workstatus == "sendadminmessage":
                bot.send_message(ADMIN_ID, "\u203C СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ\n\n" + f"{message.text}" + "\n\n" + f"@{message.from_user.username} ({message.from_user.id})")
            elif workstatus == "addproduct":
                add_new_product.add_new_product(message, chat_id, user_name)
                change_user_status.set_user_status(message, "nothing")
                keyboard.first_keyboard(message)
            elif workstatus == "editurls":
                product_hash = cursor.execute("""SELECT * FROM users WHERE chat_id = ?""", (chat_id,)).fetchone()[4]
                product_name = cursor.execute("""SELECT * FROM products WHERE product_hash = ?""", (product_hash, )).fetchone()[1]
                edit_product_urls.edit_product_urls(message, chat_id, product_hash, product_name)
            elif workstatus == "deleteproduct":
                bot.send_message(chat_id, "Выберите из списка или нажмите <code>Назад</code>")
                send_products_list.send_list(chat_id, message)
            else:
                work_with_sqlite.sql_set_tables_users_default(chat_id, user_name)
            cursor.close()
    except Exception as e:
        logging.error(f"\nmain\ndef check_user_workstatus(message)\n{e}\n{traceback.format_exc()}\n\n")
        work_with_sqlite.sql_set_tables_users_default(chat_id, user_name)
    write_to_logs(message)


def start_bot():
    """действия при старте бота"""
    try:
        bot.send_message(ADMIN_ID, "Я ребутнулся")
        with sql.connect('sqlite_price_info.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()
            cursor.execute("""UPDATE users set workstatus = 'nothing', editurlhash = 'nothing'""")
            sqlite_connection.commit()
    except Exception as e:
        logging.error(f"\nmain\ndef start_bot()\n{e}\n{traceback.format_exc()}\n\n")


def start_main_working():
    try:
        backups.copy_with_date("/from/", "/to/")
        with sql.connect('sqlite_price_info.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()
            work_with_sqlite.sql_delete_old_products(sqlite_connection, cursor)
            time.sleep(1)
            work_with_product_plots.set_new_day_in_plots(sqlite_connection, cursor)
            time.sleep(1)
            edit_product_urls.auto_delete_trash_urls(sqlite_connection, cursor)
            time.sleep(1)
            edit_product_urls.auto_edit_product_urls(sqlite_connection, cursor)
            time.sleep(1)
            change_price.change_price(sqlite_connection, cursor)
            time.sleep(1)
            send_products_list.auto_send_price_info(sqlite_connection, cursor)
            time.sleep(1)
    except Exception as e:
        logging.error(f"\nmain\ndef start_main_working\n{e}\n{traceback.format_exc()}\n\n")
    finally:
        cursor.close()
        sqlite_connection.close()

def sched():
    """бесконечный цикл для работы планировщика"""
    # schedule.every(8).hours.do(start_main_working)
    schedule.every(5).minutes.do(start_main_working)
    # schedule.every(5).seconds.do(start_main_working)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"\nmain\ndef sched()\n{e}\n{traceback.format_exc()}\n\n")
            time.sleep(5)
            continue


def bot_working():
    """команды бота в отдельном потоке"""
    while True:
        try:
            bot.polling(none_stop=True, timeout=120)
        except apihelper.ApiException as e:
            logging.error(f"\nmain\ndef bot_working()\n{e}\n{traceback.format_exc()}\n\n")
            time.sleep(15)  # wait for 15 seconds before trying again
        except Exception as e:
            logging.error(f"\nmain\ndef bot_working()\n{e}\n{traceback.format_exc()}\n\n")
            time.sleep(15)  # wait for 15 seconds before trying again


if __name__ == '__main__':
    start_bot()
    thr1 = Thread(target=bot_working)
    thr1.start()
    thr2 = Thread(target=sched)
    thr2.start()