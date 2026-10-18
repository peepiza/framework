"""Представления для помещений."""
from django.shortcuts import render
from models.rooms import get_room_by_id
from storage import load_rooms


def rooms(request):
    """Список всех помещений."""
    rooms_list = load_rooms("data/rooms.json")
    context = {
        "rooms": rooms_list,
    }
    return render(request, "rooms/room_list.html", context)


def room_detail(request, room_id: int):
    """Детальная страница помещения."""
    rooms_list = load_rooms("data/rooms.json")
    room = get_room_by_id(rooms_list, room_id)

    context = {
        "room": room,
    }

    # Если помещения нет, возвращаем статус 404
    status_code = 404 if room is None else 200
    return render(
        request,
        "rooms/room_detail.html",
        context,
        status=status_code
    )
