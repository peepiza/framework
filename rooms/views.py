"""Представления для помещений."""
from datetime import date
from django.http import HttpResponse
from homepage.views import page

# Импорты из ПР3
from models.rooms import get_room_by_id
from storage import load_rooms, load_bands, load_rehearsals
from models.rehearsals import is_room_available


def rooms(request):
    """Список всех помещений."""
    items = ""
    for room in load_rooms("data/rooms.json"):
        text = f"{room.name} — вместимость: {room.capacity} чел."
        items += f'''
        <li class="list-group-item d-flex justify-content-between align-items-center">
            {text}
            <a href="/rooms/{room.id}/" class="btn btn-sm btn-outline-primary">Подробнее</a>
        </li>'''

    content = f"""
    <h1>Помещения</h1>
    <ul class="list-group mt-3">{items}</ul>
    """
    return HttpResponse(page("Список помещений", content))


def room_detail(request, room_id: int):
    """Детальная страница помещения."""
    rooms_list = load_rooms("data/rooms.json")
    room = get_room_by_id(rooms_list, room_id)

    if room is None:
        content = """
        <h1 class="text-danger">Помещение не найдено</h1>
        <a href="/rooms/" class="btn btn-outline-secondary">← к списку</a>
        """
        return HttpResponse(page("Ошибка 404", content), status=404)

    # Проверяем доступность на сегодня с помощью логики ПР3
    bands = load_bands("data/bands.json")
    rehearsals = load_rehearsals("data/rehearsals.json", bands, rooms_list)

    available = is_room_available(rehearsals, room, date.today())
    status_text = "Свободно" if available else "Занято"
    badge_class = "bg-success" if available else "bg-danger"

    content = f"""
    <div class="card shadow-sm">
        <div class="card-body">
            <h2 class="card-title">{room.name}</h2>
            <p class="card-text"><strong>ID:</strong> {room.id}</p>
            <p class="card-text"><strong>Адрес:</strong> {room.address}</p>
            <p class="card-text"><strong>Вместимость:</strong> {room.capacity} чел.</p>
            <p class="card-text">
                <strong>Доступность сегодня:</strong>
                <span class="badge {badge_class}">{status_text}</span>
            </p>
            <a href="/rooms/" class="btn btn-outline-secondary mt-3">← Назад</a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Помещение - {room.name}", content))
