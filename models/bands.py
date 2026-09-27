"""Класс Band и функции работы с группами."""
from typing import Optional


class Band:
    """Музыкальная группа."""

    def __init__(
        self,
        band_id: int,
        name: str,
        genre: str,
        members_count: int,
    ) -> None:
        """Создать объект группы."""
        self.id = band_id
        self.name = name
        self.genre = genre
        self.members_count = members_count

    def __str__(self) -> str:
        """Строковое представление группы."""
        return (
            f"[{self.id}] {self.name} | "
            f"жанр: {self.genre} | "
            f"участников: {self.members_count}"
        )

    @classmethod
    def from_data(cls, data: dict) -> "Band":
        """Создать группу из словаря JSON."""
        return cls(
            band_id=data["id"],
            name=data["name"],
            genre=data["genre"],
            members_count=data["members_count"],
        )


def add_band(
    bands: list[Band],
    name: str,
    genre: str,
    members_count: int,
) -> Band:
    """Создать группу и добавить её в коллекцию."""
    new_id = max((band.id for band in bands), default=0) + 1
    band = Band(new_id, name, genre, members_count)
    bands.append(band)
    return band


def find_band(bands: list[Band], query: str) -> Optional[Band]:
    """Найти группу по подстроке названия."""
    query_lower = query.lower()
    for band in bands:
        if query_lower in band.name.lower():
            return band
    return None


def get_band_by_id(
    bands: list[Band],
    band_id: int,
) -> Optional[Band]:
    """Найти группу по идентификатору."""
    for band in bands:
        if band.id == band_id:
            return band
    return None


def filter_bands_by_size(
    bands: list[Band],
    min_size: int,
) -> list[Band]:
    """Отобрать группы по числу участников."""
    return [band for band in bands if band.members_count >= min_size]


def sort_bands(bands: list[Band]) -> list[Band]:
    """Упорядочить группы по числу участников."""
    return sorted(bands, key=lambda band: band.members_count)
