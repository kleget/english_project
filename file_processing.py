import pdfminer.high_level
import os


def pdf_to_txt(root, name_file):  # конвертируем pdf в txt и по факту копируем /pdf в /txt только с новыми файлами
    with open(f'{root}/{name_file}', 'rb') as file:
        root = root.replace('/pdf/', '/txt/')
        name_file = name_file.split('.')[0]
        if not os.path.exists(f'{root}/{name_file}.txt'):
            os.makedirs(root, exist_ok=True)  # создаем директорию root, чтобы по сути скопировать структуру из pdf в txt
            file1 = open(fr'{root}/{name_file}.txt', 'a+', encoding='UTF-8')  # даже если файл с таким названием уже есть, мы просто ДОзапишем в него информацию в конец
            pdfminer.high_level.extract_text_to_fp(file, file1)
            file1.close()


def rename_files_in_directory(directory):  # удаляем весь мусор из названия файла
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if ('.' in filename) and (filename.count('.') > 1):
                new_filename = filename.replace('.', '_').replace(' ', '_').replace(',', '_')
                new_filename = new_filename.replace('_pdf', '.pdf')
                old_file = os.path.join(root, filename)
                new_file = os.path.join(root, new_filename).replace('\\', '/')
                if not os.path.exists(new_file):
                    os.rename(old_file, new_file)


def get_directory_structure(rootdir):  # получаем всю структуру rootdir в виде словаря
    structure = {}
    for item in os.listdir(rootdir):
        path = os.path.join(rootdir, item)
        if os.path.isdir(path):
            # Если это папка, рекурсивно получаем её структуру
            structure[item] = get_directory_structure(path)
        else:
            # Если это файл, добавляем его в список
            if 'files' not in structure:
                structure['files'] = []
            structure['files'].append(item)
    return structure


def get_all_folders(structure, current_path=""):  # нужно для навигации по structure возвращаемой get_directory_structure
    folders = []
    for key, value in structure.items():
        if key != 'files':  # Игнорируем ключ 'files'
            folder_path = os.path.join(current_path, key).replace('\\', '/')
            folders.append(folder_path)
            if isinstance(value, dict):  # Если это вложенная папка
                folders.extend(get_all_folders(value, folder_path))
    return folders

