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
    A = analusys_func_list(list_files_names[0])
    B = analusys_func_list(list_files_names[1])
    math_word = [x for x in B if x not in A]
    # math_word = [x for x in math_word if x.isalpha()]
    print(len(A), len(B), math_word)

main(['voina-i-mir', 'math_in_machine_learning'])
# конечное время
end_time = time.time()

# разница между конечным и начальным временем
elapsed_time = end_time - start_time
print('Elapsed time: ', elapsed_time)

#тут работа с pdf которая блять 16 часов ебашила, вместо 50 секунд на тхт
    # analusys = {}
    # with open(f'{name}.pdf', "rb") as f:
    #     stream = BytesIO(f.read())
    #     doc = PDFDocument(stream)
    #     all_pages = len([p for p in doc.pages()])
    #     for i in range(1, all_pages+1):  # перебираем все страницы файла
    #         viewer = SimplePDFViewer(f)
    #         viewer.navigate(i)
    #         viewer.render()
    #         a = "".join(viewer.canvas.strings)
    #         text = a.split(' ')
    #         for x in range(len(text)):  # перебираем все слова текущей страницы
    #             if text[x] not in analusys:
    #                 analusys[text[x]] = 1
    #             else:
    #                 analusys[text[x]] += 1
    #
    # with open(f'{name}.txt', 'w', encoding="utf-8") as answ_f:
    #     sorted_analusys = sorted(analusys.items(), key=lambda item: item[1], reverse=True)
    #     for t in sorted_analusys:
    #         answ_f.write(f"{t[0]}: {t[1]}\n")
