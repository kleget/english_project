# database_operations.py
from config import *
import sqlite3 as sq
import os
from pathlib import Path
from translation_utils import translate_batch


def create_table(db_name: str, table_name: str):
    if not os.path.exists('database'):
        os.makedirs('database')
    if '.db' not in db_name:
        db_name += '.db'

    if table_name == 'from_all_files':
        schema = "id INTEGER PRIMARY KEY AUTOINCREMENT, deleted_word TEXT NOT NULL, count INTEGER NOT NULL, merged_to TEXT NOT NULL"
    else:
        schema = "id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL, count INTEGER NOT NULL"

    db_path = Path('database') / f"{db_name}.db" if '.db' not in db_name else Path('database') / db_name
    with sq.connect(db_path) as con:
        sql = con.cursor()
        sql.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
        con.commit()


def insert_many_into_table(db_name: str, table_name: str, data: list):
    if '.db' not in db_name:
        db_name += '.db'
    create_table(db_name, table_name)

    if table_name == 'from_all_files':
        columns = ('deleted_word', 'count', 'merged_to')
        query = f"INSERT INTO {table_name} {columns} VALUES (?, ?, ?)"
    else:
        columns = ('word', 'count')
        query = f"INSERT INTO {table_name} {columns} VALUES (?, ?)"

    db_path = Path('database') / db_name
    with sq.connect(db_path) as con:
        sql = con.cursor()
        formatted_data = list({tuple(item) for item in data})
        sql.executemany(query, formatted_data)
        con.commit()


def select_from_table(db_name: str, request: str):
    if '.db' not in db_name:
        db_name += '.db'
    db_path = Path('database') / db_name
    with sq.connect(db_path) as con:
        sql = con.cursor()
        sql.execute(request)
        return [item[0] for item in sql.fetchall()]



def create_intersection_table_query(tables, db_path: Path, result_table: str = "word_intersection"): 
    """
    Выполняет создание таблицы пересечения в указанной БД.
    """
    if not db_path.exists():
        print(f"Файл базы данных {db_path} не найден!")
        return False

    try:
        conn = sq.connect(db_path)
        cursor = conn.cursor()

        # Удаляем старую таблицу
        cursor.execute(f"DROP TABLE IF EXISTS {result_table}")

        # Запрос: найти слова, присутствующие во всех таблицах
        union_words = ' UNION ALL '.join([f"SELECT word, '{table}' as src FROM {table}" for table in tables])
        intersection_words = f"""
            SELECT word FROM (
                SELECT word, COUNT(DISTINCT src) as cnt FROM ({union_words})
                GROUP BY word HAVING cnt = {len(tables)}
            )
        """

        # Создаём таблицу с суммой частот только для этих слов
        union_counts = ' UNION ALL '.join([f"SELECT word, count FROM {table}" for table in tables])
        sum_query = f"""
            CREATE TABLE {result_table} AS
            SELECT 
                t.word,
                SUM(t.count) as count
            FROM ({union_counts}) t
            WHERE t.word IN ({intersection_words})
            GROUP BY t.word
            ORDER BY count DESC
        """
        cursor.execute(sum_query)
        conn.commit()

        total = cursor.execute(f"SELECT COUNT(*) FROM {result_table}").fetchone()[0]
        print(f"Создана таблица {result_table} с {total} словами.")
        conn.close()
        return True

    except Exception as e:
        print(f"Ошибка при создании пересечения: {e}")
        conn.rollback()
        conn.close()
        return False



def create_translations_table(cursor, table_name: str = "translations"):
    """
    Создает таблицу для хранения переводов слов.
    """
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            word TEXT PRIMARY KEY,
            count INTEGER NOT NULL,
            translation TEXT NOT NULL
        )
    """)
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_word ON {table_name}(word)")


def create_union_table_query(tables, db_path: Path, result_table: str = "global_union", 
                             translation_threshold: float = 0.25):
    """
    Выполняет создание таблицы объединения в указанной БД.
    Переводы хранятся в отдельной таблице translations только для часто используемых слов.
    
    :param translation_threshold: Доля слов для перевода (0.25 = топ 25%)
    """
    if not db_path.exists():
        print(f"Файл базы данных {db_path} не найден!")
        return False

    try:
        conn = sq.connect(db_path)
        cursor = conn.cursor()

        # Удаляем только таблицу global_union (translations сохраняем для кэша)
        cursor.execute(f"DROP TABLE IF EXISTS {result_table}")

        # Создаём таблицу global_union БЕЗ колонки translation
        cursor.execute(f"""
            CREATE TABLE {result_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                count INTEGER NOT NULL
            )
        """)

        # Создаём отдельную таблицу для переводов
        create_translations_table(cursor)

        # Собираем и суммируем все слова
        union_counts = ' UNION ALL '.join([f"SELECT word, count FROM {table}" for table in tables])
        cursor.execute(f"""
            SELECT word, SUM(count) as count
            FROM ({union_counts})
            GROUP BY word
            ORDER BY count DESC
        """)
        word_data = cursor.fetchall()

        # Вставляем все слова в global_union
        insert_query = f"INSERT INTO {result_table} (word, count) VALUES (?, ?)"
        cursor.executemany(insert_query, word_data)

        # Определяем количество слов для перевода (топ N по частоте)
        total_words = len(word_data)
        words_to_translate_count = max(1, int(total_words * translation_threshold))
        frequent_words_data = word_data[:words_to_translate_count]
        frequent_words = [row[0] for row in frequent_words_data]
        
        # Создаём словарь для быстрого поиска count по слову
        word_to_count = {word: count for word, count in frequent_words_data}

        # Проверяем глобальный кэш переводов (используется всеми научными БД)
        print(f"🔍 Проверяем глобальный кэш переводов для {len(frequent_words)} слов...")
        cached_translations = get_cached_translations(frequent_words)
        cached_count = len(cached_translations)
        
        # Определяем слова, которые нужно перевести (нет в глобальном кэше)
        words_to_translate = [word for word in frequent_words if word not in cached_translations]
        new_translations = {}
        
        if words_to_translate:
            print(f"🔁 Переводим {len(words_to_translate)} новых слов (из глобального кэша: {cached_count})...")
            translations_list = translate_batch(words_to_translate)
            
            if translations_list and len(translations_list) == len(words_to_translate):
                new_translations = {
                    word: trans 
                    for word, trans in zip(words_to_translate, translations_list) 
                    if trans and trans != "—"
                }
                
                # Сохраняем новые переводы в глобальный кэш (для использования другими БД)
                save_to_global_translations_cache(new_translations)
                print(f"💾 Сохранено {len(new_translations)} переводов в глобальный кэш")
            else:
                print(f"⚠️ Количество переводов ({len(translations_list) if translations_list else 0}) не совпадает с количеством слов ({len(words_to_translate)})")
        else:
            print(f"✅ Все {cached_count} слов найдены в глобальном кэше, перевод не требуется!")

        # Объединяем кэш и новые переводы
        all_translations = {**cached_translations, **new_translations}

        # Сохраняем все переводы в локальную таблицу translations (для удобства работы с этой БД)
        # Обновляем count для слов из кэша, добавляем новые переводы
        if all_translations:
            # Удаляем старые записи для этих слов (если есть)
            words_list = list(all_translations.keys())
            placeholders = ','.join(['?'] * len(words_list))
            cursor.execute(f"DELETE FROM translations WHERE word IN ({placeholders})", words_list)
            
            # Вставляем все переводы с актуальным count
            translation_insert = "INSERT INTO translations (word, count, translation) VALUES (?, ?, ?)"
            translation_data = [
                (word, word_to_count[word], trans) 
                for word, trans in all_translations.items()
                if word in word_to_count
            ]
            if translation_data:
                cursor.executemany(translation_insert, translation_data)
                print(f"✅ Сохранено {len(translation_data)} переводов в локальную таблицу translations")
        
        total_translated = len(all_translations)
        print(f"📊 Итого: {total_translated} переводов ({cached_count} из глобального кэша, {len(new_translations)} новых)")

        conn.commit()

        total = cursor.execute(f"SELECT COUNT(*) FROM {result_table}").fetchone()[0]
        print(f"✅ Таблица '{result_table}' создана с {total} словами")
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка при создании таблицы объединения: {e}")
        conn.rollback()
        conn.close()
        return False


def get_global_translations_cache_path() -> Path:
    """
    Возвращает путь к централизованной БД кэша переводов.
    Эта БД используется всеми научными БД для переиспользования переводов.
    
    Кэш работает в ОБА направления (en→ru и ru→en), что позволяет
    переиспользовать переводы независимо от языка исходного текста.
    """
    cache_db_path = Path('database') / 'translations_cache.db'
    return cache_db_path


def init_global_translations_cache():
    """
    Инициализирует централизованную БД кэша переводов.
    Создаёт БД и таблицу, если их нет.
    
    Кэш хранит переводы в ОБА направления (en→ru и ru→en),
    что позволяет переиспользовать переводы независимо от направления.
    """
    cache_path = get_global_translations_cache_path()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sq.connect(cache_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations_cache (
            word TEXT PRIMARY KEY,
            translation TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_cache_word ON translations_cache(word)")
    
    conn.commit()
    conn.close()


def get_cached_translations(words: list, use_global_cache: bool = True) -> dict:
    """
    Получает кэшированные переводы из централизованного кэша.
    Работает для обоих направлений перевода (en→ru и ru→en),
    так как кэш хранит переводы в обе стороны.
    
    :param words: Список слов для проверки (могут быть как английские, так и русские)
    :param use_global_cache: Использовать ли глобальный кэш (по умолчанию True)
    :return: Словарь {word: translation} только для найденных слов
    """
    if not words:
        return {}
    
    if not use_global_cache:
        return {}
    
    # Инициализируем кэш, если его нет
    init_global_translations_cache()
    
    cache_path = get_global_translations_cache_path()
    conn = sq.connect(cache_path)
    cursor = conn.cursor()
    
    try:
        placeholders = ','.join(['?'] * len(words))
        cursor.execute(f"""
            SELECT word, translation 
            FROM translations_cache 
            WHERE word IN ({placeholders})
        """, words)
        
        result = {row[0]: row[1] for row in cursor.fetchall()}
    finally:
        conn.close()
    
    return result


def save_to_global_translations_cache(translations: dict):
    """
    Сохраняет переводы в централизованный кэш в ОБА направления.
    Это позволяет использовать кэш как для en→ru, так и для ru→en переводов.
    
    :param translations: Словарь {word: translation}
    """
    if not translations:
        return
    
    # Инициализируем кэш, если его нет
    init_global_translations_cache()
    
    cache_path = get_global_translations_cache_path()
    conn = sq.connect(cache_path)
    cursor = conn.cursor()
    
    try:
        # Используем INSERT OR IGNORE, чтобы не перезаписывать существующие переводы
        insert_query = "INSERT OR IGNORE INTO translations_cache (word, translation) VALUES (?, ?)"
        
        # Сохраняем переводы в ОБА направления:
        # 1. word → translation (например: "hello" → "привет")
        # 2. translation → word (например: "привет" → "hello")
        translation_data = []
        for word, trans in translations.items():
            if trans and trans != "—":
                # Прямое направление: word → translation
                translation_data.append((word, trans))
                # Обратное направление: translation → word
                translation_data.append((trans, word))
        
        if translation_data:
            cursor.executemany(insert_query, translation_data)
            conn.commit()
    finally:
        conn.close()


def get_word_with_translation(cursor, word: str, union_table: str = "global_union"):
    """
    Получает слово из global_union с переводом (если есть).
    Возвращает (word, count, translation) или None.
    """
    cursor.execute(f"""
        SELECT u.word, u.count, t.translation
        FROM {union_table} u
        LEFT JOIN translations t ON u.word = t.word
        WHERE u.word = ?
    """, (word,))
    return cursor.fetchone()



# database_operations.py — добавить функцию
def create_processed_books_table(db_name: str):
    db_path = Path('database') / f"{db_name}.db"
    with sq.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_books (
                book_path TEXT PRIMARY KEY,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                word_count INTEGER,
                hash TEXT  -- можно добавить позже для проверки изменений
            )
        """)
        con.commit()


# database_operations.py
def is_book_processed(db_name: str, book_path: str) -> bool:
    """Проверяет, была ли книга уже обработана."""
    db_path = Path('database') / f"{db_name}.db"
    try:
        with sq.connect(db_path) as con:
            cursor = con.cursor()
            cursor.execute("SELECT 1 FROM processed_books WHERE book_path = ?", (book_path,))
            return cursor.fetchone() is not None
    except:
        return False  # если таблицы нет — значит, не обрабатывалась


def mark_book_as_processed(db_name: str, book_path: str, word_count: int):
    """Добавляет запись о том, что книга обработана."""
    db_path = Path('database') / f"{db_name}.db"
    with sq.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO processed_books (book_path, word_count)
            VALUES (?, ?)
        """, (book_path, word_count))
        con.commit()
