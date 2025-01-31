"""get sql base bac"""
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

import os
import shutil
from datetime import datetime, timedelta


def copy_with_date(source_folder: str, destination_folder: str) -> None:
    """
    Копирование папки с добавлением даты в название папки внутри папки с именем даты,
    если папка отсутствует.
    :param source_folder: Путь к копируемой папке.
    :param destination_folder: Путь к каталогу назначения.
    """
    current_date = datetime.today()
    date_folder_name = current_date.strftime("%d.%m.%Y")  # Создаем имя папки в формате "дд.мм.гггг"

    destination_folder = os.path.join(destination_folder, date_folder_name)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    time_suffix = current_date.strftime("%H_%M_%S")  # Создаем суффикс с текущим временем в формате "чч_мм_сс"
    new_folder_name = f"{date_folder_name}_{time_suffix}"
    new_full_folder_path = os.path.join(destination_folder, new_folder_name)

    # Копируем исходную папку в новую папку назначения
    shutil.copytree(source_folder, new_full_folder_path)

    # Удаляем папки, более старые, чем месяц
    month_ago = current_date - timedelta(days=30)
    for folder in os.listdir(destination_folder):
        folder_path = os.path.join(destination_folder, folder)
        if os.path.isdir(folder_path):
            # Извлекаем из имени папки дату создания и
            # проверяем, была ли папка создана раньше, чем месяц назад
            folder_date_str = folder.split("_")[0]
            folder_date = datetime.strptime(folder_date_str, "%d.%m.%Y")
            if folder_date < month_ago:
                # Удаляем папку со всем её содержимым
                shutil.rmtree(folder_path)
