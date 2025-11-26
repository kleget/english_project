# translation_utils.py
import requests
import time
from pathlib import Path
from secret_data import API_KEY, FOLDER_ID

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


# translation_utils.py — обновлённая функция

def translate_batch(words: list, max_chars: int = 9900) -> list:
    """
    Переводит список слов, группируя их в батчи так, чтобы суммарное количество символов
    в 'texts' не превышало max_chars (ограничение Yandex Translate API — 10 000).
    Каждое слово переводится на противоположный язык.
    """
    translations = []
    i = 0

    while i < len(words):
        batch = []
        batch_texts = []
        current_length = 0
        target_languages = []

        # Формируем батч, пока не превысим лимит
        while i < len(words):
            word = words[i].strip()
            word_len = len(word)

            # Проверяем, поместится ли это слово
            if current_length + word_len > max_chars:
                if not batch:  # Принудительно добавляем, даже если одно слово > 10к
                    batch.append(word)
                    batch_texts.append(word)
                    src_lang = detect_language(word)
                    target_lang = "en" if src_lang == "ru" else "ru"
                    target_languages.append(target_lang)
                    i += 1
                break

            batch.append(word)
            batch_texts.append(word)
            src_lang = detect_language(word)
            target_lang = "en" if src_lang == "ru" else "ru"
            target_languages.append(target_lang)
            current_length += word_len
            i += 1

        # Определяем целевой язык
        if len(set(target_languages)) == 1:
            # Все слова в батче идут в один язык
            data = {
                "folderId": FOLDER_ID,
                "texts": batch_texts,
                "targetLanguageCode": target_languages[0]
            }
            try:
                response = requests.post(URL, headers=HEADERS, json=data)
                response.raise_for_status()
                result = response.json()
                translations += [item["text"] for item in result["translations"]]
            except Exception as e:
                print(f"❌ Ошибка при переводе батча: {e}")
                translations += ["—"] * len(batch_texts)
        else:
            # Разные языки — отправляем по одному
            for word, tgt_lang in zip(batch, target_languages):
                single_data = {
                    "folderId": FOLDER_ID,
                    "texts": [word],
                    "targetLanguageCode": tgt_lang
                }
                try:
                    response = requests.post(URL, headers=HEADERS, json=single_data)
                    response.raise_for_status()
                    result = response.json()
                    translations.append(result["translations"][0]["text"])
                except Exception as e:
                    print(f"❌ Не удалось перевести '{word}': {e}")
                    translations.append("—")

        # Пауза между запросами для безопасности
        time.sleep(0.1)
    print("Перевод завершен!")
    return translations

