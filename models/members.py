"""Класс Member и функции работы с участниками."""
from typing import Optional


class Member:
    """Участник музыкальной группы."""

    def __init__(
        self,
        member_id: int,
        name: str,
        instrument: str,
        band_id: int,
    ) -> None:
        """Создать объект участника."""
        self.id = member_id
        self.name = name
        self.instrument = instrument
        self.band_id = band_id

    def __str__(self) -> str:
        """Строковое представление участника."""
        return f"{self.name} — {self.instrument}"

    @classmethod
    def from_data(cls, data: dict) -> "Member":
        """Создать участника из словаря JSON."""
        return cls(
            member_id=data["id"],
            name=data["name"],
            instrument=data["instrument"],
            band_id=data["band_id"],
        )


def add_member(
    members: list[Member],
    name: str,
    instrument: str,
    band_id: int,
) -> Member:
    """Создать участника и добавить в коллекцию."""
    new_id = max((member.id for member in members), default=0) + 1
    member = Member(new_id, name, instrument, band_id)
    members.append(member)
    return member


def get_members_by_band(
    members: list[Member],
    band_id: int,
) -> list[Member]:
    """Вернуть всех участников указанной группы."""
    return [member for member in members if member.band_id == band_id]


def find_member_by_name(
    members: list[Member],
    query: str,
) -> Optional[Member]:
    """Найти участника по подстроке имени."""
    query_lower = query.lower()
    for member in members:
        if query_lower in member.name.lower():
            return member
    return None


def sort_members_by_instrument(
    members: list[Member],
) -> list[Member]:
    """Упорядочить участников по инструменту."""
    return sorted(members, key=lambda member: member.instrument)
