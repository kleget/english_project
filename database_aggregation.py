# create_non_science_db.py
from termcolor import colored
from config import *
import sqlite3
from pathlib import Path
from database_operations import (
    create_intersection_table_query,
    create_union_table_query
)


def create_intersection_table(db_name, result_table: str = "word_intersection"):
    """
    Создает таблицу пересечения слов из всех таблиц БД.
    """
    db_path = Path('database') / db_name
    if '.db' not in db_name:
        db_path = Path('database') / f"{db_name}.db"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall() if row[0] not in [result_table]]

    if len(tables) < 2:
        print(colored(f"Недостаточно таблиц для пересечения: {len(tables)}", 'yellow'))
        return

    success = create_intersection_table_query(tables, db_path, result_table)
    if success:
        print(colored(f"✅ Таблица '{result_table}' успешно создана в {db_name}.", 'green'))


def create_union_table(db_name, result_table: str = "global_union"):
    """
    Создает таблицу объединения всех слов из таблиц БД.
    """
    db_path = Path('database') / db_name
    if '.db' not in db_name:
        db_path = Path('database') / f"{db_name}.db"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall() if row[0] not in [result_table, "word_intersection"]]

    if not tables:
        print(colored("Нет таблиц для объединения.", 'yellow'))
        return

    success = create_union_table_query(tables, db_path, result_table)
    if success:
        print(colored(f"✅ Таблица '{result_table}' успешно создана в {db_name}.", 'green'))


if __name__ == "__main__":
    print("=== Обработка biology.db ===")
    create_intersection_table('biology.db')
    create_union_table('biology.db')
