from config import *
import sqlite3 as sq

def create_table(db_name: str, table_name: str):
    if '.db' not in db_name: db_name += '.db'
    with sq.connect(f"database/{db_name}") as con:
        sql = con.cursor()
        sql.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL, count INTEGER NOT NULL);")
        con.commit()


def insert_many_into_table(db_name: str, table_name: str, sorted_analysand: list):
    if '.db' not in db_name: db_name += '.db'
    with sq.connect(f"database/{db_name}") as con:
        sql = con.cursor()
        for word, value in sorted_analysand:
            sql.execute(f"INSERT INTO {table_name} (word, count) VALUES (?, ?) ", (word, value,))
        con.commit()


def select_from_table(db_name: str, request: str):
    if '.db' not in db_name: db_name += '.db'
    with sq.connect(f"database/{db_name}") as con:
        sql = con.cursor()
        sql.execute(request)
        return sql.fetchall()