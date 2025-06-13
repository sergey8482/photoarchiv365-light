#!/usr/bin/env python3
import os
import time
from PIL import Image, ExifTags

# Расширения те же, что в dedupe.py
SUPPORTED_EXT = (
    '.jpg', '.jpeg', '.png', '.nef', '.raw', '.cr2', '.arw', '.dng',
    '.tif', '.tiff', '.bmp', '.gif', '.heic'
)

# Найти тег DateTimeOriginal в EXIF
def _get_exif_datetime(img):
    try:
        exif = img._getexif()
        if not exif:
            return None
        for k, v in ExifTags.TAGS.items():
            if v == 'DateTimeOriginal':
                return exif.get(k)
    except:
        pass
    return None

def get_photos_by_date(path):
    archive = {}
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXT):
                full = os.path.join(root, f)
                # пытаемся взять из EXIF
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