"""Тесты функций работы с репетициями."""
from datetime import date

from bands import add_band
from rooms import add_room
from rehearsals import (
    is_room_available,
    is_band_free,
    create_rehearsal,
    cancel_rehearsal,
    get_rehearsal_status,
)


def test_is_room_available_empty():
    assert is_room_available([], 1, date(2026, 9, 15))


def test_duplicate_rehearsal_forbidden():
    rehearsals = []
    bands = []
    rooms = []
    add_band(bands, "Рок-группа «Эхо»", "рок", 5)
    add_room(rooms, "Ритм", 10, "ул. Ленина, 5")
    create_rehearsal(
        rehearsals, bands, rooms, 1, 1, date(2026, 9, 15), "19:00"
    )
    assert not is_room_available(
        rehearsals, 1, date(2026, 9, 15)
    )
    assert not is_band_free(rehearsals, 1, date(2026, 9, 15))


def test_cancel_rehearsal():
    rehearsals = [{"id": 1, "band_id": 1, "room_id": 1,
                   "rehearsal_date": "2026-09-15", "start_time": "19:00"}]
    assert cancel_rehearsal(rehearsals, 1)
    assert rehearsals == []


def test_get_rehearsal_status():
    assert get_rehearsal_status(True) == (
        "Помещение доступно для бронирования"
    )
    assert get_rehearsal_status(False) == "Помещение уже занято"
