"""Сохранение и загрузка данных проекта в JSON-файлах."""
import json
import os
from typing import Any


def _load_json(filename: str, default: Any) -> Any:
    """Загрузить данные из JSON-файла.

    При отсутствии файла или некорректном JSON
    возвращается значение по умолчанию.
    """
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"Ошибка чтения {filename}: {error}")
        return default


def _save_json(filename: str, data: Any) -> None:
    """Сохранить данные в JSON-файл с отступами."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Ошибка записи {filename}: {error}")


def load_bands(filename: str) -> list[dict]:
    """Загрузить список групп из JSON-файла."""
    return _load_json(filename, [])


def save_bands(filename: str, bands: list[dict]) -> None:
    """Сохранить список групп в JSON-файл."""
    _save_json(filename, bands)


def load_members(filename: str) -> list[dict]:
    """Загрузить список участников из JSON-файла."""
    return _load_json(filename, [])


def save_members(filename: str, members: list[dict]) -> None:
    """Сохранить список участников в JSON-файл."""
    _save_json(filename, members)


def load_rooms(filename: str) -> list[dict]:
    """Загрузить список помещений из JSON-файла."""
    return _load_json(filename, [])


def save_rooms(filename: str, rooms: list[dict]) -> None:
    """Сохранить список помещений в JSON-файл."""
    _save_json(filename, rooms)


def load_rehearsals(filename: str) -> list[dict]:
    """Загрузить список репетиций из JSON-файла."""
    return _load_json(filename, [])


def save_rehearsals(filename: str, rehearsals: list[dict]) -> None:
    """Сохранить список репетиций в JSON-файл."""
    _save_json(filename, rehearsals)
