# translation_utils.py
import requests
import time
from pathlib import Path
from secret_data import *

# === Ваши данные ===
URL = "https://translate.api.cloud.yandex.net/translate/v2/translate"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {API_KEY}"
}


def detect_language(word: str) -> str:
    """Определяет язык: если есть кириллица — русский, иначе английский."""
    word = word.strip()
    return "ru" if any('а' <= c.lower() <= 'я' for c in word) else "en"


def translate_batch(words: list, batch_size: int = 800) -> list:
    """
    Переводит список слов пакетно, группируя по направлению перевода (ru→en, en→ru).
    """
    translations = ["—"] * len(words)  # заглушка на случай ошибки
    word_to_index = {}  # чтобы сохранить порядок

    # Группируем слова по индексам и языкам
    en_batch = []  # en → ru
    ru_batch = []  # ru → en
    en_indices = []
    ru_indices = []

    for i, word in enumerate(words):
        word_to_index[word] = i
        src_lang = detect_language(word)
        if src_lang == "ru":
            ru_batch.append(word)
            ru_indices.append(i)
        else:
            en_batch.append(word)
            en_indices.append(i)

    # Вспомогательная функция для перевода пачки
    def send_batch(texts, target_lang, indices):
        if not texts:
            return
        data = {
            "folderId": FOLDER_ID,
            "texts": texts,
            "targetLanguageCode": target_lang
        }
        try:
            response = requests.post(URL, headers=HEADERS, json=data)
            response.raise_for_status()
            result = response.json()
            for idx, translation in zip(indices, result["translations"]):
                translations[idx] = translation["text"]
        except Exception as e:
            print(f"❌ Ошибка при переводе {len(texts)} слов ({target_lang}): {e}")
            for idx in indices:
                translations[idx] = "—"

    # Отправляем пачки (разбиваем на подбатчи по batch_size)
    for i in range(0, len(ru_batch), batch_size):
        send_batch(ru_batch[i:i+batch_size], "en", ru_indices[i:i+batch_size])

    for i in range(0, len(en_batch), batch_size):
        send_batch(en_batch[i:i+batch_size], "ru", en_indices[i:i+batch_size])

    # Пауза после всех запросов
    time.sleep(0.1)
    return translations
