import os, sys
import streamlit as st

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.dedupe import find_duplicate_groups
from backend.junk import detect_junk

st.set_page_config(page_title="Фотоархив365 Light")
st.title("Фотоархив365 Light")

# Ввод папки
folder_input = st.text_input("Путь к папке для сканирования", ".")
folder = folder_input.strip().strip('"').strip("'")

# Инициализация состояния
if 'dupe_groups' not in st.session_state:
    st.session_state.dupe_groups = {}
if 'to_delete' not in st.session_state:
    st.session_state.to_delete = set()

# Кнопка анализа
if st.button("Анализ"):
    st.session_state.dupe = find_duplicate_groups(folder, threshold=0)
    st.session_state.junk = detect_junk(folder)

tabs = st.tabs(["Дубликаты", "Мусор"])
with tabs[0]:
    dupe = st.session_state.get('dupe', {})
    st.write(f"Найдено {len(dupe)} групп дубликатов")
    for cluster in dupe.values():
        cols = st.columns(2)
        for idx, path in enumerate(cluster):
            with cols[idx % 2]:
                st.image(path, width=200)
                st.write(os.path.basename(path))
with tabs[1]:
    junk = st.session_state.get('junk', {})
    st.write(f"Найдено {len(junk)} мусорных фото")
    for path, reason in junk.items():
        st.image(path, width=150)
        st.write(f"{os.path.basename(path)} ({reason})")

# Если есть результаты — показываем их
if st.session_state.dupe_groups:
    dupe = st.session_state.dupe_groups
    st.success(f"Найдено {len(dupe)} групп дубликатов")
    for h, files in dupe.items():
        st.write(f"### Группа: {h}")
        cols = st.columns(2)
        for idx, path in enumerate(files):
            with cols[idx % 2]:
                st.image(path, width=200, caption=os.path.basename(path))
                key = f"del_{h}_{idx}"
                checked = st.checkbox(f"Удалить {os.path.basename(path)}", key=key)
                if checked:
                    st.session_state.to_delete.add(path)
                else:
                    st.session_state.to_delete.discard(path)
    # Кнопка удаления
    if st.session_state.to_delete and st.button("Применить удаление"):
        removed = 0
        for f in list(st.session_state.to_delete):
            try:
                os.remove(f)
                removed += 1
            except Exception as e:
                st.error(f"Ошибка удаления {f}: {e}")
        st.success(f"Удалено {removed} файлов")
        # Сброс состояния после удаления
        st.session_state.dupe_groups.clear()
        st.session_state.to_delete.clear() 