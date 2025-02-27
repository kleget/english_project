from io import BytesIO
from pdfreader import PDFDocument, SimplePDFViewer
from pdf_to_txt import *
from work_with_text import *

import time

# начальное время
start_time = time.time()
def main(list_files_names):
    # тут мы все pdf делаем текстовыми
    # for x in range(len(list_files_names)):
    #     pdf_to_txt(list_files_names[x])

    # for x in range(len(list_files_names)):
    A = analusys_func_dict(list_files_names[0])
    B = analusys_func_dict(list_files_names[1])
    math_word = {}
    for x in B:
        if x not in A:
            math_word[x] = B[x]
    # math_word = [x for x in math_word if x.isalpha()]
    sorted_analysand = {}
    sorted_analysand = sorted(math_word.items(), key=lambda item: item[1], reverse=True)
    with open('answer.txt', 'w', encoding='UTF-8') as ans_f:
        for t in sorted_analysand:
            ans_f.write(f"{t[0]}: {t[1]}\n")

    print(len(sorted_analysand))

main(['voina-i-mir', 'math_in_machine_learning'])
# конечное время
end_time = time.time()

# разница между конечным и начальным временем
elapsed_time = end_time - start_time
print('Elapsed time: ', elapsed_time)

