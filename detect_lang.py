import fasttext
import os
import random
import numpy as np  # Явно импортируем numpy
from collections import Counter
from termcolor import colored

fasttext.FastText.eprint = lambda x: None  # отключаем все сообщения fastText


def detect_main_language(
    file_path: str,
    num_samples: int = 10,
    sample_size: int = 1000,
    model_path: str = "lid.176.bin"
) -> str:
    model = fasttext.load_model(model_path)
    file_size = os.path.getsize(file_path)
    languages = []
    
    with open(file_path, "rb") as f:
        for _ in range(num_samples):
            position = 0 if file_size <= sample_size else random.randint(0, file_size - sample_size)
            f.seek(position)
            
            try:
                sample = f.read(sample_size).decode("utf-8", errors='ignore').strip()
                if not sample:
                    continue
                
                labels, probs = model.predict(sample.replace("\n", ""), k=1)
                lang_code = labels[0].replace("__label__", "")
                languages.append(lang_code)
                
            except Exception as e:
                print(colored(f"Error processing sample: {str(e)}"), 'red')
                continue
    
    return Counter(languages).most_common(1)[0][0] if languages else "und"

# Пример использования
# print(detect_main_language("E:/Code/english_project/book/txt/ru_non_science/test.txt"))