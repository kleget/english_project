import multiprocessing
import pymorphy3
import re
import spacy
from functools import lru_cache
import os

nlp = None

# Инициализация модели в дочернем процессе
def init_spacy():
    global nlp
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "textcat"])
    nlp.max_length = 40000000

# Глобальный MorphAnalyzer (лучше тоже в init, но можно и так)
morph = pymorphy3.MorphAnalyzer()

# Кэш
@lru_cache(maxsize=100000)
def get_lemma(word):
    return morph.parse(word)[0].normal_form

# Функции для одного абзаца
def lemmatize_ru_paragraph(paragraph):
    words = re.findall(r'\w+', paragraph.lower())
    return " ".join([get_lemma(w) for w in words])

def lemmatize_en_paragraph(paragraph):
    global nlp
    doc = nlp(paragraph.lower())
    return " ".join([token.lemma_ for token in doc if token.is_alpha])

# Разделение на абзацы
def split_into_paragraphs(text):
    return [p for p in text.split('\n') if p.strip()]

# Параллельная обработка
def parallel_lemmatize_mp(text, lang="ru", max_workers=None):
    paragraphs = split_into_paragraphs(text)

    if lang == "ru":
        func = lemmatize_ru_paragraph
        initializer = None
    elif lang == "en":
        func = lemmatize_en_paragraph
        initializer = init_spacy
    else:
        raise ValueError("Unsupported language")

    if max_workers is None:
        max_workers = os.cpu_count()

    with multiprocessing.Pool(processes=max_workers, initializer=initializer) as pool:
        results = pool.map(func, paragraphs)

    return " ".join(results)