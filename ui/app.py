import os, sys
import streamlit as st

# подключаем backend-пакеты
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.dedupe import find_duplicate_groups
from backend.archive import get_photos_by_date, organize_photos, MONTH_NAMES

st.set_page_config(page_title="Фотоархив365 Light")
st.title("Фотоархив365 Light")

# Инициализация состояния
if 'dupe' not in st.session_state:
    st.session_state.dupe = {}
if 'archive' not in st.session_state:
    st.session_state.archive = {}
if 'to_delete' not in st.session_state:
    st.session_state.to_delete = set()

folder_input = st.text_input("Путь к папке для сканирования", ".")
folder = folder_input.strip().strip('"').strip("'")

if st.button("Анализ"):
    # Преобразуем список кластеров в словарь для session_state
    raw_dupe_groups = find_duplicate_groups(folder, threshold=0)
    processed_dupe_groups = {}
    for cluster in raw_dupe_groups:
        if len(cluster) > 1: # Убедимся, что это группа дубликатов (больше 1 файла)
            representative_hash = str(cluster[0][1]) # Хеш первой картинки как ключ
            file_paths = [f for f, _ in cluster] # Список файлов в группе
            processed_dupe_groups[representative_hash] = file_paths

    st.session_state.dupe = processed_dupe_groups
    st.session_state.archive = get_photos_by_date(folder)
    st.session_state.to_delete.clear() # Очищаем выбранные для удаления файлы при новом анализе

# Секция дубликатов
if st.session_state.get('dupe'):
    st.header("Дубликаты")
    clusters = st.session_state.dupe
    st.write(f"Найдено {len(clusters)} групп дубликатов")
    for cluster_hash, cluster_files in clusters.items():
        st.write(f"### Группа: {cluster_hash}")
        cols = st.columns(2)
        for idx, path in enumerate(cluster_files):
            with cols[idx % 2]:
                st.image(path, width=200)
                name = os.path.basename(path)
                key = f"dup_del_{path}"
                if st.checkbox(f"Удалить {name}", key=key):
                    st.session_state.to_delete.add(path)
                else:
                    st.session_state.to_delete.discard(path)
    if st.session_state.to_delete and st.button("Применить удаление дубликатов"):
        removed = 0
        for f in list(st.session_state.to_delete):
            try:
                os.remove(f)
                removed += 1
            except Exception as e:
                st.error(f"Не удалось удалить {os.path.basename(f)}: {e}")
        st.success(f"Удалено {removed} файлов")
        st.session_state.dupe = {} # Очищаем дубликаты после удаления
        st.session_state.to_delete.clear()

# Секция архива по датам
if st.session_state.get('archive'):
    st.header("Архив по дате")
    if st.button("📁 Сгруппировать файлы по папкам", help="Создать папки Год/Месяц и переместить туда фото"):
        organize_photos(folder)
        st.success("Файлы перемещены в папки Год/Месяц")
    for year in sorted(st.session_state.archive.keys(), reverse=True):
        with st.expander(f"{year}"):
            for month_num in sorted(st.session_state.archive[year].keys()):
                month_name = MONTH_NAMES.get(month_num, month_num)
                st.subheader(month_name)
                photos = st.session_state.archive[year][month_num]
                cols = st.columns(4)
                for i, path in enumerate(photos):
                    with cols[i % 4]:
                        st.image(path, width=150)
                        st.caption(os.path.basename(path)) 