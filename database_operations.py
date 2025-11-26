# database_operations.py
from config import *
import sqlite3 as sq
import os
from pathlib import Path


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
        formatted_data = [tuple(item) for item in data]
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
                SUM(t.count) as total_count
            FROM ({union_counts}) t
            WHERE t.word IN ({intersection_words})
            GROUP BY t.word
            ORDER BY total_count DESC
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



def create_union_table_query(tables, db_path: Path, result_table: str = "global_union"):
    """
    Выполняет создание таблицы объединения в указанной БД.
    """
    if not db_path.exists():
        print(f"Файл базы данных {db_path} не найден!")
        return False

    try:
        conn = sq.connect(db_path)
        cursor = conn.cursor()

        # Удаляем старую таблицу
        cursor.execute(f"DROP TABLE IF EXISTS {result_table}")

        # Создаём новую с колонкой translation
        cursor.execute(f"""
            CREATE TABLE {result_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                total_count INTEGER NOT NULL,
                translation TEXT
            )
        """)

        # Собираем и суммируем все слова
        union_counts = ' UNION ALL '.join([f"SELECT word, count FROM {table}" for table in tables])
        cursor.execute(f"""
            SELECT word, SUM(count) as total_count
            FROM ({union_counts})
            GROUP BY word
            ORDER BY total_count DESC
        """)
        word_data = cursor.fetchall()

        # Извлекаем слова
        words = [row[0] for row in word_data]

        # Переводим
        from translation_utils import translate_batch
        print(f"🔁 Начинаем перевод {len(words)} слов...")
        translations = translate_batch(words)

        # Вставляем в таблицу
        insert_query = f"INSERT INTO {result_table} (word, total_count, translation) VALUES (?, ?, ?)"
        for (word, count), translation in zip(word_data, translations):
            cursor.execute(insert_query, (word, count, translation))

        conn.commit()

        total = cursor.execute(f"SELECT COUNT(*) FROM {result_table}").fetchone()[0]
        print(f"✅ Таблица '{result_table}' создана. Слов с переводами: {total}")
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка при создании таблицы объединения: {e}")
        conn.rollback()
        conn.close()
        return False
