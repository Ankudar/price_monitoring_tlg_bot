"""work_with_users_message"""
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
import change_user_status
import delete_product
import traceback
from welcome import WELCOME_TEXT
from work_with_txt import write_to_logs
from config import ADMIN_ID
from logger_config import logging

def register_commands_from_work_with_users_message(bot):
    """проброс bot в модуль из main"""
    import keyboard
    import send_products_list
    import work_with_sqlite
    import work_with_product_plots

    @bot.message_handler(commands=['start', 'help'])
    def start_help(message):
        """обработчик start и help"""
        chat_id = message.chat.id
        user_name = message.chat.username
        bot.send_chat_action(chat_id, 'typing')
        bot.send_message(chat_id, WELCOME_TEXT)
        keyboard.first_keyboard(message)
        work_with_sqlite.sql_set_tables_users_default(chat_id, user_name)
        write_to_logs(message)

    @bot.message_handler(regexp='Дальше')
    def next_button(message):
        """обработчик кнопки дальше"""
        # if message.from_user.id == ADMIN_ID:
        keyboard.second_keyboard(message)
        # else:
            # bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Добавить товар')
    def add_product(message):
        """обработчик кнопки Добавить товар"""
        # if message.from_user.id == ADMIN_ID:
        chat_id = message.chat.id
        user_name = message.chat.username
        keyboard.add_product_keyboard(message)
        work_with_sqlite.sql_set_tables_users_default(chat_id, user_name)
        change_user_status.set_user_status(message, "addproduct")
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Мой список')
    def users_product_list(message):
        """обработчик кнопки Мой список"""
        chat_id = message.chat.id
        # if message.from_user.id == ADMIN_ID:
        send_products_list.send_list(chat_id, message)
        keyboard.first_keyboard(message)
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Редактировать ссылки')
    def edit_product_urls(message):
        """обработчик кнопки Редактировать ссылки"""
        chat_id = message.chat.id
        # if message.from_user.id == ADMIN_ID:
        keyboard.edit_product_urls_keyboard(message)
        send_products_list.send_list(chat_id, message)
        change_user_status.set_user_status(message, "editurls")
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Удалить товар')
    def remove_product(message):
        """обработчик кнопки Удалить товар"""
        chat_id = message.chat.id
        # if message.from_user.id == ADMIN_ID:
        keyboard.remove_product_keyboard(message)
        send_products_list.send_list(chat_id, message)
        change_user_status.set_user_status(message, "deleteproduct")
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Написать разработчику')
    def message_to_admin(message):
        """обработчик кнопки Написать разработчику"""
        # if message.from_user.id == ADMIN_ID:
        chat_id = message.chat.id
        user_name = message.chat.username
        keyboard.message_to_admin_keyboard(message)
        change_user_status.set_user_status(message, "sendadminmessage")
        work_with_sqlite.sql_set_tables_users_default(chat_id, user_name)
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Назад')
    def back_button(message):
        """обработчик кнопки Добавить товар"""
        # if message.from_user.id == ADMIN_ID:
        keyboard.first_keyboard(message)
        change_user_status.set_user_status(message, "nothing")
        change_user_status.set_user_editurlhash("nothing", message.from_user.id)
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Поблагодарить разработчика')
    def donation(message):
        """обработчик кнопки Поблагодарить разработчика"""
        # if message.from_user.id == ADMIN_ID:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Поблагодарить разработчика, если вам нравится бот, можно перейдя по <a href=\"https://www.donationalerts.com/r/ankudar\">ссылке</a>")
        keyboard.second_keyboard(message)
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.message_handler(regexp='Вопросы и ответы')
    def faq(message):
        """обработчик кнопки FAQ"""
        # if message.from_user.id == ADMIN_ID:
        chat_id = message.chat.id
        bot.send_message(chat_id, WELCOME_TEXT)
        keyboard.second_keyboard(message)
        # else:
        #     bot.reply_to(message, "Не сегодня...")
        write_to_logs(message)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        chat_id = call.message.chat.id
        user_name = call.from_user.username
        len_call = len(str(call.data).split(" "))
        if len_call == 1:
            product_hash = str(call.data)
        elif len_call == 2:
            product_hash = str(call.data).split(" ")[1]
        inline_status = str(call.data).split(" ")[0]
        change_user_status.set_user_editurlhash(product_hash, chat_id)
        sqlite_connection = sql.connect('sqlite_price_info.db')
        cursor = sqlite_connection.cursor()
        try:
            workstatus = cursor.execute("""SELECT * FROM users WHERE chat_id = ?""", (chat_id, )).fetchall()[0][3]
            product_name = cursor.execute("""SELECT * FROM products WHERE product_hash = ?""", (product_hash, )).fetchall()[0][1]
            if workstatus == "editurls":
                bot.send_message(chat_id, "Пришлите ссылку, которую бы вы хотели установить самостоятельно\nЕсли передумали или закончили - нажмите <code>Назад</code>\nДо момента пока не нажмете <code>Назад</code> бот будет работать с ссылками для этого товара")
            elif workstatus == "deleteproduct":
                delete_product.delete_product(product_name, chat_id, user_name, product_hash)
                send_products_list.send_list(chat_id, call.message)
            elif inline_status == "plot":
                work_with_product_plots.send_plots(product_name, chat_id, product_hash)
            elif inline_status == "delete":
                delete_product.delete_product(product_name, chat_id, user_name, product_hash)
            elif (workstatus == "nothing" and product_hash != "nothing"):
                send_products_list.send_price_info(product_name, chat_id, product_hash)
        except Exception as e:
            logging.error(f"\nwork_with_users_message\ndef callback_inline(call)\n{e}\n{traceback.format_exc()}\n\n")
