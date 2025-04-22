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

    for x in all_folders:  # работает только для вложенности 2: pdf/basic
        if '/' in x:
            x = x.split('/')
            # list_all_files_from_rootdir.append(structure[x[0]][x[1]]['files'])
            list_all_files_from_rootdir.append([f"{x[1]}/{i}" for i in structure[x[0]][x[1]]['files']])
    return list_all_files_from_rootdir

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
                print("x_y:", x_y)
                # create_table(*x_y.split('/'))  # добавил эту функцию сразу в INSERT, чтобы не было недоразумений

                A = analysand_func_dict(y.replace('.txt', ''))  # получаем массив НЕ отсортированных готовых данных из книги
                # B = select_from_table(x_y.split('/')[0], f"SELECT word FROM {x_y.split('/')[1]}")  # B - это обычные слова, А - это специальные слова
                B = ['']
                print(1)
                for x in A:  # тут мы проверяем, чтобы в math_word попали только те слова, которых нет в обычной книге
                    if (x not in B) and (x != '') and (x != "''"):
                        math_word[x] = A[x]
                print(2)
                sorted_analysand = sorted(math_word.items(), key=lambda item: item[1], reverse=True)
                print(3)
                #############################################################################
                #################### работает, но
                # sorted_analysand = [list(item) for item in sorted_analysand] # из хуйни в список списков
                # print(4)
                #
                # # это выполняется ооочень долго
                # e = 0
                # g = 1
                # dict_del = {}
                # print(f"len(sorted_analysand)={len(sorted_analysand)}")
                # while e in range(len(sorted_analysand) - 1):
                #     print(e)
                #     while g in range(len(sorted_analysand) - 1):
                #         if (levenstein(sorted_analysand[e][0], sorted_analysand[g][0]) <= 2) and (
                #                 (len(sorted_analysand[e][0]) >= 4) and (len(sorted_analysand[g][0]) >= 4)):
                #             sorted_analysand[e][1] += sorted_analysand[g][1]
                #             dict_del[sorted_analysand[g][0]] = sorted_analysand[g][1]
                #             del sorted_analysand[g]
                #         else:
                #             g += 1
                #     e += 1
                #     g = e + 1
                #############################################################################


                # Исходные данные должны быть в формате: [["строка", "число"], ...]
                sorted_analysand = [list(item) for item in sorted_analysand]

                # 1. Преобразование строковых значений в числа (тут и так в int)
                # for item in sorted_analysand:
                #     item[1] = int(item[1])

                # 2. Группировка по длинам строк
                length_groups = defaultdict(list)
                for idx, item in enumerate(sorted_analysand):
                    s = item[0]
                    if len(s) >= 4: # 4, чтобы раст-е Левенштейна при сравнение с расстаянием <=2 было разумным, а не так, чтобы мы (хуй и душ) объединим в одно слово
                        length_groups[len(s)].append(idx)  # а вот это я не понял нахуя

                # 3. Инициализация DSU
                parent = list(range(len(sorted_analysand)))

                def find(u):
                    while parent[u] != u:
                        parent[u] = parent[parent[u]]
                        u = parent[u]
                    return u

                def union(u, v):
                    root_u = find(u)
                    root_v = find(v)
                    if root_u != root_v:
                        parent[root_v] = root_u

                # 4. Поиск и объединение похожих строк
                processed = set()
                maxi = 0 
                # это максимальный элемент из всех вложенных списков length_groups, чтоыбы не вносить лишнее в processed
                for m in length_groups:
                    if length_groups[m][-1] > maxi:
                        maxi = length_groups[m][-1]

                
                # чтобы он не проверял все одинаковые элементы, я из сразу внесу как проверенные, такак это ни на что не влияет
                for i in range(maxi+1):
                    processed.add((i, i))
                

                MIN_COMMON_RATIO = 0.6  # 60% совпадение символов

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
                                
                                # Фильтр 3: Первые 3 символа должны совпадать
                                if s1[:3] != s2[:3]:
                                    continue
                                
                                log_file = open("merge_errors.log", "w")

                                if Levenshtein.distance(s1, s2) <= 2:
                                    # Проверка на явно не связанные слова
                                    if abs(len(s1) - len(s2)) > 2 or s1[:3] != s2[:3]:
                                        log_file.write(f"UNEXPECTED MERGE: {s1} ({len(s1)}) <- {s2} ({len(s2)}), dist={Levenshtein.distance(s1, s2)}\n")
                                    union(idx1, idx2)
                # # это уже основная оптимизация, чтобы не проверять просто в тупую все по O(n^2)
                # for l in list(length_groups.keys()): 
                #     for dl in (0, 1, 2):
                #         current_l = l + dl
                #         if current_l not in length_groups:
                #             continue
                #         # current_l - это нужно для того, чтобы не сравнивать все элеметны со всеми, потому что levenshtain занимает много времени. 
                #         # ведь логично, что слова 'hello' и 'hi' нет смысла сравнивать, так как их длинна отличается на на 3, а мы рассматриваем только ( |len(a)-(len(b))| <= 2 )
                #         # поэтому мы берем длину слова hello(5) и сравниваем это слова только со словами, длинна которых 5, 6, 7
                #         # так мы сильно сократим кол-во проверок levenshtain
                #         # idx1 - это значение элемента l из length_groups (а это значени в свою очередь индекс элемента из sorted analysand)
                #         # idx2 - это значение элемента current_l из length_groups
                #         for idx1 in length_groups[l]:
                #             s1 = sorted_analysand[idx1][0]
                #             for idx2 in length_groups[current_l]:
                #                 # if idx2 > idx1:
                #                 #     break
                #                 if idx1 < idx2 or (idx1, idx2) in processed:
                #                     continue

                #                 processed.add((idx1, idx2))
                #                 s2 = sorted_analysand[idx2][0]

                #                 if Levenshtein.distance(s1, s2) <= 2:
                #                     union(idx1, idx2)

                # 5. Формирование результата и списка удаленных элементов
                groups = defaultdict(list)
                list_del = []

                for idx in range(len(sorted_analysand)):
                    groups[find(idx)].append(idx)

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
                    total = sum(sorted_analysand[idx][1] for idx in group)
                    result.append([main_item[0], str(total)])

                # 6. Возвращаем данные в исходный формат
                sorted_analysand = result



                print(5)
                # list_del = []
                # for x in dict_del:  # это нужно для того, чтобы список конвертировать в вложенный список для записи в бд
                    # list_del.append([x, dict_del[x]])
                print("Finish: ", len(sorted_analysand))
                insert_many_into_table('delete', 'from_all_files', list_del)
                insert_many_into_table(*x_y.split('/'), sorted_analysand) # тут записываем окончательный набор данных в БД


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

    # A = analysand_func_dict(rootdir) # сюда нужно файл передавать конкретный из txt уже
    # B = analysand_func_dict(rootdir)
    #
    # math_word = {}
    # for x in B:  # тут мы проверяем, чтобы в math_word попали только те слова, которых нет в обычной книге
    #     if x not in A:
    #         math_word[x] = B[x]
    # sorted_analysand = sorted(math_word.items(), key=lambda item: item[1], reverse=True)
    # sorted_analysand = [list(item) for item in sorted_analysand]

    # тут мы в файл записываем все, что мы удалили, весь мусор, просто на всякий случай, и так-же применяем расстояние Левеншейна
    # with open('answer_deleting.txt', 'w', encoding='UTF-8') as ans_d:
    #     e = 0
    #     g = 1
    #     while e in range(len(sorted_analysand)-1):
    #         while g in range(len(sorted_analysand)-1):
    #             if (levenstein(sorted_analysand[e][0], sorted_analysand[g][0]) <= 2) and ((len(sorted_analysand[e][0]) >= 4) and (len(sorted_analysand[g][0]) >= 4)):
    #                 sorted_analysand[e][1] += sorted_analysand[g][1]
    #                 ans_d.write(f"{sorted_analysand[g][0]}: {sorted_analysand[g][1]}\n")
    #                 del sorted_analysand[g]
    #             else:
    #                 g += 1
    #         e += 1
    #         g = e+1

    # тут мы ответ записываем в файл, но это только если у нас один файл, а если у меня дохуя?
    # я уже делаю все череб бд
    # with open('answer.txt', 'w', encoding='UTF-8') as ans_a:
    #     sorted_analysand = sorted(sorted_analysand, key=lambda item: item[1], reverse=True)
    #     # sorted_analysand = list(map(list, sorted_analysand))
    #     sorted_analysand = [list(item) for item in sorted_analysand]
    #     for i in range(len(sorted_analysand)):
    #         ans_a.write(f"{sorted_analysand[i][0]}: {sorted_analysand[i][1]}\n")

    # print(len(sorted_analysand))


main(rootdir)
# конечное время
end_time = time.time()

# разница между конечным и начальным временем
elapsed_time = end_time - start_time
print('Elapsed time: ', elapsed_time)

