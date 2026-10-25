-- =============================================
-- Структура базы данных «Сервис планирования репетиций»
-- =============================================

CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    address TEXT
);

CREATE TABLE IF NOT EXISTS bands (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    genre TEXT NOT NULL,
    members_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rehearsals (
    id INTEGER PRIMARY KEY,
    band_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    rehearsal_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (band_id) REFERENCES bands(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);