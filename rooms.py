"""Функции обработки данных о помещениях."""
from typing import Optional


def add_room(
    rooms: list[dict],
    name: str,
    capacity: int,
    address: str,
) -> dict:
    """Добавить помещение в список rooms."""
    new_id = max((room["id"] for room in rooms), default=0) + 1
    room = {
        "id": new_id,
        "name": name,
        "capacity": capacity,
        "address": address,
    }
    rooms.append(room)
    return room


def find_room(rooms: list[dict], query: str) -> Optional[dict]:
    """Найти помещение по подстроке названия."""
    query_lower = query.lower()
    for room in rooms:
        if query_lower in room["name"].lower():
            return room
    return None


def get_room_by_id(rooms: list[dict], room_id: int) -> Optional[dict]:
    """Найти помещение по идентификатору."""
    for room in rooms:
        if room["id"] == room_id:
            return room
    return None


def check_room_capacity(
    rooms: list[dict],
    room_id: int,
    min_capacity: int,
) -> bool:
    """Проверить, вмещает ли помещение не меньше min_capacity человек."""
    room = get_room_by_id(rooms, room_id)
    if room is None:
        return False
    return room["capacity"] >= min_capacity


def filter_rooms_by_capacity(
    rooms: list[dict],
    min_capacity: int,
) -> list[dict]:
    """Отобрать помещения с вместимостью не меньше min_capacity."""
    return [
        room for room in rooms if room["capacity"] >= min_capacity
    ]


def sort_rooms(rooms: list[dict]) -> list[dict]:
    """Упорядочить помещения по вместимости."""
    return sorted(rooms, key=lambda room: room["capacity"])
