import os
import subprocess

def pdf_to_txt(root, name_file):
    # root = root.replace('/pdf/', '/txt/')
    name_file = name_file.split('.')[0]
    # print(f"pdftotext: {root}/{name_file}.txt")
    if not os.path.exists(f"{root.replace('/pdf/', '/txt/')}/{name_file}.txt"):
        os.makedirs(root.replace('/pdf/', '/txt/'), exist_ok=True)
        subprocess.run(["pdftotext", "-layout", "-nopgbrk", f"{root.replace('/txt/', '/pdf/')}/{name_file}.pdf", f"{root.replace('/pdf/', '/txt/')}/{name_file}.txt", '-q'], check=True)


def rename_files_in_directory(directory):  # удаляем весь мусор из названия файла
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if ('.' in filename) and (filename.count('.') > 1):
                new_filename = filename.replace('.', '_').replace(' ', '_').replace(',', '_').replace('__', '_').replace('___', '_').replace('[', '_').replace(']', '_')
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
            # Если это папка, то рекурсивно получаем её структуру
            structure[item] = get_directory_structure(path)
        else:
            # Если это файл, то добавляем его в список
            if 'files' not in structure:
                structure['files'] = []
            structure['files'].append(item)
    return structure


def get_all_folders(structure, current_path=""):  # нужно для навигации по structure возвращаемой get_directory_structure
    # получаем все папки из structure в виде списка
    # пример: ['pdf', 'pdf/math', 'pdf/basic', 'pdf/code', 'txt', 'txt/math', 'txt/basic', 'txt/code']
    folders = []
    for key, value in structure.items():
        if key != 'files':  # Игнорируем ключ 'files'
            folder_path = os.path.join(current_path, key).replace('\\', '/')
            folders.append(folder_path)
            if isinstance(value, dict):  # Если это вложенная папка
                folders.extend(get_all_folders(value, folder_path))
    return folders

