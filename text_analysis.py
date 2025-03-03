from lemmatize import *

chars = r"""!"#$%&'()*+-,./:;<=>?@[\]^_`{|}~×–…“”«»—"""


def removing_anomaly(mas):
    mas = lemmatize_text_en(lemmatize_text_ru(mas))
    mas = mas.split()  # удаляем аномалии из текста
    for x in range(len(mas)):  # тут мы вставляем пробелы по бокам каждого символа кроме букв
        e = set(mas[x]) & set(chars)
        e = list(e)
        if mas[x] not in chars:
            if (len(e) != 0) and (len(mas[x]) != 1):
                i = 0
                while i in range(len(mas[x])):  # тут нужен цикл для перебора каждой буквы слова
                    if mas[x][i] in chars:
                        r = len(mas[x])
                        if i != len(mas[x]) - 1:
                            mas[x] = f'{mas[x][:i:]} {mas[x][i]} {mas[x][-(r - i - 1)::]}'
                            i += 1
                        else:
                            mas[x] = f'{mas[x][:i:]} {mas[x][i]}'
                            i += 1
                    i += 1
    mas = ' '.join(mas)
    mas = mas.replace('\xad', ' ')
    # mas = re.sub(r'\\x.{2}', ' ', mas)
    mas = mas.split()

    for x in range(len(mas)):  # удаляем к все числа и все строки с числами
        if mas[x].isdigit():
            mas[x] = ' '
        if any(character.isdigit() for character in mas[x]):
            mas[x] = ' '
        if (len(mas[x]) > 17) or (len(mas[x]) <= 2):  # если слово слишком длинное(аномалия, склеились без пробелов)
            mas[x] = ' '
        if 'cid' in mas[x]:
            mas[x] = ' '
        # mas[x] = lemmatize_text_en(lemmatize_text_ru(mas[x]))

    # e = 0
    # g = 1
    # while e in range(len(mas)):
    #     while g in range(len(mas)):
    #         if levenstein(mas[e], mas[g]) <= 2:
    #             mas[e] += mas[g]
    #             del mas[g]
    #         else:
    #             g += 1
    #     e += 1
    return ' '.join(mas).split(' ')


def multiple_replace(tekst, zamena):  # не помню зачем
    pattern = re.compile("|".join(sorted((re.escape(k) for k in zamena), key=len, reverse=True)), re.DOTALL)
    return pattern.sub(lambda m: zamena[m.group(0)], tekst)


def get_file(name_file):  # вынес открытие и чтение файла, чтобы в функциях не повторяться
    with open(f'book/txt/{name_file}.txt', 'r', encoding='utf-8') as file:
        f = file.read()
        f = f.lower()
        text = removing_anomaly(f)
    return text


def analysand_func_dict(name_file):  # возвращает список слов в виде словаря
    analysand = {}
    text = get_file(name_file)
    for x in range(len(text)):  # перебираем все слова текущей страницы
        if text[x] not in analysand:
            analysand[text[x]] = 1
        else:
            analysand[text[x]] += 1

    return analysand


def analysand_func_list(name_file):  # возвращает список слов в виде списка
    analysand = []
    text = get_file(name_file)
    for x in range(len(text)):  # перебираем все слова текущей страницы
        if text[x] not in analysand:
            analysand.append(text[x])
    return analysand


def levenstein(str_1, str_2):
    n, m = len(str_1), len(str_2)
    if n > m:
        str_1, str_2 = str_2, str_1
        n, m = m, n

    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if str_1[j - 1] != str_2[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]

# print(levenstein('матрицы', 'матрица'))