import os, sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.dedupe import find_duplicate_groups
from backend.archive import get_photos_by_date, organize_photos, MONTH_NAMES

st.set_page_config(page_title="Фотоархив365 Light")
st.title("Фотоархив365 Light")

# Инициализация текущей папки
if 'folder' not in st.session_state:
    st.session_state.folder = os.getcwd()

# Панель выбора папки (интерактивный браузер)
st.sidebar.header("Навигация по папкам")
current = st.sidebar.text_input("Текущая папка", st.session_state.folder)
st.sidebar.write("Подпапки:")
try:
    subdirs = [d for d in os.listdir(current) if os.path.isdir(os.path.join(current, d))]
except Exception:
    subdirs = []
choice = st.sidebar.selectbox("Перейти в", [".."] + subdirs)
if st.sidebar.button("Жми перейти"):
    if choice == "..":
        new_folder = os.path.dirname(current)
    else:
        new_folder = os.path.join(current, choice)
    st.session_state.folder = new_folder

st.sidebar.write(f"**Выбрано:** {st.session_state.folder}")

# Основная кнопка анализа
if st.button("🔍 Анализ"):
    folder = st.session_state.folder
    st.session_state.dupe = find_duplicate_groups(folder, threshold=0)
    st.session_state.archive = get_photos_by_date(folder)
    st.session_state.to_delete = set()

# Раздел «Дубликаты»
if st.session_state.get('dupe'):
    st.header("Дубликаты")
    for i, cluster in enumerate(st.session_state.dupe.values(), start=1):
        with st.expander(f"Дубликаты №{i} — {len(cluster)} фото", expanded=False):
            st.image(cluster[0], width=300, caption=os.path.basename(cluster[0]))
            rest = cluster[1:]
            if rest:
                cols = st.columns(len(rest))
                for idx, path in enumerate(rest):
                    with cols[idx]:
                        st.image(path, width=150, caption=os.path.basename(path))
            if st.button(f"Удалить все дубликаты №{i}", key=f"del_all_{i}"):
                removed = 0
                for p in rest:
                    os.remove(p)
                    removed += 1
                st.success(f"Удалено {removed} файлов")
                # обновляем state
                key = list(st.session_state.dupe.keys())[i-1]
                st.session_state.dupe.pop(key)

# Раздел «Архив по дате»
if st.session_state.get('archive'):
    st.header("Архив по дате")
    if st.button("📁 Сгруппировать файлы по папкам"):
        organize_photos(st.session_state.folder)
        st.success("Файлы перемещены в папки Год/Месяц")
    for year in sorted(st.session_state.archive.keys(), reverse=True):
        with st.expander(f"{year}", expanded=False):
            for month_num in sorted(st.session_state.archive[year].keys()):
                month_name = MONTH_NAMES.get(month_num, month_num)
                st.subheader(month_name)
                photos = st.session_state.archive[year][month_num]
                cols = st.columns(4)
                for j, path in enumerate(photos):
                    with cols[j % 4]:
                        st.image(path, width=150)
                        st.caption(os.path.basename(path)) 