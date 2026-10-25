"""Модуль подключения к базе данных SQLite."""
import sqlite3

DB_PATH = "data/rehearsal_planner.sqlite"

def get_connection():
    """Создать соединение с базой данных и включить внешние ключи."""
    conn = sqlite3.connect(DB_PATH)
    # Включаем проверку внешних ключей (по умолчанию в SQLite они выключены)
    conn.execute("PRAGMA foreign_keys = ON")
    # Позволяет обращаться к полям результата по именам (row['name'])
    conn.row_factory = sqlite3.Row
    return conn