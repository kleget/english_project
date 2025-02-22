# user_0 = {
#     'username': 'efermi',
#     'first': 'enrico',
#     'last': 'fermi',
#     }
#
# for key, value in user_0.items():
#     print("Key: " + key)
#     print("Value: " + value + "\n")
import time
# from io import BytesIO
# from pdfreader import PDFDocument, SimplePDFViewer
#
start_time = time.time()
#
# analusys = {}
# with open('math_in_machine_learning.pdf', "rb") as f:
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
# with open('answer.txt', 'w', encoding="utf-8") as answ_f:
#     # sorted_analusys = sorted(analusys.items(), key=lambda item: item[1], reverse=True)
#     # for t in sorted_analusys:
#     answ_f.write(str(analusys))
analusys = {}

with open('math_in_machine_learning.txt', 'r', encoding='utf-8') as file:
    f = file.read()
    # a = "".join(f)
    text = f.split(' ')
    for x in range(len(text)):  # перебираем все слова текущей страницы
        if text[x] not in analusys:
            analusys[text[x]] = 1
        else:
            analusys[text[x]] += 1

# with open('answer.txt', 'w', encoding="utf-8") as answ_f:
#     # sorted_analusys = sorted(analusys.items(), key=lambda item: item[1], reverse=True)
#     # for t in sorted_analusys:
#     answ_f.write(str(analusys))
#     print(len(analusys))
with open('answer.txt', 'w', encoding="utf-8") as answ_f:
    sorted_analusys = sorted(analusys.items(), key=lambda item: item[1], reverse=True)
    for t in sorted_analusys:
        answ_f.write(f"{t[0]}: {t[1]}\n")



end_time = time.time()  # время окончания выполнения
execution_time = end_time - start_time  # вычисляем время выполнения

print(f"Время выполнения программы: {execution_time} секунд")

# end_time = time.time()  # время окончания выполнения
# execution_time = end_time - start_time  # вычисляем время выполнения
#
# print(f"Время выполнения программы: {execution_time} секунд")
