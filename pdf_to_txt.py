import pdfminer.high_level
import time


start_time = time.time()

with open('math_in_machine_learning.pdf', 'rb') as file:
    file1 = open(r'math_in_machine_learning.txt', 'a+', encoding='UTF-8')
    pdfminer.high_level.extract_text_to_fp(file, file1)
    end_time = time.time()  # время окончания выполнения
    execution_time = end_time - start_time  # вычисляем время выполнения

    print(f"Время выполнения программы: {execution_time} секунд")

    file1.close()

