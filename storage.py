"""Сохранение и загрузка данных проекта в JSON-файлах."""
import json
import os
from typing import Any

from models.bands import Band
from models.members import Member
from models.rooms import Room
from models.rehearsals import Rehearsal


def _load_json(filename: str, default: Any) -> Any:
    """Загрузить данные из JSON-файла с обработкой ошибок."""
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"Ошибка чтения {filename}: {error}")
        return default


def _save_json(filename: str, data: Any) -> None:
    """Сохранить данные в JSON-файл."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Ошибка записи {filename}: {error}")


def load_bands(filename: str) -> list[Band]:
    """Загрузить группы из JSON и вернуть объекты Band."""
    raw = _load_json(filename, [])
    return [Band.from_data(item) for item in raw]


def save_bands(filename: str, bands: list[Band]) -> None:
    """Сохранить объекты Band в JSON."""
    data = [
        {
            "id": band.id,
            "name": band.name,
            "genre": band.genre,
            "members_count": band.members_count,
        }
        for band in bands
    ]
    _save_json(filename, data)


def load_members(filename: str) -> list[Member]:
    """Загрузить участников из JSON и вернуть объекты Member."""
    raw = _load_json(filename, [])
    return [Member.from_data(item) for item in raw]


def save_members(filename: str, members: list[Member]) -> None:
    """Сохранить объекты Member в JSON."""
    data = [
        {
            "id": member.id,
            "name": member.name,
            "instrument": member.instrument,
            "band_id": member.band_id,
        }
        for member in members
    ]
    _save_json(filename, data)


def load_rooms(filename: str) -> list[Room]:
    """Загрузить помещения из JSON и вернуть объекты Room."""
    raw = _load_json(filename, [])
    return [Room.from_data(item) for item in raw]


def save_rooms(filename: str, rooms: list[Room]) -> None:
    """Сохранить объекты Room в JSON."""
    data = [
        {
            "id": room.id,
            "name": room.name,
            "capacity": room.capacity,
            "address": room.address,
        }
        for room in rooms
    ]
    _save_json(filename, data)


def load_rehearsals(
    filename: str,
    bands: list[Band],
    rooms: list[Room],
) -> list[Rehearsal]:
    """Загрузить репетиции из JSON с восстановлением связей."""
    raw = _load_json(filename, [])
    rehearsals = []
    for item in raw:
        rehearsal = Rehearsal.from_data(item, bands, rooms)
        if rehearsal is not None:
            rehearsals.append(rehearsal)
    return rehearsals


def save_rehearsals(
    filename: str,
    rehearsals: list[Rehearsal],
) -> None:
    """Сохранить объекты Rehearsal в JSON (с id связанных объектов)."""
    data = [
        {
            "id": rehearsal.id,
            "band_id": rehearsal.band.id,
            "room_id": rehearsal.room.id,
            "rehearsal_date": rehearsal.rehearsal_date,
            "start_time": rehearsal.start_time,
            "is_cancelled": rehearsal.is_cancelled,
        }
        for rehearsal in rehearsals
    ]
    _save_json(filename, data)
