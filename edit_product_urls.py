"""edit_product_urls"""
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
import re
import time
import traceback
import os
import multiprocessing
from datetime import datetime
from config import ADMIN_ID
from logger_config import logging
from selenium_driver import get_driver
from selenium.common.exceptions import StaleElementReferenceException

def edit_product_urls(message, chat_id, product_hash, product_name):
    """Редактирование ссылок продукта"""
    from main import bot
    sqlite_connection = sql.connect('sqlite_price_info.db')
    cursor = sqlite_connection.cursor()
    message_if_wrong_site = """Необходимо прислать <code>одну</code> ссылку на товар из поддерживаемого магазина без постороннего текста:
                <code>https://citilink.ru/</code>
                <code>https://dns-shop.ru/</code>
                <code>https://mvideo.ru/</code>
                <code>https://wildberries.ru</code>
                <code>https://regard.ru/</code>
                <code>https://onlinetrade.ru/</code>
                <code>https://ozon.ru/</code>
                <code>https://eldorado.ru</code>
                <code>https://detmir.ru</code>"""
    arr = []
    sites = cursor.execute("""SELECT * FROM sites""").fetchall()
    for elements in sites:
        arr = arr + [elements[1]]
    new_url = str(message.text)
    match = re.search("^(?:((?:https?|s?ftp):)\/\/www\.)([^:\/\s]+)(?::(\d*))?(?:\/([^\s?#]+)?([?][^?#]*)?(#.*)?)?", new_url)
    if match is not None:
        for element in arr:
            match = re.search(element, new_url)
            if match:
                try:
                    sql_update_query = """UPDATE price SET url = ?, new = ?, old = ?, min = ?, max = ?, change = ?, check_status = ? WHERE product_hash = ? AND site = ?"""
                    new = "null"
                    old = min = max = 0
                    change = check_status = "false"
                    url = str(message.text)
                    site = element
                    data = (url, new, old, min, max, change, check_status, product_hash, site)
                    cursor.execute(sql_update_query, data)
                    sqlite_connection.commit()
                    cursor.close()
                    bot.send_message(chat_id, f"""Готово!
Для товара <code>{product_name}</code>
В магазине <code>{element}</code>
Установлена ссылка <code>{new_url}</code>""")
                except Exception as e:
                    logging.error(f"\nedit_product_urls\ndef edit_product_urls(message, chat_id, product_hash, product_name)\n{e}\n{traceback.format_exc()}\n\n")
                finally:
                    if sqlite_connection:
                        sqlite_connection.close()
    else:
        bot.send_message(chat_id, message_if_wrong_site)

def auto_delete_trash_urls(sqlite_connection, cursor):
    # """Автоматически удаляем трэш ссылку"""
    from main import bot
    try:
        cursor.execute('SELECT url FROM price')
        prices = cursor.fetchall()
        cursor.execute('SELECT trash_url FROM trash_urls')
        trash_urls = cursor.fetchall()
        for price in prices:
            if price[0] in [item[0] for item in trash_urls]:
                cursor.execute(f"UPDATE price SET url = 'null' WHERE url = '{price[0]}'")
        sqlite_connection.commit()
    except sql.Error as e:
        logging.error(f"\nedit_product_urls\ndef auto_delete_trash_urls\n{e}\n{traceback.format_exc()}\n\n")

def get_trash_urls(cursor):
    cursor.execute("SELECT trash_url FROM trash_urls")
    return [row[0] for row in cursor.fetchall()]

def auto_edit_product_urls(sqlite_connection, cursor):
    """Автоматический поиск ссылок продукта"""
    from main import bot

    start_time = time.time()
    message = bot.send_message(ADMIN_ID, "Идет обновление ссылок")
    message_id = message.message_id  # Save the message ID
    query = '''SELECT price.* FROM price INNER JOIN sites ON price.site = sites.site_url WHERE price.url IS NOT NULL AND price.url = 'null' AND sites.site_status = 'true' '''
    urls = cursor.execute(query).fetchall()
    trash_urls = get_trash_urls(cursor)
    last_duration = None
    duration = "00:00:00"  # Initialize duration
    driver = get_driver()

    for elements in urls:
        worker_task(elements, cursor, sqlite_connection, trash_urls, driver)
        end_time = time.time() - start_time
        hours, seconds = divmod(int(end_time), 3600)
        minutes, seconds = divmod(seconds, 60)
        duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        if duration != last_duration:
            bot.edit_message_text(chat_id=ADMIN_ID, message_id=message_id, text=f"Идет обновление ссылок {duration}")  # Update the message
            last_duration = duration

    bot.edit_message_text(chat_id=ADMIN_ID, message_id=message_id, text=f"Подбор ссылок завершен: {duration}")  # Update the message
    driver.quit()


def worker_task(elements, cursor, sqlite_connection, trash_urls, driver):
    product_name = elements[1]
    site = elements[2]
    product_hash = elements[10]
    url = f"https://duckduckgo.com/?q=site:{site} {product_name}"
    try:
        driver.get(url)
        time.sleep(10)
        elems = driver.find_elements('xpath', "//a[@href]")
        elems = filter(lambda x: f"www.{site}" in x.get_attribute("href"), elems)
        iteration_count = 0
        for new_url in elems:
            driver.get(new_url.get_attribute("href"))
            sql_update_query = """UPDATE price SET url = ? WHERE product_hash = ? AND site = ?"""
            url = driver.current_url
            if url in trash_urls:
                iteration_count += 1
                if iteration_count >= 20:
                    break
                else:
                    continue
            match = re.search("^(?:((?:https?|s?ftp):)\/\/www\.)([^:\/\s]+)\/$", url)
            if match is None:
                data = (url, product_hash, site)
                cursor.execute(sql_update_query, data)
                sqlite_connection.commit()
                break
    except Exception as e:
        logging.error(f"\nedit_product_urls\ndef auto_edit_product_urls({product_name}, {site}, {product_hash})\n{e}\n{traceback.format_exc()}\n\n")
