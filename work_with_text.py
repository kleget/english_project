import re
chars = r"""!"#$%&'()*+-,./:;<=>?@[\]^_`{|}~×–…“”«»—"""
' « художественная'
def removing_anomaly(mas):  # удаляем аномалии из текста



    mas = mas.split()
    for x in range(len(mas)):  # тут мы вставляем пробелы по бокам каждого символа кроме букв
        e = set(mas[x]) & set(chars)
        e = list(e)
        if len(mas[x]) > 17:  # если слово слишком длинное(аномалия, склеились без пробелов)
            mas[x] = ' '

        if (len(e) != 0) and (len(mas[x]) != 1):
            i = 0
            while i in range(len(mas[x])):
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
    'экспоненциальным'
    return ' '.join(mas).split(' ')


def multiple_replace(tekst, zamena):
    pattern = re.compile("|".join(sorted((re.escape(k) for k in zamena), key=len, reverse=True)), re.DOTALL)
    return pattern.sub(lambda m: zamena[m.group(0)], tekst)


def analusys_func_dict(name_file):
    analusys = {}

    with open(f'book/txt/{name_file}.txt', 'r', encoding='utf-8') as file:
        f = file.read()
        f = f.lower()
        # text = f.split(' ')
        text = removing_anomaly(f)
        for x in range(len(text)):  # перебираем все слова текущей страницы
            if text[x] not in analusys:
                analusys[text[x]] = 1
            else:
                analusys[text[x]] += 1

    return analusys


def analusys_func_list(name_file):
    analusys = []

    with open(f'book/txt/{name_file}.txt', 'r', encoding='utf-8') as file:
        f = file.read()
        f = f.lower()
        # text = f.split(' ')
        text = removing_anomaly(f)
        for x in range(len(text)):  # перебираем все слова текущей страницы
            if text[x] not in analusys:
                analusys.append(text[x])


    return analusys


