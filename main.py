from io import BytesIO
from pdfreader import PDFDocument, SimplePDFViewer
from database_operations import *
from file_processing import *
from text_analysis import *
import os
import re
import time
from config import *
import Levenshtein
from collections import defaultdict
from database_aggregation import*
from colorama import init
from termcolor import colored

# начальное время
start_time = time.time()



def initialize_all_databases():
    """
    Initialize processed_books tables for every category found under book/txt.
    """
    txt_root = os.path.join(rootdir, "txt")
    if not os.path.isdir(txt_root):
        print(colored(f"Directory not found: {txt_root}", "red"))
        return

    os.makedirs("database", exist_ok=True)

    def normalize_category(name: str) -> str:
        # Strip separators so DB names match the ones used during processing (e.g. en_non_science -> ennonscience)
        return re.sub(r"[^a-zA-Z0-9\u0400-\u04FF]", "", name)

    raw_categories = [
        entry for entry in os.listdir(txt_root)
        if os.path.isdir(os.path.join(txt_root, entry))
    ]

    categories = sorted({
        normalized for entry in raw_categories
        if (normalized := normalize_category(entry))
    })

    if not categories:
        print(colored(f"No categories found under: {txt_root}", "yellow"))
        return

    for category in categories:
        create_processed_books_table(category)

    print(colored(f"processed_books ready: {', '.join(categories)}", "green"))


def print_all_files_from_rootdir():
    structure = get_directory_structure(rootdir)
    all_folders = get_all_folders(structure)

    list_all_files_from_rootdir = []

    for folder in all_folders:  # работает только для вложенности 2: pdf/basic
        if '/' in folder:
            folder = folder.split('/')
            list_all_files_from_rootdir.append([f"{folder[1]}/{i}" for i in structure[folder[0]][folder[1]]['files']])
    return list_all_files_from_rootdir



def reqursion(all_files_from_rootdir, start_num):
    for y in all_files_from_rootdir:
        if type(y) == list:
            reqursion(y, start_num)
        else:
            if '.txt' in y:
                if (start_num == 1 and 'non_science' in y) or (start_num != 1 and 'non_science' not in y):
                    clear_book_name = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ/]', '', y.split('.')[0], flags=re.IGNORECASE)
                    db_name = clear_book_name.split('/')[0]

                    # === ПРОВЕРКА: уже обработана? ===
                    if is_book_processed(db_name, y):
                        print(colored(f"⏭️ Пропуск: {y[:30]} — уже обработана", 'yellow'))
                        continue

                    # === ОСНОВНАЯ ЛОГИКА ===
                    scinence_word = {}
                    A = analysand_func_dict(y.replace('.txt', ''))

                    try:
                        lang_current_book = detect_main_language(f"E:/Code/english_project/book/txt/{y}")
                        nonscience_db = 'runonscience' if lang_current_book == 'ru' else 'ennonscience'
                        B = select_from_table(nonscience_db, "SELECT word FROM global_union")
                    except:
                        B = ['']

                    for w in A:
                        if (w not in B) and (w != '') and (w != "''"):
                            scinence_word[w] = A[w]

                    sorted_analysand = sorted(scinence_word.items(), key=lambda item: item[1], reverse=True)
                    sorted_analysand, list_del = algo_cleaner(sorted_analysand)

                    # === СОХРАНЕНИЕ ===
                    table_name = clear_book_name.split('/')[1]
                    insert_many_into_table(db_name, table_name, sorted_analysand)
                    insert_many_into_table('delete', 'from_all_files', list_del)

                    # === ОТМЕТИТЬ КАК ОБРАБОТАННУЮ ===
                    mark_book_as_processed(db_name, y, len(sorted_analysand))
                    print(colored(f"✅ Обработана: {y[:30]} | Слов: {len(sorted_analysand)}", 'green'))

                    # === ОБНОВИТЬ АГРЕГАЦИИ ПОСЛЕ КАЖДОЙ КНИГИ ===
                    if y == all_files_from_rootdir[-1]:
                        print(f"=== Обновление агрегаций для {db_name} ===")
                        create_intersection_table(db_name=f"{db_name}.db")
                        create_union_table(db_name=f"{db_name}.db")


def algo_cleaner(sorted_analysand):
#####################################   ПОНЯТНО  #####################################
    def find_dsu(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    length_groups = defaultdict(list)
    for idx, item in enumerate(sorted_analysand):
        s = item[0]
        if len(s) >= 4:
            length_groups[len(s)].append(idx)
   # Вызов DSU
    parent, rank = algo_DSU(sorted_analysand, length_groups)

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

    return result, list_del


def algo_DSU(sorted_analysand, length_groups):
    n = len(sorted_analysand)
    parent = list(range(n))
    rank = [1] * n
    processed = set()
    
    # Итеративная реализация find с path compression
    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]  # Path compression
            u = parent[u]
        return u
    
    def union(u, v):
        u_root = find(u)
        v_root = find(v)
        if u_root == v_root:
            return
        if rank[u_root] < rank[v_root]:
            parent[u_root] = v_root
        else:
            parent[v_root] = u_root
            if rank[u_root] == rank[v_root]:
                rank[u_root] += 1
    
    # Предварительно извлекаем слова, их длины и префиксы
    words = [word for word, _ in sorted_analysand]
    lengths = [len(word) for word in words]
    prefixes = [word[:3] if len(word) >= 3 else word for word in words]
    
    # Создаем кэш расстояний
    distance_cache = {}
    
    # Сортируем длины для обработки
    sorted_lengths = sorted(length_groups.keys())
    
    # Обрабатываем каждую длину
    for l in sorted_lengths:
        current_group = length_groups[l]
        # Группируем текущую группу по префиксам
        current_prefix_map = defaultdict(list)
        for idx in current_group:
            current_prefix_map[prefixes[idx]].append(idx)
        
        # Обрабатываем пары внутри текущей группы
        for prefix, indices in current_prefix_map.items():
            num_indices = len(indices)
            for i in range(num_indices):
                idx1 = indices[i]
                s1 = words[idx1]
                len1 = lengths[idx1]
                for j in range(i + 1, num_indices):
                    idx2 = indices[j]
                    s2 = words[idx2]
                    len2 = lengths[idx2]
                    if abs(len1 - len2) > LEN_LEVENSHTEIN:
                        continue
                    pair = tuple(sorted((idx1, idx2)))
                    if pair in processed:
                        continue
                    # Используем отсортированные слова для кэша
                    cache_key = tuple(sorted((s1, s2)))
                    if cache_key not in distance_cache:
                        distance_cache[cache_key] = Levenshtein.distance(s1, s2)
                    if distance_cache[cache_key] <= LEN_LEVENSHTEIN:
                        union(idx1, idx2)
                        processed.add(pair)
        
        # Обрабатываем соседние группы длин
        for dl in (-3, -2, -1, 1, 2, 3):
            neighbor_l = l + dl
            if neighbor_l not in length_groups:
                continue
            neighbor_group = length_groups[neighbor_l]
            # Группируем соседнюю группу по префиксам
            neighbor_prefix_map = defaultdict(list)
            for idx in neighbor_group:
                neighbor_prefix_map[prefixes[idx]].append(idx)
            
            # Сравниваем текущие префиксы с соседними
            for prefix in current_prefix_map:
                if prefix not in neighbor_prefix_map:
                    continue
                current_indices = current_prefix_map[prefix]
                neighbor_indices = neighbor_prefix_map[prefix]
                for idx1 in current_indices:
                    s1 = words[idx1]
                    len1 = lengths[idx1]
                    for idx2 in neighbor_indices:
                        # Проверяем порядок индексов для избежания дубликатов
                        if idx1 >= idx2:
                            continue
                        s2 = words[idx2]
                        len2 = lengths[idx2]
                        if abs(len1 - len2) > LEN_LEVENSHTEIN:
                            continue
                        pair = tuple(sorted((idx1, idx2)))
                        if pair in processed:
                            continue
                        cache_key = tuple(sorted((s1, s2)))
                        if cache_key not in distance_cache:
                            distance_cache[cache_key] = Levenshtein.distance(s1, s2)
                        if distance_cache[cache_key] <= LEN_LEVENSHTEIN:
                            union(idx1, idx2)
                            processed.add(pair)
    
    return parent, rank


def main(rootdir, start_num):
    # тут мы просто делаем все имена книг чистыми без мусора(пробегается только по /pdf/)
    rename_files_in_directory(rootdir)

    # перебираем все дерево файлов rootdir и все файлы .pdf конвертируем в .txt с помощью pdf_to_txt()
    for root, dirs, files in os.walk(rootdir):
        if files:  # Если в папке есть файлы
            root = root.replace('\\', '/')  # путь к папке
            for file in files:
                if '/txt/' not in root:
                    pdf_to_txt(root, file)

    reqursion(print_all_files_from_rootdir(), start_num)


if __name__ == "__main__":
    initialize_all_databases()  # ← ДОБАВЬ ЭТУ СТРОКУ
    main(rootdir, 1) # это чтобы мы сформировали файлы non_scienct

    main(rootdir, 2) # а это чтобы файылы с науками были чистыми

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Все выполнилось за: ', elapsed_time, 'секунд')
