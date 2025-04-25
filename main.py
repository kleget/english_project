from io import BytesIO
from pdfreader import PDFDocument, SimplePDFViewer
from database_operations import *
from file_processing import *
from text_analysis import *
import os
import time
from config import *
import Levenshtein
from collections import defaultdict
    


# начальное время
start_time = time.time()

def print_all_files_from_rootdir():
    structure = get_directory_structure(rootdir)
    all_folders = get_all_folders(structure)

    list_all_files_from_rootdir = []

    for folder in all_folders:  # работает только для вложенности 2: pdf/basic
        if '/' in folder:
            folder = folder.split('/')
            list_all_files_from_rootdir.append([f"{folder[1]}/{i}" for i in structure[folder[0]][folder[1]]['files']])
    return list_all_files_from_rootdir


def reqursion(all_files_from_rootdir):
    math_word = {} # это все слова из всех файлов, не по отдельности, а именно все вообще математические слов
    # basik_words = {}
    '''это просто все слова, обычные, по хорошему они должны быть статические и в БД, а не каждый раз собирать их из множества книг'''

    for y in all_files_from_rootdir:
        if type(y) == list:
            reqursion(y)
        else:
            if '.txt' in y:
                clear_book_name = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ/]', '', y.split('.')[0], flags=re.IGNORECASE)
                A = analysand_func_dict(y.replace('.txt', ''))  # получаем массив НЕ отсортированных готовых данных из книги
                # B = select_from_table(clear_book_name.split('/')[0], f"SELECT word FROM {clear_book_name.split('/')[1]}")  # B - это обычные слова, А - это специальные слова
                B = ['']
                for all_files_from_rootdir in A:  # тут мы проверяем, чтобы в math_word попали только те слова, которых нет в обычной книге
                    if (all_files_from_rootdir not in B) and (all_files_from_rootdir != '') and (all_files_from_rootdir != "''"):
                        math_word[all_files_from_rootdir] = A[all_files_from_rootdir]

                sorted_analysand = sorted(math_word.items(), key=lambda item: item[1], reverse=True)
                sorted_analysand, list_del = algo_cleaner(sorted_analysand)

                print('Book: ', y, "Count: ", len(sorted_analysand), 'del: ', len(list_del))
                insert_many_into_table('delete', 'from_all_files', list_del)
                insert_many_into_table(*clear_book_name.split('/'), sorted_analysand) # тут записываем окончательный набор данных в БД



def algo_DSU(sorted_analysand, length_groups):
    print("Optimized algo_DSU")
    n = len(sorted_analysand)
    parent = list(range(n))
    rank = [1]*n
    processed = set()
    
    # Быстрый поиск с path compression
    find = lambda u: u if parent[u] == u else find(parent[u])
    
    # Оптимизированная функция объединения
    def union(u, v):
        u_root = find(u)
        v_root = find(v)
        if u_root == v_root: return
        if rank[u_root] < rank[v_root]:
            parent[u_root] = v_root
        else:
            parent[v_root] = u_root
            if rank[u_root] == rank[v_root]: 
                rank[u_root] += 1

    # Кэш для расстояний
    distance_cache = {}
    
    # Предварительная фильтрация и группировка
    filtered_groups = {}
    for l in length_groups:
        filtered_groups[l] = [idx for idx in length_groups[l] 
            if len(sorted_analysand[idx][0]) >= MIN_WORD_LENGTH]

    # Основной цикл с оптимизациями
    for l in filtered_groups:
        group = filtered_groups[l]
        group_size = len(group)
        
        for i in range(group_size):
            idx1 = group[i]
            s1 = sorted_analysand[idx1][0]
            s1_prefix = s1[:3]
            s1_len = len(s1)
            
            # Ограничение на количество сравнений
            for j in range(i+1, min(i+50, group_size)):  # MAX_NEIGHBORS=50
                idx2 = group[j]
                if (idx1, idx2) in processed: continue
                
                s2 = sorted_analysand[idx2][0]
                if abs(s1_len - len(s2)) > 1: continue
                if s1_prefix != s2[:3]: continue
                
                # Кэширование расстояний
                cache_key = (s1, s2) if s1 < s2 else (s2, s1)
                if cache_key not in distance_cache:
                    distance_cache[cache_key] = Levenshtein.distance(s1, s2)
                
                if distance_cache[cache_key] <= 1:
                    union(idx1, idx2)
                    processed.add((idx1, idx2))

    print('Finish optimized algo_DSU')
    return parent, rank

def algo_cleaner(sorted_analysand):
    print("algo_cleaner")

    def find_dsu(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union_by_rank_DSU(u, v):
        root_u = find_dsu(u)
        root_v = find_dsu(v)
        if root_u != root_v:
            if rank[root_u] > rank[root_v]:
                parent[root_v] = root_u
            else:
                parent[root_u] = root_v
                if rank[root_u] == rank[root_v]:
                    rank[root_v] += 1


    # Группировка по длине
    length_groups = defaultdict(list)
    for idx, item in enumerate(sorted_analysand):
        s = item[0]
        if len(s) >= 4:
            length_groups[len(s)].append(idx)

    # Вызов DSU
    parent, rank = algo_DSU(sorted_analysand, length_groups)

    # Дополнительная обработка через префиксы
    prefix_groups = defaultdict(list)
    for idx, item in enumerate(sorted_analysand):
        word = item[0]
        if len(word) >= MIN_WORD_LENGTH:
            prefix = word[:PREFIX_LENGTH] if len(word) >= PREFIX_LENGTH else word
            key = (len(word), prefix)
            prefix_groups[key].append(idx)

    # Оптимизированное сравнение пар
    processed_pairs = set()
    for (length, prefix), group in prefix_groups.items():
        group_size = len(group)
        for i in range(group_size):
            idx1 = group[i]
            s1 = sorted_analysand[idx1][0]
            
            for j in range(i+1, min(i+MAX_GROUP_SIZE, group_size)):
                idx2 = group[j]
                
                if (idx1, idx2) in processed_pairs:
                    continue
                processed_pairs.add((idx1, idx2))
                
                s2 = sorted_analysand[idx2][0]
                
                if abs(len(s1) - len(s2)) > 2:
                    continue
                
                if Levenshtein.distance(s1, s2) <= 2:
                    # Используем union_by_rank из DSU
                    union_by_rank_DSU(idx1, idx2)  # Если вынесены в класс

    print("Формирование результата и списка удаленных элементов")
    # Формирование результата и списка удаленных элементов
    groups = defaultdict(list)
    list_del = []

    for idx in range(len(sorted_analysand)):
        groups[find_dsu(idx)].append(idx)

    result = []
    for group in groups.values():
        if not group:
            continue

        main_idx = group[0]
        main_item = sorted_analysand[main_idx]

        # Добавляем информацию об удаленных элементах
        for del_idx in group[1:]:
            del_item = sorted_analysand[del_idx]
            list_del.append([
                del_item[0],
                str(del_item[1]),  # Сохраняем оригинальный строковый формат
                main_item[0]
            ])

        # Суммируем значения и возвращаем строковый формат
        total = sum(sorted_analysand[idx][1] for idx in group) # cколько раз замержили, окажется в колонке count в DB
        result.append([main_item[0], str(total)])

    print('finish ')
    return result, list_del


def main(rootdir):
    # тут мы просто делаем все имена книг чистыми без мусора(пробегается только по /pdf/)
    rename_files_in_directory(rootdir)

    # перебираем все дерево файлов rootdir и все файлы .pdf конвертируем в .txt с помощью pdf_to_txt()
    for root, dirs, files in os.walk(rootdir):
        if files:  # Если в папке есть файлы
            root = root.replace('\\', '/')# Выводим путь к папке
            print(root)  # ну это своеобразный индикатор, того, какую папку мы проходим и какие файлы обрабатываем сейчас.

            for file in files:
                if '/txt/' not in root:
                    pdf_to_txt(root, file)

    reqursion(print_all_files_from_rootdir())


if __name__ == "__main__":
    main(rootdir)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Все выполнилось за: ', elapsed_time, 'секунд')