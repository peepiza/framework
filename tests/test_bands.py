"""Тесты функций работы с группами."""
from bands import (
    add_band,
    find_band,
    filter_bands_by_size,
    sort_bands,
)


def test_add_band():
    bands = []
    add_band(bands, "Рок-группа «Эхо»", "рок", 5)
    assert len(bands) == 1
    assert bands[0]["name"] == "Рок-группа «Эхо»"


def test_find_band():
    bands = []
    add_band(bands, "Рок-группа «Эхо»", "рок", 5)
    assert find_band(bands, "эхо") is not None


def test_filter_bands_by_size():
    bands = []
    add_band(bands, "A", "рок", 3)
    add_band(bands, "B", "джаз", 7)
    result = filter_bands_by_size(bands, 5)
    assert len(result) == 1
    assert result[0]["name"] == "B"


def test_sort_bands():
    bands = []
    add_band(bands, "A", "рок", 7)
    add_band(bands, "B", "джаз", 3)
    sorted_bands = sort_bands(bands)
    assert sorted_bands[0]["members_count"] == 3
