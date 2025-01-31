"""change_price"""
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

import time
import random
import re
import sqlite3 as sql
import os
import multiprocessing
import queue
import traceback
from logger_config import logging
from ssl import SSLError
from datetime import datetime
from config import ADMIN_ID
from selenium_driver import get_driver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException, WebDriverException


def change_price(sqlite_connection, cursor):
    """Automatic price change for a product"""
    from main import bot

    message = bot.send_message(ADMIN_ID, f"Идет обновление цен")
    message_id = message.message_id  # Save the message ID

    now_date = datetime.now()
    query = '''SELECT price.* FROM price INNER JOIN sites ON price.site = sites.site_url WHERE price.url IS NOT NULL AND price.url != 'null' AND sites.site_status = 'true' '''
    urls = cursor.execute(query).fetchall()
    total_urls = len(urls)  # Total number of URLs
    processed_urls = 0  # Number of processed URLs

    start_time = time.time()

    q = multiprocessing.Queue()
    random.shuffle(urls)
    for elements in urls:
        q.put(elements)
    time.sleep(0.1)

    max_processes = os.cpu_count() - 1
    running_processes = []
    last_duration = None

    while not q.empty() or running_processes:
        while len(running_processes) < max_processes and not q.empty():
            elements = q.get()
            process = multiprocessing.Process(target=update_price, args=(elements, cursor, sqlite_connection, now_date))
            time.sleep(0.5)
            process.start()
            running_processes.append(process)
            processed_urls += 1  # Increase the number of processed URLs

        for process in running_processes:
            if not process.is_alive():
                process.join()
                running_processes.remove(process)

        end_time = time.time() - start_time
        hours, seconds = divmod(int(end_time), 3600)
        minutes, seconds = divmod(seconds, 60)
        duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        percent = (processed_urls / total_urls) * 100  # Calculate the percentage of completion

        if duration != last_duration:
            bot.edit_message_text(chat_id=ADMIN_ID, message_id=message_id, text=f"Идет обновление цен {duration} ({percent:.2f}/100%)")  # Update the message
            last_duration = duration

        time.sleep(0.1)
    bot.edit_message_text(chat_id=ADMIN_ID, message_id=message_id, text=f"Обновление цен завершено {duration}")  # Update the message



def update_price(elements, cursor, sqlite_connection, now_date):
    from main import bot
    from selenium.common.exceptions import TimeoutException
    product_name = elements[1]
    site = elements[2]
    url = elements[3]
    new = elements[4]
    min = elements[6]
    max = elements[7]
    check_status = elements[9]
    product_hash = elements[10]
    new_price = 0

    if check_status == "false":
        try:
            driver = get_driver()
            driver.get(url)
            time.sleep(10)
            in_stock = check_in_stock(driver, site)
            cursor.execute(f'UPDATE price set in_stock = "{in_stock}" WHERE product_hash = "{product_hash}" AND site = "{site}"')
            sqlite_connection.commit()
            new_price = get_new_price(site, driver)
        except (SSLError, NoSuchWindowException, WebDriverException) as e:
            logging.error(f"\nchange_price\ndef update_price()\n{e}\n{traceback.format_exc()}\n\n")
        except Exception as e:
            logging.error(f"\nchange_price\ndef update_price()\n{e}\n{traceback.format_exc()}\n\n")
        if new_price > 0:
            if new != new_price:
                set_new_price(new, new_price, product_hash, site, cursor, sqlite_connection, now_date, min, max)
        new_price = 0
        check_status = "true"
        cursor.execute('UPDATE price set check_status = ? WHERE product_hash = ? AND site = ?', (check_status, product_hash, site))
        sqlite_connection.commit()

def set_new_price(new, new_price, product_hash, site, cursor, sqlite_connection, now_date, min, max):
    sql_update_query = """UPDATE price set old = ?, new = ?, min = ?, max = ?, change = ? WHERE product_hash = ? AND site = ?"""
    old = 0 if str(new) == "null" else str(new)
    new = int(new_price)
    min = new if min == 0 or int(new) < min else min
    max = new if int(new) > max else max
    change = "true"
    data = (old, new, min, max, change, product_hash, site)
    cursor.execute(sql_update_query, data)
    sqlite_connection.commit()
    sql_update_query = """UPDATE products set product_newtime = ? WHERE product_hash = ?"""
    product_newtime = now_date.strftime("%Y-%m-%d")
    data = (product_newtime, product_hash)
    cursor.execute(sql_update_query, data)
    sqlite_connection.commit()


def get_new_price(site, driver):
    prices = {
        "dns-shop.ru": ('"dimension5",', ')'),
        "mvideo.ru": ('"price__main-value"> ', '₽'),
        "onlinetrade.ru": ('"price" content="', '"'),
        "wildberries.ru": ('"price-block__final-price">', '₽'),
        "citilink.ru": ('"price":"', '"'),
        "eldorado.ru": ('"price":"', '.'),
        "regard.ru": ('"https://schema.org/InStock","price":', ','),
        "ozon.ru": ('"price":"', '"'),
        "detmir.ru": (' купить по цене ', '₽')
    }

    if site not in prices:
        return 0

    try:
        if not driver.window_handles:  # Check if the browser window is still open
            return 0
        page_source = driver.page_source
        start_index = page_source.index(prices[site][0]) + len(prices[site][0])
        end_index = page_source.index(prices[site][1], start_index)
        price = page_source[start_index:end_index]
    except ValueError:
        return 0

    new_price = int(re.sub('\D+', '', price)) if price else 0
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    time.sleep(random.randint(1, 3))
    driver.quit()
    return new_price


def check_in_stock(driver, site):
    texts = {
        "dns-shop.ru": [
                        "Товара нет в наличии", "Продажи прекращены"
                        ],
        "mvideo.ru": "Товар временно отсутствует в продаже",
        "onlinetrade.ru": [
                        "Сообщить о поступлении товара в продажу", "Временно отсутствует"
                        ],
        "wildberries.ru": "Нет в наличии",
        "citilink.ru": [
                        "Сообщить о поступлении", "Нет в наличии", "Введите ваш e-mail"
                        ],
        "eldorado.ru": [
                        "Нет в наличии", "Сообщить о поступлении"
                        ],
        "regard.ru": "Нет в наличии",
        "ozon.ru": "Этот товар закончился",
        "detmir.ru": "Нет в наличии"
    }
    try:
        match = re.search(texts.get(site, ""), driver.page_source)
        if match is None:
            return 'true'
        else:
            return 'false'
    except Exception:
        pass
