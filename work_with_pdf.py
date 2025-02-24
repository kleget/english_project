import time
from io import BytesIO
from pdfreader import PDFDocument, SimplePDFViewer

def pdf_to_txt(file):

    analusys = {}
    with open('math_in_machine_learning.pdf', "rb") as f:
        stream = BytesIO(f.read())
        doc = PDFDocument(stream)
        all_pages = len([p for p in doc.pages()])
        for i in range(1, 3):  # перебираем все страницы файла
            viewer = SimplePDFViewer(f)
            viewer.navigate(i)
            viewer.render()
            a = "".join(viewer.canvas.strings)
            text = a.split(' ')
            for x in range(len(text)):  # перебираем все слова текущей страницы
                if text[x] not in analusys:
                    analusys[text[x]] = 1
                else:
                    analusys[text[x]] += 1

    with open('answer.txt', 'w', encoding="utf-8") as answ_f:
        answ_f.write(str(analusys))
