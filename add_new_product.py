"""add_new_product"""
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
import random
import re
import traceback
import time
from config import ADMIN_ID
from logger_config import logging
from selenium_driver import get_driver


def add_new_product(message, chat_id, user_name):
    """добавление нового продукта в sql"""
    from main import bot
    now_date = datetime.datetime.now()
    driver = get_driver()
    try:
        sqlite_connection = sql.connect('sqlite_price_info.db')
        cursor = sqlite_connection.cursor()
        count = cursor.execute("""SELECT COUNT(chat_id) FROM products WHERE chat_id = ?""", (chat_id, )).fetchone()
        user_def_count = cursor.execute("""SELECT * from users where chat_id = ?""", (chat_id,)).fetchall()[0][-1]
        if int(count[0]) < user_def_count:
            match = re.search('(?:((?:https?|s?ftp):)\/\/)([^:\/\s]+)(?::(\d*))?(?:\/([^\s?#]+)?([?][^?#]*)?(#.*)?)?', message.text)
            if match is not None:
                user_url = match.group(0)
                user_site, product_name = when_user_send_url(chat_id, driver, user_url)
            else:
                product_name = message.text
            data = cursor.execute(
                """SELECT * from products WHERE product_name = ? AND chat_id = ?""", (product_name, chat_id)).fetchall()
            if len(data) == 0:
                sql_update_query = """INSERT INTO products (product_name, chat_id, product_addtime, product_newtime, product_hash, send_message) VALUES (?, ?, ?, ?, ?, ?)"""
                product_addtime = product_newtime = now_date.strftime("%Y-%m-%d")
                product_hash = set_hash()
                send_message = "false"
                data = (product_name, chat_id, product_addtime, product_newtime, product_hash, send_message)
                cursor.execute(sql_update_query, data)

                old = min = max = 0
                change = check_status = "false"
                url = new = "null"
                sql_update_query = """INSERT INTO price (product_name, site, url, new, old, min, max, change, check_status, product_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

                arr = []
                sites = cursor.execute("""SELECT * FROM sites""").fetchall()
                for elements in sites:
                    arr = arr + [elements[1]]
                for element in arr:
                    site = f"{element}"
                    data = (product_name, site, url, new, old, min, max, change, check_status, product_hash)
                    cursor.execute(sql_update_query, data)
                if match is not None:
                    cursor.execute(f'UPDATE price set url = "{user_url}" WHERE product_hash = "{product_hash}" AND site = "{user_site}"')
                sqlite_connection.commit()
                cursor.close()

                bot.send_message(ADMIN_ID, f"Новый товар - {product_name} (@{user_name})")
                bot.send_message(chat_id, f"<code>{product_name}</code> - добавленo.\nВ ближайшее время бот подберет ссылки в соответствии с запросом и пришлет цены.\nНо если вы добавите ссылки на товар вручную - это исключит возможные ошибки (рекомендуется).")
            else:
                bot.send_message(chat_id, "Вы уже мониторите это")
        else:
            bot.send_message(chat_id, "Лимит мониторинга - 3 позиций")
    except Exception as e:
        bot.send_message(chat_id, "Что-то пошло не так... если товар не добавился - попробуйте указать наименование самостоятельно, если добавляли ссылку. Иначе - попробуйте позже.")
        bot.send_message(ADMIN_ID, "Что-то пошло не так... если товар не добавился - попробуйте указать наименование самостоятельно, если добавляли ссылку. Иначе - попробуйте позже.")
        logging.error(f"\nadd_new_product\ndef add_new_product(message, chat_id, user_name)\n{e}\n{traceback.format_exc()}\n\n")
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    driver.quit()


def set_hash():
    """создаем уникальный хэш продукта"""
    chars = '0123456789abcdefghjklmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(chars) for _ in range(8))


def when_user_send_url(chat_id, driver, user_url):
    from main import bot
    bot.send_message(chat_id, "Ожидайте...")
    driver.get(user_url)
    time.sleep(2)
    driver.refresh()
    time.sleep(5)
    start_time = time.time()
    if re.search(r'dns-shop.ru', user_url):
        for i in range(6):
            time.sleep(2)
            driver.refresh()
        with open('logs.txt', 'a', encoding="utf8") as file:
            file.write(f"{driver.page_source}\n")
        product_name = driver.page_source.split('Product","name":"')[1].split('"')[0]
        user_site = 'dns-shop.ru'
    elif re.search(r'mvideo.ru', user_url):
        product_name = driver.page_source.split('"name" class="title">')[1].split('<')[0]
        user_site = 'mvideo.ru'
    elif re.search(r'wildberries.ru', user_url):
        product_name = driver.page_source.split('goodsName}">')[1].split('<')[0]
        user_site = 'wildberries.ru'
    elif re.search(r'citilink.ru', user_url):
        product_name = driver.page_source.split('"name": "')[1].split('"')[0]
        user_site = 'citilink.ru'
    elif re.search(r'onlinetrade.ru', user_url):
        product_name = driver.page_source.split('h1 itemprop="name">')[1].split('<')[0]
        user_site = 'onlinetrade.ru'
    elif re.search(r'eldorado.ru', user_url):
        product_name = driver.page_source.split('title" content="')[1].split('"')[0]
        user_site = 'eldorado.ru'
    elif re.search(r'regard.ru', user_url):
        product_name = driver.page_source.split('"Product","name":"')[1].split('"')[0]
        user_site = 'regard.ru'
    elif re.search(r'ozon.ru', user_url):
        product_name = driver.page_source.split('"name":"')[1].split('"')[0]
        user_site = 'ozon.ru'
    elif re.search(r'detmir.ru', user_url):
        product_name = driver.page_source.split('"name":"')[1].split('"')[0]
        user_site = 'detmir.ru'
    else:
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
        bot.send_message(chat_id, message_if_wrong_site)
    return user_site, product_name
