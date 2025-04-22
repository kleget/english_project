from config import *
import sqlite3 as sq
import os

# def create_table(db_name: str, table_name: str):
#     if not os.path.exists('database'):
#         os.makedirs('database')
#     if '.db' not in db_name: db_name += '.db'
#     with sq.connect(f"database/{db_name}") as con:
#         sql = con.cursor()
#         sql.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL, count INTEGER NOT NULL);")
#         con.commit()
#
#
# def insert_many_into_table(db_name: str, table_name: str, sorted_analysand: list):
#     if '.db' not in db_name: db_name += '.db'
#     create_table(db_name, table_name) # чтобы не произошло такого, что мы записываем в таблицу или файл, которого нет
#     with sq.connect(f"database/{db_name}") as con:
#         sql = con.cursor()
#         print(f"{db_name}_{table_name}")
#         for word, value in sorted_analysand:
#             sql.execute(f"INSERT INTO {table_name} (word, count) VALUES (?, ?) ", (word, value,))
#         con.commit()

def create_table(db_name: str, table_name: str):
    if not os.path.exists('database'):
        os.makedirs('database')
    if '.db' not in db_name:
        db_name += '.db'

    # Определяем схему таблицы
    if table_name == 'from_all_files':
        schema = """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deleted_word TEXT NOT NULL,
            count INTEGER NOT NULL,
            merged_to TEXT NOT NULL
        """
    else:
        schema = """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            count INTEGER NOT NULL
        """

    with sq.connect(f"database/{db_name}") as con:
        sql = con.cursor()
        sql.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
        con.commit()


def insert_many_into_table(db_name: str, table_name: str, data: list):
    if '.db' not in db_name:
        db_name += '.db'
    create_table(db_name, table_name)

    # Определяем колонки и формат вставки
    if table_name == 'from_all_files':
        columns = ('deleted_word', 'count', 'merged_to')
        query = f"INSERT INTO {table_name} {columns} VALUES (?, ?, ?)"
    else:
        columns = ('word', 'count')
        query = f"INSERT INTO {table_name} {columns} VALUES (?, ?)"

    with sq.connect(f"database/{db_name}") as con:
        sql = con.cursor()
        # Преобразуем все элементы в кортежи
        formatted_data = [tuple(item) for item in data]
        sql.executemany(query, formatted_data)
        con.commit()


def select_from_table(db_name: str, request: str):
    if '.db' not in db_name: db_name += '.db'
    with sq.connect(f"database/{db_name}") as con:
        sql = con.cursor()
        sql.execute(request)
        return sql.fetchall()



