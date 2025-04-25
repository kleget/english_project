from lemmatize import *
from config import *
from detect_lang import *


def removing_anomaly(text_from_book, lang):  # куча всяких обработок, просто чистим данные полученные из книг 
    arr_all_words = parallel_lemmatize_mp(text_from_book, lang=lang).split(" ")
    # arr_all_words = lemmatize_text_en(lemmatize_text_ru(text_from_book)).split()
    for x in range(len(arr_all_words)):  # тут мы вставляем пробелы по бокам каждого символа кроме букв
        e = set(arr_all_words[x]) & set(chars)
        e = list(e)
        if arr_all_words[x] not in chars:
            if (len(e) != 0) and (len(arr_all_words[x]) != 1):
                i = 0
                while i in range(len(arr_all_words[x])):  # тут нужен цикл для перебора каждой буквы слова
                    if arr_all_words[x][i] in chars:
                        r = len(arr_all_words[x])
                        if i != len(arr_all_words[x]) - 1:
                            arr_all_words[x] = f'{arr_all_words[x][:i:]} {arr_all_words[x][i]} {arr_all_words[x][-(r - i - 1)::]}'
                            i += 1
                        else:
                            arr_all_words[x] = f'{arr_all_words[x][:i:]} {arr_all_words[x][i]}'
                            i += 1
                    i += 1

    arr_all_words = ' '.join(arr_all_words).replace('\xad', ' ').split()

    for x in range(len(arr_all_words)):  # удаляем все числа и все строки с числами
        if arr_all_words[x].isdigit(): # если слово и есть число, удаляем его
            arr_all_words[x] = ' '
        if any(char.isdigit() for char in arr_all_words[x]): # если в слове есть число, это слова удаляем
            arr_all_words[x] = ' '
        if (len(arr_all_words[x]) > 17) or (len(arr_all_words[x]) <= 2):  # из-за кривого pdf->txt если слово слишком длинное(аномалия, склеились без пробелов)
            arr_all_words[x] = ' '
        # if 'cid' in arr_all_words[x]: # из-за кривого pdf->txt было куча cid
        #     arr_all_words[x] = ' '

    return ' '.join(arr_all_words).split(' ')



def get_txt_file(name_file):
    # lang = detect_main_language(f'book/txt/{name_file}.txt')  # вынес открытие и чтение файла, чтобы в функциях не повторяться
    with open(f'book/txt/{name_file}.txt', 'r', encoding='utf-8') as file:
        return removing_anomaly(file.read().lower(), 'ru')


def analysand_func_dict(name_file):  # возвращает список слов в виде словаря
    analysand = {}
    lemmatized_text = sorted(get_txt_file(name_file))

    for x in range(len(lemmatized_text)):  # перебираем все слова текущей страницы
        if lemmatized_text[x] not in analysand:
            analysand[lemmatized_text[x]] = 1
        else:
            analysand[lemmatized_text[x]] += 1

    return analysand


def analysand_func_list(name_file):  # возвращает список слов в виде списка
    analysand = []
    lemmatized_text = get_txt_file(name_file)
    for x in range(len(lemmatized_text)):  # перебираем все слова текущей страницы
        if lemmatized_text[x] not in analysand:
            analysand.append(lemmatized_text[x])
    return analysand


# def levenstein(str_1, str_2):  # расстояние Левенштейна для чистки данных
#     n, m = len(str_1), len(str_2)
#     if n > m:
#         str_1, str_2 = str_2, str_1
#         n, m = m, n

#     current_row = range(n + 1)
#     for i in range(1, m + 1):
#         previous_row, current_row = current_row, [i] + [0] * n
#         for j in range(1, n + 1):
#             add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
#             if str_1[j - 1] != str_2[i - 1]:
#                 change += 1
#             current_row[j] = min(add, delete, change)

#     return current_row[n]
