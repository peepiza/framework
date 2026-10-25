"""Скрипт переноса данных из JSON-файлов в базу данных SQLite."""
import json
from db.database import get_connection

ROOMS_FILE = "data/rooms.json"
BANDS_FILE = "data/bands.json"
REHEARSALS_FILE = "data/rehearsals.json"

def load_json(filename):
    with open(filename, encoding="utf-8") as file:
        return json.load(file)

def import_data(conn):
    """Загружает данные из JSON и вставляет их в таблицы."""
    rooms = load_json(ROOMS_FILE)
    bands = load_json(BANDS_FILE)
    rehearsals = load_json(REHEARSALS_FILE)

    # 1. Импорт помещений
    conn.executemany(
        "INSERT INTO rooms (id, name, capacity, address) VALUES (?, ?, ?, ?)",
        [(r["id"], r["name"], r["capacity"], r.get("address", "")) for r in rooms]
    )

    # 2. Импорт групп
    conn.executemany(
        "INSERT INTO bands (id, name, genre, members_count) VALUES (?, ?, ?, ?)",
        [(b["id"], b["name"], b["genre"], b["members_count"]) for b in bands]
    )

    # 3. Импорт репетиций
    conn.executemany(
        """INSERT INTO rehearsals (id, band_id, room_id, rehearsal_date, start_time, is_cancelled)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [(
            r["id"], r["band_id"], r["room_id"],
            r["rehearsal_date"], r["start_time"],
            int(r.get("is_cancelled", False)) # bool в Python -> 0/1 в SQLite
        ) for r in rehearsals]
    )

def main():
    conn = get_connection()
    try:
        print("Очистка старых данных...")
        conn.execute("DELETE FROM rehearsals")
        conn.execute("DELETE FROM bands")
        conn.execute("DELETE FROM rooms")
        
        print("Импорт данных...")
        import_data(conn)
        conn.commit()
        print("Импорт успешно завершен!")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при импорте: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()