"""Класс Room и функции работы с помещениями."""
from typing import Optional


class Room:
    """Помещение для репетиций."""

    def __init__(
        self,
        room_id: int,
        name: str,
        capacity: int,
        address: str,
    ) -> None:
        """Создать объект помещения."""
        self.id = room_id
        self.name = name
        self.capacity = capacity
        self.address = address

    def __str__(self) -> str:
        """Строковое представление помещения."""
        return (
            f"[{self.id}] {self.name} | "
            f"вместимость: {self.capacity} | "
            f"адрес: {self.address}"
        )

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить, вмещает ли помещение указанное число людей."""
        return self.capacity >= people_count

    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """Проверить корректность значения вместимости."""
        return capacity > 0

    @classmethod
    def from_data(cls, data: dict) -> "Room":
        """Создать помещение из словаря JSON."""
        return cls(
            room_id=data["id"],
            name=data["name"],
            capacity=data["capacity"],
            address=data["address"],
        )


def add_room(
    rooms: list[Room],
    name: str,
    capacity: int,
    address: str,
) -> Room:
    """Создать помещение и добавить его в коллекцию."""
    new_id = max((room.id for room in rooms), default=0) + 1
    room = Room(new_id, name, capacity, address)
    rooms.append(room)
    return room


def find_room(rooms: list[Room], query: str) -> Optional[Room]:
    """Найти помещение по подстроке названия."""
    query_lower = query.lower()
    for room in rooms:
        if query_lower in room.name.lower():
            return room
    return None


def get_room_by_id(
    rooms: list[Room],
    room_id: int,
) -> Optional[Room]:
    """Найти помещение по идентификатору."""
    for room in rooms:
        if room.id == room_id:
            return room
    return None


def check_room_capacity(
    rooms: list[Room],
    room_id: int,
    min_capacity: int,
) -> bool:
    """Проверить вместимость помещения через метод объекта."""
    room = get_room_by_id(rooms, room_id)
    if room is None:
        return False
    return room.is_suitable_for(min_capacity)


def filter_rooms_by_capacity(
    rooms: list[Room],
    min_capacity: int,
) -> list[Room]:
    """Отобрать помещения по вместимости."""
    return [
        room for room in rooms if room.is_suitable_for(min_capacity)
    ]


def sort_rooms(rooms: list[Room]) -> list[Room]:
    """Упорядочить помещения по вместимости."""
    return sorted(rooms, key=lambda room: room.capacity)
