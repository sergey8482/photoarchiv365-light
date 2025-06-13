import streamlit as st
import os
from backend.dedupe import scan_folder

st.set_page_config(page_title="Фотоархив365 Light")
st.title("Фотоархив365 Light")

folder = st.text_input("Путь к папке для сканирования", ".")

if st.button("Анализ"):
    with st.spinner(f"Сканируем {folder}..."):
        groups = scan_folder(folder)
        dupe_groups = {h: fns for h, fns in groups.items() if len(fns) > 1}
    st.success(f"Найдено {len(dupe_groups)} групп дубликатов")
    to_delete = []
    for h, files in dupe_groups.items():
        st.write(f"### Группа: {h}")
        cols = st.columns(2)
        for idx, filepath in enumerate(files):
            with cols[idx % 2]:
                st.image(filepath, width=200, caption=os.path.basename(filepath))
                if st.checkbox(f"Удалить {os.path.basename(filepath)}", key=f"{h}_{idx}"):
                    to_delete.append(filepath)
    if to_delete:
        if st.button("Применить удаление"):
            for f in to_delete:
                os.remove(f)
            st.success(f"Удалено {len(to_delete)} файлов")