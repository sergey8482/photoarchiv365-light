#!/usr/bin/env python3
from PIL import Image
import imagehash
import os, sys
import json

def scan_folder(path):
    groups = {}
    print(f"DEBUG: начинаем сканирование {path}")
    for root, _, files in os.walk(path):
        for fname in files:
            if fname.startswith('._'): # Игнорируем файлы метаданных macOS
                print(f"DEBUG: Игнорируем метафайл: {os.path.join(root, fname)}")
                continue
            if fname.lower().endswith(('.jpg','.jpeg','.png')):
                full = os.path.join(root, fname)
                print(f"DEBUG: найден файл {full}")
                try:
                    h = str(imagehash.average_hash(Image.open(full)))
                    groups.setdefault(h, []).append(full)
                except Exception as e:
                    print(f"DEBUG: ошибка при хэшировании {full}: {e}")
    return groups

def main(path):
    print(f"Scanning folder: {path}")
    groups = scan_folder(path)
    # Отфильтровать группы-одиночки
    dupe_groups = {h: fns for h, fns in groups.items() if len(fns) > 1}
    print(json.dumps(dupe_groups, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    main(folder) 