from config import *
import sqlite3 as sq
import os
import difflib
from database_operations import *


def similarity(s1, s2):
  matcher = difflib.SequenceMatcher(None, s1, s2)
  return matcher.ratio()

def select_all_tables(n):
    with sq.connect(f"database/{n}.db") as con:
        sql = con.cursor()
        sql.execute("SELECT name FROM sqlite_sequence;")
        return sql.fetchall()

def select_all_data_from_tables(db, name):
    with sq.connect(f"database/{db}.db") as con:
        sql = con.cursor()
        sql.execute(f"SELECT word FROM {name};")
        return sql.fetchall()


# for n in ['ennonscience', 'runonscience']:
#     tables_names = list(map(str, [x[0] for x in select_all_tables(n)]))

#     words = [] # все слова из всех таблиц

#     for table in tables_names:
#         # word = set(x[0] for x in select_all_data_from_tables(table))
#         word = set(select_all_data_from_tables(n, table)) # чтобы все были уникальными
#         # words.append(x for x in word)
#         for x in word:
#             words.append(x)
#         print(f"{table}: {len(word)}")


#     print(len(set(words)))

    
#     insert_many_into_table('all_non_science', n, list(set(words)))

###########################################
import sqlite3
import logging
from pathlib import Path


import sqlite3
import logging
from pathlib import Path

def create_intersection_table(db_name, result_table: str = "word_intersection"):
    """
    Создает таблицу с пересечением слов из всех таблиц БД и суммирует их частоты
    
    :param db_name: имя файла базы данных
    :param result_table: имя результирующей таблицы
    """
    # Путь к базе данных
    db_path = Path('database') / db_name
    
    if not db_path.exists():
        logging.error(f"Файл базы данных {db_path} не найден!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Получаем список всех таблиц (исключая системные)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall() if row[0] != result_table]
        
        if len(tables) < 2:
            logging.warning(f"Нужно минимум 2 таблицы, найдено {len(tables)}")
            return
        
        logging.info(f"Обрабатываем таблицы: {', '.join(tables)}")
        
        # Удаляем старую версию результирующей таблицы
        cursor.execute(f"DROP TABLE IF EXISTS {result_table}")
        
        # 1. Сначала находим слова, которые есть во всех таблицах
        intersection_words_query = f"""
        SELECT word FROM (
            SELECT word, COUNT(DISTINCT src) as cnt FROM (
                { ' UNION ALL '.join([f"SELECT word, '{table}' as src FROM {table}" for table in tables]) }
            ) GROUP BY word HAVING cnt = {len(tables)}
        )"""
        
        # 2. Затем суммируем count для этих слов из всех таблиц
        sum_counts_query = f"""
        CREATE TABLE {result_table} AS
        SELECT 
            t.word,
            SUM(t.count) as total_count
        FROM (
            { ' UNION ALL '.join([f"SELECT word, count FROM {table}" for table in tables]) }
        ) t
        WHERE t.word IN ({intersection_words_query})
        GROUP BY t.word
        ORDER BY total_count DESC;
        """
        
        cursor.execute(sum_counts_query)
        conn.commit()
        
        # Проверяем результат
        result = cursor.execute(f"SELECT word, total_count FROM {result_table} ORDER BY total_count DESC LIMIT 5").fetchall()
        total_words = cursor.execute(f"SELECT COUNT(*) FROM {result_table}").fetchone()[0]
        
        logging.info(f"Создана таблица {result_table} с {total_words} словами")
        logging.info("Топ-5 самых частых слов:")
        for word, count in result:
            logging.info(f"{word}: {count}")
            
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.info("=== Обработка biology.db ===")
    create_intersection_table('biology.db')