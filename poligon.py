# этот файл я использую как испытатьельный полигон для проверки и отладки


# def get_directory_structure(rootdir):
#     structure = {}
#     for item in os.listdir(rootdir):
#         path = os.path.join(rootdir, item)
#         if os.path.isdir(path):
#             # Если это папка, рекурсивно получаем её структуру
#             structure[item] = get_directory_structure(path)
#         else:
#             # Если это файл, добавляем его в список
#             if 'files' not in structure:
#                 structure['files'] = []
#             structure['files'].append(item)
#     return structure
#
#
# def get_all_folders(structure, current_path=""):  # нужно для навигации по папке
#     folders = []
#     for key, value in structure.items():
#         if key != 'files':  # Игнорируем ключ 'files'
#             folder_path = os.path.join(current_path, key)
#             folders.append(folder_path)
#             if isinstance(value, dict):  # Если это вложенная папка
#                 folders.extend(get_all_folders(value, folder_path))
#     return folders
#
#
# # def get_all_files(structure, current_path=""):  # нужно для получения всех файлов structure
# #     files = []
# #     for key, value in structure.items():
# #         if key == 'files':  # Если это список файлов
# #             for file in value:
# #                 files.append(os.path.join(current_path, file))
# #         elif isinstance(value, dict):  # Если это вложенная папка
# #             folder_path = os.path.join(current_path, key)
# #             files.extend(get_all_files(value, folder_path))
# #     return files
#
# directory_structure = get_directory_structure(rootdir)
# # all_files = get_all_files(directory_structure)
# all_folders = get_all_folders(directory_structure)
#
#
# print(directory_structure)
# # print(all_folders)
# # print(all_files)

from file_processing import get_directory_structure, get_all_folders
from text_analysis import analysand_func_dict
from config import *
import sqlite3 as sq
import re
import os
from database_operations import *

# в get_txt_file нужно передавать название файла в месте папкой типа code/book.txt, а не просто book.txt
def print_all_files_from_rootdir():
    structure = get_directory_structure(rootdir)
    all_folders = get_all_folders(structure)

    list_all_files_from_rootdir = []

    for x in all_folders:  # работает только для вложенности 2: pdf/basic
        if '/' in x:
            x = x.split('/')
            list_all_files_from_rootdir.append([f"{x[1]}/{i}" for i in structure[x[0]][x[1]]['files']])
    return list_all_files_from_rootdir


list_all_files = print_all_files_from_rootdir()

def reqursion(x):
    math_word = {} # это все слова из всех файлов, не по отдельности, а именно все вообще математические слов
    # basik_words = {}
    '''это просто все слова, обычные, по хорошему они должны быть статические и в БД, а не каждый раз собирать их из множества книг'''

    for y in x:
        if type(y) == list:
            reqursion(y)
        else:
            if '.txt' in y:
                x_y = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ/]', '', y.split('.')[0], flags=re.IGNORECASE)

                create_table(*x_y.split('/'))

                A = analysand_func_dict(y.replace('.txt', ''))  # получаем массив НЕ отсортированных готовых данных из книги
                B = select_from_table(x_y.split('/')[0], f"SELECT word FROM {x_y.split('/')[1]}")  # B - это обычные слова, А - это специальные слова
                # B = ['привет', 'вода', 'лампа', 'кошка']
                for x in A:  # тут мы проверяем, чтобы в math_word попали только те слова, которых нет в обычной книге
                    if (x not in B) and (x != '') and (x != "''"):
                        math_word[x] = A[x]
                sorted_analysand = sorted(math_word.items(), key=lambda item: item[1], reverse=True)
                sorted_analysand = [list(item) for item in sorted_analysand] # из хуйни в список списков
                # for i in sorted_analysand:
                insert_many_into_table(*x_y.split('/'), sorted_analysand)


reqursion(list_all_files)
