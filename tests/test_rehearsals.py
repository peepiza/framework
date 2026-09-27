"""Тесты класса Rehearsal и функций работы с репетициями."""
from datetime import date

from models import Band, Room
from models.rehearsals import (
    is_room_available,
    is_band_free,
    create_rehearsal,
    cancel_rehearsal,
    get_rehearsal_status,
)


def test_rehearsal_creation():
    band = Band(1, "Рок-группа «Эхо»", "рок", 5)
    room = Room(1, "Ритм", 10, "ул. Ленина, 5")
    rehearsals = []
    rehearsal = create_rehearsal(
        rehearsals, band, room, date(2026, 9, 15), "19:00"
    )
    assert rehearsal is not None
    assert rehearsal.band is band
    assert rehearsal.room is room
    assert rehearsal.rehearsal_date == "2026-09-15"
    assert rehearsal.is_cancelled is False


def test_duplicate_rehearsal_forbidden():
    band = Band(1, "Рок-группа «Эхо»", "рок", 5)
    room = Room(1, "Ритм", 10, "ул. Ленина, 5")
    rehearsals = []
    create_rehearsal(
        rehearsals, band, room, date(2026, 9, 15), "19:00"
    )
    assert not is_room_available(
        rehearsals, room, date(2026, 9, 15)
    )
    assert not is_band_free(rehearsals, band, date(2026, 9, 15))


def test_cancel_rehearsal():
    band = Band(1, "Рок-группа «Эхо»", "рок", 5)
    room = Room(1, "Ритм", 10, "ул. Ленина, 5")
    rehearsals = []
    create_rehearsal(
        rehearsals, band, room, date(2026, 9, 15), "19:00"
    )
    assert cancel_rehearsal(rehearsals, 1)
    assert rehearsals[0].is_cancelled
    assert is_room_available(
        rehearsals, room, date(2026, 9, 15)
    )


def test_room_too_small():
    band = Band(1, "Рок-группа «Эхо»", "рок", 20)
    room = Room(1, "Малая", 5, "ул. Ленина, 5")
    rehearsals = []
    rehearsal = create_rehearsal(
        rehearsals, band, room, date(2026, 9, 15), "19:00"
    )
    assert rehearsal is None
    assert rehearsals == []


def test_get_rehearsal_status():
    assert get_rehearsal_status(True) == (
        "Помещение доступно для бронирования"
    )
    assert get_rehearsal_status(False) == "Помещение уже занято"
