#!/usr/bin/env python3
import os
import cv2
import numpy as np
from PIL import Image

# Тот же список расширений, что и для дедупликации
SUPPORTED_EXT = (
    '.jpg', '.jpeg', '.png', '.nef', '.raw', '.cr2', '.arw', '.dng',
    '.tif', '.tiff', '.bmp', '.gif', '.heic'
)

def detect_junk(path, blur_thresh=100.0, dark_thresh=50):
    """
    Сканирует папку и возвращает dict {путь: причина},
    где причина — 'blurry' (размытие) или 'dark' (тёмное).
    """
    junk = {}
    for root, _, files in os.walk(path):
        for fname in files:
            if fname.startswith('._'): # Игнорируем файлы метаданных macOS
                continue
            if fname.lower().endswith(SUPPORTED_EXT):
                full = os.path.join(root, fname)
                # читаем как grayscale через OpenCV
                img_data = np.fromfile(full, dtype=np.uint8)
                img = cv2.imdecode(img_data, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                # оценка резкости
                variance = cv2.Laplacian(img, cv2.CV_64F).var()
                # оценка яркости
                brightness = float(np.mean(img))
                if variance < blur_thresh:
                    junk[full] = 'blurry'
                elif brightness < dark_thresh:
                    junk[full] = 'dark'
    return junk 