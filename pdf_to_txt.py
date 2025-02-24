import pdfminer.high_level


def pdf_to_txt(name_file): # конвертируем pdf в txt
    with open(f'book/pdf/{name_file}.pdf', 'rb') as file:
        file1 = open(fr'book/txt/{name_file}.txt', 'a+', encoding='UTF-8')
        pdfminer.high_level.extract_text_to_fp(file, file1)
        file1.close()

