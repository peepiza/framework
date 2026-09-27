"""Функции работы с репетициями.

Содержит функцию get_rehearsal_status(), перенесённую из ПР1.
"""
from datetime import date
from typing import Optional


def is_room_available(
    rehearsals: list[dict],
    room_id: int,
    rehearsal_date: date,
) -> bool:
    """Проверить, свободно ли помещение на указанную дату."""
    date_str = rehearsal_date.isoformat()
    for rehearsal in rehearsals:
        if (
            rehearsal["room_id"] == room_id
            and rehearsal["rehearsal_date"] == date_str
        ):
            return False
    return True


def is_band_free(
    rehearsals: list[dict],
    band_id: int,
    rehearsal_date: date,
) -> bool:
    """Проверить, свободна ли группа на указанную дату."""
    date_str = rehearsal_date.isoformat()
    for rehearsal in rehearsals:
        if (
            rehearsal["band_id"] == band_id
            and rehearsal["rehearsal_date"] == date_str
        ):
            return False
    return True


def create_rehearsal(
    rehearsals: list[dict],
    bands: list[dict],
    rooms: list[dict],
    band_id: int,
    room_id: int,
    rehearsal_date: date,
    start_time: str,
) -> Optional[dict]:
    """Создать репетицию с проверками.

    Проверяет:
    - существование группы и помещения;
    - вместимость помещения;
    - доступность помещения и группы на дату.
    Возвращает созданную запись или None.
    """
    from bands import get_band_by_id
    from rooms import get_room_by_id, check_room_capacity

    band = get_band_by_id(bands, band_id)
    room = get_room_by_id(rooms, room_id)

    if band is None:
        print("Группа не найдена.")
        return None
    if room is None:
        print("Помещение не найдено.")
        return None
    if not check_room_capacity(rooms, room_id, band["members_count"]):
        print("Помещение недостаточно вместительное.")
        return None
    if not is_room_available(rehearsals, room_id, rehearsal_date):
        print("Помещение занято на эту дату.")
        return None
    if not is_band_free(rehearsals, band_id, rehearsal_date):
        print("У группы уже есть репетиция на эту дату.")
        return None

    new_id = max(
        (rehearsal["id"] for rehearsal in rehearsals), default=0
    ) + 1
    rehearsal = {
        "id": new_id,
        "band_id": band_id,
        "room_id": room_id,
        "rehearsal_date": rehearsal_date.isoformat(),
        "start_time": start_time,
    }
    rehearsals.append(rehearsal)
    return rehearsal


def cancel_rehearsal(
    rehearsals: list[dict],
    rehearsal_id: int,
) -> bool:
    """Отменить репетицию по идентификатору."""
    for rehearsal in rehearsals:
        if rehearsal["id"] == rehearsal_id:
            rehearsals.remove(rehearsal)
            return True
    return False


def get_rehearsal_status(is_available: bool) -> str:
    """Вернуть текстовый статус репетиции (функция из ПР1)."""
    if is_available:
        return "Помещение доступно для бронирования"
    return "Помещение уже занято"
