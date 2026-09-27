"""Класс Rehearsal и функции работы с репетициями."""
from datetime import date
from typing import Optional

from models.bands import Band
from models.rooms import Room


class Rehearsal:
    """Запланированная репетиция группы в помещении."""

    def __init__(
        self,
        rehearsal_id: int,
        band: Band,
        room: Room,
        rehearsal_date: str,
        start_time: str,
    ) -> None:
        """Создать объект репетиции."""
        self.id = rehearsal_id
        self.band = band
        self.room = room
        self.rehearsal_date = rehearsal_date
        self.start_time = start_time
        self.is_cancelled = False

    def cancel(self) -> None:
        """Отменить репетицию."""
        self.is_cancelled = True

    def __str__(self) -> str:
        """Строковое представление репетиции."""
        status = "отменена" if self.is_cancelled else "активна"
        return (
            f"[{self.id}] {self.band.name} | "
            f"{self.room.name} | "
            f"{self.rehearsal_date} {self.start_time} | "
            f"{status}"
        )

    @classmethod
    def from_data(
        cls,
        data: dict,
        bands: list[Band],
        rooms: list[Room],
    ) -> Optional["Rehearsal"]:
        """Создать репетицию из словаря JSON с поиском связанных объектов."""
        band = next(
            (b for b in bands if b.id == data["band_id"]),
            None,
        )
        room = next(
            (r for r in rooms if r.id == data["room_id"]),
            None,
        )
        if band is None or room is None:
            return None
        rehearsal = cls(
            rehearsal_id=data["id"],
            band=band,
            room=room,
            rehearsal_date=data["rehearsal_date"],
            start_time=data["start_time"],
        )
        rehearsal.is_cancelled = data.get("is_cancelled", False)
        return rehearsal


def is_room_available(
    rehearsals: list[Rehearsal],
    room: Room,
    rehearsal_date: date,
) -> bool:
    """Проверить, свободно ли помещение на дату."""
    date_str = rehearsal_date.isoformat()
    for rehearsal in rehearsals:
        if rehearsal.is_cancelled:
            continue
        if (
            rehearsal.room.id == room.id
            and rehearsal.rehearsal_date == date_str
        ):
            return False
    return True


def is_band_free(
    rehearsals: list[Rehearsal],
    band: Band,
    rehearsal_date: date,
) -> bool:
    """Проверить, свободна ли группа на дату."""
    date_str = rehearsal_date.isoformat()
    for rehearsal in rehearsals:
        if rehearsal.is_cancelled:
            continue
        if (
            rehearsal.band.id == band.id
            and rehearsal.rehearsal_date == date_str
        ):
            return False
    return True


def create_rehearsal(
    rehearsals: list[Rehearsal],
    band: Band,
    room: Room,
    rehearsal_date: date,
    start_time: str,
) -> Optional[Rehearsal]:
    """Создать репетицию с проверками."""
    if not room.is_suitable_for(band.members_count):
        print("Помещение недостаточно вместительное.")
        return None
    if not is_room_available(rehearsals, room, rehearsal_date):
        print("Помещение занято на эту дату.")
        return None
    if not is_band_free(rehearsals, band, rehearsal_date):
        print("У группы уже есть репетиция на эту дату.")
        return None

    new_id = max(
        (rehearsal.id for rehearsal in rehearsals), default=0
    ) + 1
    rehearsal = Rehearsal(
        rehearsal_id=new_id,
        band=band,
        room=room,
        rehearsal_date=rehearsal_date.isoformat(),
        start_time=start_time,
    )
    rehearsals.append(rehearsal)
    return rehearsal


def cancel_rehearsal(
    rehearsals: list[Rehearsal],
    rehearsal_id: int,
) -> bool:
    """Отменить репетицию по идентификатору."""
    for rehearsal in rehearsals:
        if rehearsal.id == rehearsal_id:
            rehearsal.cancel()
            return True
    return False


def get_rehearsal_status(is_available: bool) -> str:
    """Вернуть текстовый статус помещения (функция из ПР1)."""
    if is_available:
        return "Помещение доступно для бронирования"
    return "Помещение уже занято"
