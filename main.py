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

# def find(u, parent):
#     while parent[u] != u:
#         parent[u] = parent[parent[u]]
#         u = parent[u]
#     return u

def union(u, v, parent):
    root_u = find(u, parent)
    root_v = find(v, parent)
    if root_u != root_v:
        parent[root_v] = root_u
    return parent



def find(u, parent):
    while parent[u] != u:
        parent[u] = parent[parent[u]]  # Сжатие пути
        u = parent[u]
    return u

def union_by_rank(u, v, parent, rank):
    root_u = find(u, parent)
    root_v = find(v, parent)
    if root_u != root_v:
        # NEW: Объединение по рангу
        if rank[root_u] > rank[root_v]:
            parent[root_v] = root_u
        else:
            parent[root_u] = root_v
            if rank[root_u] == rank[root_v]:
                rank[root_v] += 1
    return parent

def algo_DSU(sorted_analysand, length_groups):
    # 3. Инициализация DSU
    parent = list(range(len(sorted_analysand)))

    # 4. Поиск и объединение похожих строк
    processed = set()
    maxi = 0 

    # это максимальный элемент из всех вложенных списков length_groups, чтоыбы не вносить лишнее в processed
    for m in length_groups:
        if length_groups[m][-1] > maxi:
            maxi = length_groups[m][-1]

    
    # чтобы он не проверял все одинаковые элементы, я их сразу внесу как проверенные, такак это ни на что не влияет
    for i in range(maxi+1):
        processed.add((i, i))
    

    MIN_COMMON_RATIO = 0.6  # 60% совпадение символов
    # это уже основная оптимизация, чтобы не проверять просто в тупую все по O(n^2)
    for l in list(length_groups.keys()):
        for dl in (0, 1, 2):
            current_l = l + dl
            if current_l not in length_groups:
                continue
                
            for idx1 in length_groups[l]:
                s1 = sorted_analysand[idx1][0]
                for idx2 in length_groups[current_l]:
                    if idx2 <= idx1 or (idx1, idx2) in processed:
                        continue
                    
                    processed.add((idx1, idx2))
                    s2 = sorted_analysand[idx2][0]
                    
                    # Фильтр 1: Проверка общего количества символов
                    common = len(set(s1) & set(s2))
                    if common / max(len(s1), len(s2)) < MIN_COMMON_RATIO:
                        continue
                    
                    # Фильтр 2: Максимальная разница длин
                    if abs(len(s1) - len(s2)) > 2:
                        continue
                    
                    # Фильтр 3: Первые 3 символа должны совпадать, чтобы мы не мержили например (пуСТЬ и чаСТЬ)
                    if s1[:3] != s2[:3]:
                        continue
                    
                    log_file = open("merge_errors.log", "w")

                    if Levenshtein.distance(s1, s2) <= 2:
                        # Проверка на явно не связанные слова
                        if abs(len(s1) - len(s2)) > 2 or s1[:3] != s2[:3]:
                            print('log added')
                            log_file.write(f"UNEXPECTED MERGE: {s1} ({len(s1)}) <- {s2} ({len(s2)}), dist={Levenshtein.distance(s1, s2)}\n")
                        parent = list(range(len(sorted_analysand)))
                        rank = [1] * len(sorted_analysand)  # Инициализация рангов
                        parent = union_by_rank(idx1, idx2, parent, rank)
    return parent

def algo_cleaner(sorted_analysand):
    # Исходные данные должны быть в формате: [["строка", "число"], ...]
    sorted_analysand = [list(item) for item in sorted_analysand]

    # 2. Группировка по длинам строк
    length_groups = defaultdict(list)
    for idx, item in enumerate(sorted_analysand):
        s = item[0]
        if len(s) >= 4: # 4, чтобы раст-е Левенштейна при сравнение с расстаянием <=2 было разумным, а не так, чтобы мы (хуй и душ) объединим в одно слово
            length_groups[len(s)].append(idx)  # а вот это я не понял нахуя

    parent = algo_DSU(sorted_analysand, length_groups)

    ################################################################
    prefix_groups = defaultdict(list)
    for idx, item in enumerate(sorted_analysand):
        word = item[0]
        if len(word) >= MIN_WORD_LENGTH:
            prefix = word[:PREFIX_LENGTH] if len(word) >= PREFIX_LENGTH else word
            key = (len(word), prefix)
            prefix_groups[key].append(idx)

    # 3. Кэширование расстояния Левенштейна (NEW)
    @lru_cache(maxsize=100000)
    def cached_levenshtein(s1, s2):
        return Levenshtein.distance(s1, s2)

    # 4. Оптимизированное сравнение пар (NEW)
    processed_pairs = set()
    for (length, prefix), group in prefix_groups.items():
        group_size = len(group)
        for i in range(group_size):
            idx1 = group[i]
            s1 = sorted_analysand[idx1][0]
            
            # Сравниваем только с ближайшими соседями
            for j in range(i+1, min(i+MAX_GROUP_SIZE, group_size)):
                idx2 = group[j]
                
                # Пропускаем уже обработанные пары
                if (idx1, idx2) in processed_pairs:
                    continue
                processed_pairs.add((idx1, idx2))
                
                s2 = sorted_analysand[idx2][0]
                
                # Быстрая проверка длины
                if abs(len(s1) - len(s2)) > 2:
                    continue
                
                # Основная проверка
                if cached_levenshtein(s1, s2) <= 2:
                    # union(idx1, idx2)
                    parent = union(idx1, idx2, parent)




    ################################################################

    # 5. Формирование результата и списка удаленных элементов
    groups = defaultdict(list)
    list_del = []

    for idx in range(len(sorted_analysand)):
        groups[find(idx, parent)].append(idx)

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