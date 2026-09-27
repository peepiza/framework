"""Функции обработки данных об участниках групп."""
from typing import Optional


def add_member(
    members: list[dict],
    name: str,
    instrument: str,
    band_id: int,
) -> dict:
    """Добавить участника в список members."""
    new_id = max((member["id"] for member in members), default=0) + 1
    member = {
        "id": new_id,
        "name": name,
        "instrument": instrument,
        "band_id": band_id,
    }
    members.append(member)
    return member


def get_members_by_band(members: list[dict], band_id: int) -> list[dict]:
    """Вернуть всех участников указанной группы."""
    return [member for member in members if member["band_id"] == band_id]


def find_member_by_name(members: list[dict], query: str) -> Optional[dict]:
    """Найти участника по подстроке имени."""
    query_lower = query.lower()
    for member in members:
        if query_lower in member["name"].lower():
            return member
    return None


def sort_members_by_instrument(members: list[dict]) -> list[dict]:
    """Упорядочить участников по названию инструмента."""
    return sorted(members, key=lambda member: member["instrument"])
