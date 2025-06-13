#!/usr/bin/env python3
import os
import json
from PIL import Image
import imagehash

def find_duplicate_groups(path, threshold=0):
    # Собираем список (путь, hash)
    file_hashes = []
    print(f"DEBUG: начинаем сканирование {path}")
    for root, _, files in os.walk(path):
        for fname in files:
            if fname.startswith('._'): # Игнорируем файлы метаданных macOS
                print(f"DEBUG: Игнорируем метафайл: {os.path.join(root, fname)}")
                continue
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.nef')):
                full = os.path.join(root, fname)
                print(f"DEBUG: найден файл {full}")
                try:
                    h = imagehash.average_hash(Image.open(full))
                    print(f"DEBUG: Хеш для {full}: {h}") # Добавлено отладочное сообщение для хеша
                    file_hashes.append((full, h))
                except Exception as e:
                    print(f"DEBUG: ошибка при хэшировании {full}: {e}") # Подробное логирование ошибок

    groups = []
    visited = set()
    # Простая кластеризация: объединяем файлы с расстоянием <= threshold
    for i, (f1, h1) in enumerate(file_hashes):
        if f1 in visited:
            continue
        cluster = [(f1, h1)]
        visited.add(f1)
        for f2, h2 in file_hashes[i+1:]:
            if f2 not in visited and (h1 - h2) <= threshold:
                cluster.append((f2, h2))
                visited.add(f2)
        if len(cluster) > 1:
            groups.append(cluster)
    return groups

def main(path):
    print(f"Scanning folder: {path}")
    clusters = find_duplicate_groups(path, threshold=0)
    # Преобразуем в JSON: ключ — строковое представление хэша первой картинки
    result = {}
    for cluster in clusters:
        rep_hash = str(cluster[0][1])
        files = [f for f, _ in cluster]
        result[rep_hash] = files
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    main(folder) 