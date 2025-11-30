from lemmatize import *
from config import *
from detect_lang import *
import re


def fix_hyphenated_words(text):
    """
    Объединяет слова, разделенные переносом на разные строки.
    Обрабатывает различные форматы переносов в PDF файлах:
    - "од-\nнако" → "однако"
    - "непо\xad\nдалеку" → "неподалеку"
    - "за\nграницей" → "заграницей"
    - "\nоднако" → "однако" (слово начинается с новой строки)
    - "затра\xad\n      гивает" → "затрагивает"
    """
    # Шаг 1: Удаляем различные невидимые символы переноса (делаем это первым!)
    text = text.replace('\xad', '')  # soft hyphen
    text = text.replace('\u200b', '')  # zero-width space
    text = text.replace('\u2011', '')  # non-breaking hyphen
    text = text.replace('\u00ad', '')  # soft hyphen (другой код)
    
    # Шаг 2: Обрабатываем переносы с дефисом и множественными пробелами
    # Паттерн 1: слово-дефис + пробелы/табуляция + перенос строки + пробелы + слово
    text = re.sub(
        r'([а-яА-ЯёЁa-zA-Z]{1,10})[\s\t]*-\s*\r?\n\s*([а-яА-ЯёЁa-zA-Z]{2,})',
        lambda m: m.group(1) + m.group(2) if len(m.group(1)) + len(m.group(2)) <= 25 else m.group(0),
        text,
        flags=re.MULTILINE
    )
    
    # Паттерн 2: слово-дефис + пробелы + слово (когда pdftotext убрал перенос, но оставил пробелы)
    text = re.sub(
        r'([а-яА-ЯёЁa-zA-Z]{1,10})[\s\t]*-\s+([а-яА-ЯёЁa-zA-Z]{2,})',
        lambda m: m.group(1) + m.group(2) if len(m.group(1)) + len(m.group(2)) <= 25 else m.group(0),
        text
    )
    
    # Шаг 3: Обрабатываем переносы без дефиса между словами
    # Паттерн 3: слово1 + пробелы + перенос строки + пробелы + слово2
    # Объединяем только если оба слова короткие или суммарная длина разумная
    def merge_words(match):
        word1 = match.group(1)
        word2 = match.group(2)
        total_len = len(word1) + len(word2)
        # Объединяем если:
        # - оба слова короткие (<= 5 символов каждое), ИЛИ
        # - первое слово очень короткое (<= 3) и второе длинное, ИЛИ
        # - суммарная длина <= 15
        if (len(word1) <= 5 and len(word2) <= 5) or \
           (len(word1) <= 3 and len(word2) >= 3) or \
           (total_len <= 15):
            return word1 + word2
        return match.group(0)
    
    text = re.sub(
        r'([а-яА-ЯёЁa-zA-Z]{1,8})\s+\r?\n\s+([а-яА-ЯёЁa-zA-Z]{2,})',
        merge_words,
        text,
        flags=re.MULTILINE
    )
    
    # Паттерн 4: слово + перенос строки + пробелы + слово (без пробелов перед переносом)
    text = re.sub(
        r'([а-яА-ЯёЁa-zA-Z]{1,8})\r?\n\s+([а-яА-ЯёЁa-zA-Z]{2,})',
        merge_words,
        text,
        flags=re.MULTILINE
    )
    
    # Паттерн 5: перенос строки + пробелы + слово (слово начинается с новой строки)
    # Это обрабатывает случаи типа "\nоднако" или "слово \nоднако"
    # Объединяем только если перед переносом есть пробел или знак препинания (не буква)
    text = re.sub(
        r'([\s.,;:!?])\s*\r?\n\s+([а-яА-ЯёЁa-zA-Z]{2,})',
        r'\1 \2',  # Заменяем на исходный символ + пробел + слово
        text,
        flags=re.MULTILINE
    )
    
    # Паттерн 5b: начало строки + пробелы + слово (обрабатывает "\nоднако" в начале текста)
    text = re.sub(
        r'^\s*\r?\n\s+([а-яА-ЯёЁa-zA-Z]{2,})',
        r'\1',  # Убираем перенос, оставляем только слово
        text,
        flags=re.MULTILINE
    )
    
    # Шаг 4: Обрабатываем длинные переносы (первая часть 6-15 символов)
    text = re.sub(
        r'([а-яА-ЯёЁa-zA-Z]{6,15})[\s\t]*-\s*\r?\n\s*([а-яА-ЯёЁa-zA-Z]{2,6})',
        lambda m: m.group(1) + m.group(2) if len(m.group(1)) + len(m.group(2)) <= 25 else m.group(0),
        text,
        flags=re.MULTILINE
    )
    
    # Шаг 5: Финальная очистка - удаляем одиночные переносы строки между словами
    # (оставляем только те, что в конце абзаца)
    text = re.sub(r'([а-яА-ЯёЁa-zA-Z])\s*\r?\n\s*([а-яА-ЯёЁa-zA-Z])', r'\1 \2', text, flags=re.MULTILINE)
    
    return text


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
        text = file.read().lower()
        # Исправляем переносы ДО обработки
        text = fix_hyphenated_words(text)
        return removing_anomaly(text, 'ru')


def analysand_func_dict(name_file):  # возвращает список слов в виде словаря
    analysand = {}
    lemmatized_text = sorted(get_txt_file(name_file))

    for x in range(len(lemmatized_text)):  # перебираем все слова текущей страницы
        if lemmatized_text[x] not in analysand:
            analysand[lemmatized_text[x]] = 1
        else:
            analysand[lemmatized_text[x]] += 1

    return analysand


# def analysand_func_list(name_file):  # возвращает список слов в виде списка
#     analysand = []
#     lemmatized_text = get_txt_file(name_file)
#     for x in range(len(lemmatized_text)):  # перебираем все слова текущей страницы
#         if lemmatized_text[x] not in analysand:
#             analysand.append(lemmatized_text[x])
#     return analysand
