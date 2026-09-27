"""Тесты функций работы с помещениями."""
from rooms import (
    add_room,
    find_room,
    check_room_capacity,
    sort_rooms,
)


def test_add_room():
    rooms = []
    add_room(rooms, "Репетиционная база «Ритм»", 10, "ул. Ленина, 5")
    assert len(rooms) == 1


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
    assert sorted_rooms[0]["capacity"] == 10
