"""work_with_txt"""
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

import datetime

def write_to_logs(message):
    """запись в лог файл"""
    now_date = datetime.datetime.now()
    with open('logs.txt', 'a', encoding="utf8") as file:
        file.write(f"{now_date:%d-%m-%Y %H:%M:%S} | {message.chat.id}({message.chat.type}, {message.chat.username}) | {message.text}\n")
