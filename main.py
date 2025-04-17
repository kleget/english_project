from io import BytesIO
from pdfreader import PDFDocument, SimplePDFViewer
from file_processing import *
from text_analysis import *
import os
import time
from config import *



# начальное время
start_time = time.time()

def print_all_files_from_rootdir():
    # я не знаю, смысла в этом нет, функция создана просто чтобы можно было вывести структуру
    structure = get_directory_structure(rootdir)
    all_folders = get_all_folders(structure)

    list_all_files_from_rootdir = []

    for x in all_folders:  # работает только для вложенности 2: pdf/basic
        if '/' in x:
            x = x.split('/')
            list_all_files_from_rootdir.append(structure[x[0]][x[1]]['files'])
    return list_all_files_from_rootdir



def main(rootdir):
    # тут мы просто делаем все имена книг чистыми без мусора(пробегается только по /pdf/)
    rename_files_in_directory(rootdir)

    # перебираем все дерево файлов rootdir и все файлы .pdf конвертируем в .txt с помощью pdf_to_txt()
    for root, dirs, files in os.walk(rootdir):
        if files:  # Если в папке есть файлы
            root = root.replace('\\', '/')# Выводим путь к папке
            print(root)
            for file in files:
                if '/txt/' not in root:
                    pdf_to_txt(root, file)

    list_all_files = print_all_files_from_rootdir()  #
    # for x in range(len(list_files_names)):
    #     pdf_to_txt(list_files_names[x])

    # for x in range(len(list_files_names)):
    A = analysand_func_dict(rootdir) # сюда нужно файл передавать конкретный из txt уже
    B = analysand_func_dict(rootdir)

    math_word = {}
    for x in B:  # тут мы проверяем, чтобы в math_word попали только те слова, которых нет в обычной книге
        if x not in A:
            math_word[x] = B[x]
    sorted_analysand = sorted(math_word.items(), key=lambda item: item[1], reverse=True)
    sorted_analysand = [list(item) for item in sorted_analysand]

    # тут мы в файл записываем все, что мы удалили, весь мусор, просто на всякий случай, и так-же применяем расстояние Левеншейна
    with open('answer_deleting.txt', 'w', encoding='UTF-8') as ans_d:
        e = 0
        g = 1
        while e in range(len(sorted_analysand)-1):
            while g in range(len(sorted_analysand)-1):
                if (levenstein(sorted_analysand[e][0], sorted_analysand[g][0]) <= 2) and ((len(sorted_analysand[e][0]) >= 4) and (len(sorted_analysand[g][0]) >= 4)):
                    sorted_analysand[e][1] += sorted_analysand[g][1]
                    ans_d.write(f"{sorted_analysand[g][0]}: {sorted_analysand[g][1]}\n")
                    del sorted_analysand[g]
                else:
                    g += 1
            e += 1
            g = e+1


    with open('answer.txt', 'w', encoding='UTF-8') as ans_a:
        sorted_analysand = sorted(sorted_analysand, key=lambda item: item[1], reverse=True)
        # sorted_analysand = list(map(list, sorted_analysand))
        sorted_analysand = [list(item) for item in sorted_analysand]
        for i in range(len(sorted_analysand)):
            ans_a.write(f"{sorted_analysand[i][0]}: {sorted_analysand[i][1]}\n")

    print(len(sorted_analysand))


main(rootdir)
# конечное время
end_time = time.time()

# разница между конечным и начальным временем
elapsed_time = end_time - start_time
print('Elapsed time: ', elapsed_time)
print('for test')

