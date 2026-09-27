"""Тесты класса Room и функций работы с помещениями."""
from models import Room
from models.rooms import (
    add_room,
    find_room,
    check_room_capacity,
    sort_rooms,
)


def test_room_creation():
    room = Room(1, "Ритм", 10, "ул. Ленина, 5")
    assert room.id == 1
    assert room.name == "Ритм"
    assert room.capacity == 10
    assert room.address == "ул. Ленина, 5"


def test_room_is_suitable_for():
    room = Room(1, "Ритм", 10, "ул. Ленина, 5")
    assert room.is_suitable_for(5)
    assert not room.is_suitable_for(20)


def test_add_room():
    rooms = []
    add_room(rooms, "Студия «Звук»", 20, "пр. Мира, 12")
    assert len(rooms) == 1
    assert isinstance(rooms[0], Room)


def test_find_room():
    rooms = []
    add_room(rooms, "Студия «Звук»", 20, "пр. Мира, 12")
    assert find_room(rooms, "звук") is not None


def test_check_room_capacity():
    rooms = []
    add_room(rooms, "Студия «Звук»", 20, "пр. Мира, 12")
    assert check_room_capacity(rooms, 1, 10)
    assert not check_room_capacity(rooms, 1, 30)


def test_sort_rooms():
    rooms = []
    add_room(rooms, "Большая", 50, "A")
    add_room(rooms, "Малая", 10, "B")
    sorted_rooms = sort_rooms(rooms)
    assert sorted_rooms[0].capacity == 10
