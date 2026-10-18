"""Представления для репетиций."""
from django.shortcuts import render
from storage import load_rooms, load_bands, load_rehearsals
from models.rehearsals import find_rehearsal_by_id


def rehearsals(request):
    """Список всех репетиций."""
    rooms = load_rooms("data/rooms.json")
    bands = load_bands("data/bands.json")
    rehearsals_list = load_rehearsals("data/rehearsals.json", bands, rooms)

    context = {
        "rehearsals": rehearsals_list,
    }
    return render(request, "rehearsals/rehearsal_list.html", context)


def rehearsal_detail(request, rehearsal_id: int):
    """Детальная страница репетиции."""
    rooms = load_rooms("data/rooms.json")
    bands = load_bands("data/bands.json")
    rehearsals_list = load_rehearsals("data/rehearsals.json", bands, rooms)

    rehearsal = find_rehearsal_by_id(rehearsals_list, rehearsal_id)

    context = {
        "rehearsal": rehearsal,
    }

    # Если репетиции нет, возвращаем статус 404
    status_code = 404 if rehearsal is None else 200
    return render(
        request,
        "rehearsals/rehearsal_detail.html",
        context,
        status=status_code
    )
