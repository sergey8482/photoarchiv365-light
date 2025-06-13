import os, sys
import PySimpleGUI as sg
from PIL import Image, ImageTk
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.dedupe import find_duplicate_groups
from backend.archive import get_photos_by_date, organize_photos, MONTH_NAMES

def resize_image(image_path, size=(300, 300)):
    """Resize image for preview"""
    try:
        img = Image.open(image_path)
        img.thumbnail(size)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        return bio.getvalue()
    except Exception as e:
        print(f"Error resizing {image_path}: {e}")
        return None

def create_duplicate_group(group_num, cluster):
    """Create layout for a group of duplicates"""
    layout = [
        [sg.Text(f"Дубликаты №{group_num} — {len(cluster)} фото", font=('Helvetica', 12, 'bold'))],
        [sg.Image(data=resize_image(cluster[0]), key=f'preview_{group_num}_0')],
    ]
    
    # Add smaller previews for duplicates
    if len(cluster) > 1:
        cols = []
        for i in range(len(cluster[1:])):
            cols.append([sg.Image(data=resize_image(cluster[i+1], (150, 150)), key=f'preview_{group_num}_{i+1}')])
        layout.append([sg.Column(cols, scrollable=True, horizontal_scroll=True)])
    
    # Add delete button
    layout.append([
        sg.Button(f"Удалить все дубликаты №{group_num}", key=f'delete_{group_num}')
    ])
    
    return layout

def main():
    sg.theme('LightBlue2')
    
    # Main layout
    layout = [
        [sg.Text("Фотоархив365 Light", font=('Helvetica', 16, 'bold'))],
        [sg.FolderBrowse("Выбрать папку", key='folder'), 
         sg.Text("", key='folder_display', size=(50, 1))],
        [sg.Button("🔍 Анализ", key='analyze')],
        [sg.Column([], key='results', scrollable=True, vertical_scroll_only=True)]
    ]
    
    window = sg.Window('Фотоархив365 Light', layout, resizable=True, finalize=True)
    
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            break
            
        if event == 'folder':
            window['folder_display'].update(values['folder'])
            
        if event == 'analyze':
            folder = values['folder']
            if not folder:
                sg.popup_error("Выберите папку для анализа")
                continue
                
            # Clear previous results
            window['results'].update([])
            
            # Find duplicates
            dupe_groups = find_duplicate_groups(folder, threshold=0)
            
            # Create layout for each group
            results_layout = []
            for i, cluster in enumerate(dupe_groups.values(), 1):
                results_layout.extend(create_duplicate_group(i, cluster))
                results_layout.append([sg.HorizontalSeparator()])
            
            window['results'].update(results_layout)
            
        # Handle delete buttons
        if event and event.startswith('delete_'):
            group_num = int(event.split('_')[1])
            cluster = list(dupe_groups.values())[group_num-1]
            
            if sg.popup_yes_no(f"Удалить все дубликаты группы №{group_num}?") == 'Yes':
                removed = 0
                for path in cluster[1:]:  # Skip first file (original)
                    try:
                        os.remove(path)
                        removed += 1
                    except Exception as e:
                        sg.popup_error(f"Ошибка при удалении {path}: {e}")
                
                if removed > 0:
                    sg.popup_ok(f"Удалено {removed} файлов")
                    # Refresh the window
                    window['analyze'].click()
    
    window.close()

if __name__ == '__main__':
    main() 