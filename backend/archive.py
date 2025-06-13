#!/usr/bin/env python3
import os
import time
import shutil
from PIL import Image, ExifTags

# все поддерживаемые расширения
SUPPORTED_EXT = (
    '.jpg', '.jpeg', '.png', '.nef', '.raw', '.cr2', '.arw', '.dng',
    '.tif', '.tiff', '.bmp', '.gif', '.heic'
)

# маппинг номера месяца → его название
MONTH_NAMES = {
    '01': 'Январь',   '02': 'Февраль', '03': 'Март',
    '04': 'Апрель',   '05': 'Май',     '06': 'Июнь',
    '07': 'Июль',     '08': 'Август',  '09': 'Сентябрь',
    '10': 'Октябрь',  '11': 'Ноябрь',  '12': 'Декабрь',
}

# Найти тег DateTimeOriginal в EXIF
def _get_exif_datetime(img):
    try:
        exif = img._getexif()
        if not exif:
            return None
        for tag, name in ExifTags.TAGS.items():
            if name == 'DateTimeOriginal':
                return exif.get(tag)
    except:
        pass
    return None

def get_photos_by_date(path):
    """Возвращает dict[year][month_num] = [файлы...]"""
    archive = {}
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXT):
                full = os.path.join(root, f)
                # EXIF → дата оригинала
                try:
                    dt = _get_exif_datetime(Image.open(full))
                except:
                    dt = None
                if dt:
                    date_part = dt.split(' ')[0]  # "YYYY:MM:DD"
                    year, month = date_part.split(':')[:2]
                else:
                    # fallback на время модификации файла
                    ts = os.path.getmtime(full)
                    lt = time.localtime(ts)
                    year, month = str(lt.tm_year), f"{lt.tm_mon:02d}"
                archive.setdefault(year, {}).setdefault(month, []).append(full)
    return archive

def organize_photos(path):
    """
    Создает папки path/Год/Месяц (название) и перемещает туда файлы.
    Возвращает структуру archive для отображения.
    """
    archive = get_photos_by_date(path)
    for year, months in archive.items():
        year_folder = os.path.join(path, year)
        os.makedirs(year_folder, exist_ok=True)
        for month_num, files in months.items():
            name = MONTH_NAMES.get(month_num, month_num)
            month_folder = os.path.join(year_folder, name)
            os.makedirs(month_folder, exist_ok=True)
            for src in files:
                dst = os.path.join(month_folder, os.path.basename(src))
                # если файл ещё не перемещён
                if os.path.abspath(src) != os.path.abspath(dst):
                    shutil.move(src, dst)
    return archive 