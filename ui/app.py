import os, sys
import streamlit as st

# подключаем backend-пакеты
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.dedupe import find_duplicate_groups
from backend.archive import get_photos_by_date

st.set_page_config(page_title="Фотоархив365 Light")
st.title("Фотоархив365 Light")

folder_input = st.text_input("Путь к папке для сканирования", ".")
folder = folder_input.strip().strip('"').strip("'")

if st.button("Анализ"):
    st.session_state.dupe = find_duplicate_groups(folder, threshold=0)
    st.session_state.archive = get_photos_by_date(folder)
    st.session_state.to_delete = set()

# Секция дубликатов
if st.session_state.get('dupe'):
    st.header("Дубликаты")
    clusters = st.session_state.dupe
    st.write(f"Найдено {len(clusters)} групп дубликатов")
    for cluster in clusters.values():
        cols = st.columns(2)
        for idx, path in enumerate(cluster):
            with cols[idx % 2]:
                st.image(path, width=200)
                name = os.path.basename(path)
                key = f"dup_del_{path}"
                if st.checkbox(f"Удалить {name}", key=key):
                    st.session_state.to_delete.add(path)
    if st.session_state.to_delete and st.button("Применить удаление дубликатов"):
        removed = 0
        for f in list(st.session_state.to_delete):
            try:
                os.remove(f)
                removed += 1
            except Exception as e:
                st.error(f"Не удалось удалить {os.path.basename(f)}: {e}")
        st.success(f"Удалено {removed} файлов")
        st.session_state.dupe = {}

# Секция архива по датам
if st.session_state.get('archive'):
    st.header("Архив по дате")
    archive = st.session_state.archive
    for year in sorted(archive.keys(), reverse=True):
        st.subheader(year)
        for month in sorted(archive[year].keys()):
            st.write(f"**Месяц {month}**")
            photos = archive[year][month]
            cols = st.columns(4)
            for i, path in enumerate(photos):
                with cols[i % 4]:
                    st.image(path, width=150)
                    st.caption(os.path.basename(path)) 