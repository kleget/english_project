import time
from io import BytesIO
from pdfreader import PDFDocument, SimplePDFViewer

start_time = time.time()

analusys = {}

with open('numpy.pdf', "rb") as f:
    stream = BytesIO(f.read())
    doc = PDFDocument(stream)
    all_pages = len([p for p in doc.pages()])
    for i in range(1, all_pages+1):
        viewer = SimplePDFViewer(f)
        viewer.navigate(i)
        viewer.render()


end_time = time.time()  # время окончания выполнения
execution_time = end_time - start_time  # вычисляем время выполнения

print(f"Время выполнения программы: {execution_time} секунд")
