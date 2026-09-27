"""Функции обработки данных о музыкальных группах."""
from typing import Optional


def add_band(
    bands: list[dict],
    name: str,
    genre: str,
    members_count: int,
) -> dict:
    """Добавить музыкальную группу в список bands."""
    new_id = max((band["id"] for band in bands), default=0) + 1
    band = {
        "id": new_id,
        "name": name,
        "genre": genre,
        "members_count": members_count,
    }
    bands.append(band)
    return band


def find_band(bands: list[dict], query: str) -> Optional[dict]:
    """Найти группу по подстроке названия (без учёта регистра)."""
    query_lower = query.lower()
    for band in bands:
        if query_lower in band["name"].lower():
            return band
    return None


def get_band_by_id(bands: list[dict], band_id: int) -> Optional[dict]:
    """Найти группу по идентификатору."""
    for band in bands:
        if band["id"] == band_id:
            return band
    return None


def filter_bands_by_size(bands: list[dict], min_size: int) -> list[dict]:
    """Отобрать группы с числом участников не меньше min_size."""
    return [band for band in bands if band["members_count"] >= min_size]


def sort_bands(bands: list[dict]) -> list[dict]:
    """Вернуть группы, упорядоченные по числу участников."""
    return sorted(bands, key=lambda band: band["members_count"])
