"""Клавиатуры"""
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

from telebot import types
from main import bot

def first_keyboard(message: types.Message):
    """запуск стартовой клавиатуры"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(("\U0001F4CA Добавить товар"), ('\U0001F4C3 Мой список'))
    keyboard.add(('\U0001F504 Редактировать ссылки'), ('\u274C Удалить товар'))
    keyboard.add('\u25B6 Дальше')
    bot.send_message(message.chat.id, "...", reply_markup=keyboard)


def second_keyboard(message: types.Message):
    """запуск второй клавиатуры"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(("\U0001F4E7 Написать разработчику"), ('\u0024 Поблагодарить разработчика'))
    keyboard.add('\u2049 Вопросы и ответы')
    keyboard.add('\u25C0 Назад')
    bot.send_message(message.chat.id, "...", reply_markup=keyboard)

def add_product_keyboard(message: types.Message):
    """запуск кнопки добавления товара"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add('\u25C0 Назад')
    bot.send_message(message.chat.id, "Пришлите наименование товара или ссылку на товар (каждый товар необходимо добавлять отдельно друг от друга, если это ссылка - то кроме нее ничего дописывать не надо).\nЕсли передумали - нажмите <code>Назад</code>", reply_markup=keyboard)

def edit_product_urls_keyboard(message: types.Message):
    """запуск кнопки редактирования ссылок"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add('\u25C0 Назад')
    bot.send_message(message.chat.id, "Для какой позиции менять ссылки?\nЕсли передумали - нажмите <code>Назад</code>", reply_markup=keyboard)

def remove_product_keyboard(message: types.Message):
    """запуск кнопки удаление товаров"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add('\u25C0 Назад')
    bot.send_message(message.chat.id, "Что удалить?\nЕсли передумали или закончили - нажмите <code>Назад</code>", reply_markup=keyboard)

def message_to_admin_keyboard(message: types.Message):
    """запуск кнопки написать сообщение админу"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add('\u25C0 Назад')
    bot.send_message(message.chat.id, "Напишите желаемое сообщение.\nЕсли передумали - нажмите <code>Назад</code>", reply_markup=keyboard)
