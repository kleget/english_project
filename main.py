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
    A = analysand_func_dict(list_files_names[0])
    B = analysand_func_dict(list_files_names[1])

    math_word = {}
    for x in B:  # тут мы проверяем, чтобы в math_word попали только те слова, которых нет в обычной книге
        if x not in A:
            math_word[x] = B[x]
    sorted_analysand = sorted(math_word.items(), key=lambda item: item[1], reverse=True)
    sorted_analysand = [list(item) for item in sorted_analysand]

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

main(['voina-i-mir', 'math_in_machine_learning'])
# конечное время
end_time = time.time()

# разница между конечным и начальным временем
elapsed_time = end_time - start_time
print('Elapsed time: ', elapsed_time)

