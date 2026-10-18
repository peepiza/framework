"""Представления для репетиций."""
from django.http import HttpResponse
from homepage.views import page

# Импорты из ПР3
from storage import load_rooms, load_bands, load_rehearsals
from models.rehearsals import find_rehearsal_by_id


def rehearsals(request):
    """Список всех репетиций."""
    rooms = load_rooms("data/rooms.json")
    bands = load_bands("data/bands.json")
    rehearsals_list = load_rehearsals("data/rehearsals.json", bands, rooms)

    items = ""
    for r in rehearsals_list:
        status = "Отменена" if r.is_cancelled else "Активна"
        badge = "bg-secondary" if r.is_cancelled else "bg-success"

        text = f"{r.band.name} — {r.room.name} ({r.rehearsal_date} {r.start_time})"
        items += f'''
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <span>{text} <span class="badge {badge}">{status}</span></span>
            <a href="/rehearsals/{r.id}/" class="btn btn-sm btn-outline-primary">Детали</a>
        </li>'''

    content = f"""
    <h1>Репетиции</h1>
    <ul class="list-group mt-3">{items}</ul>
    """
    return HttpResponse(page("Список репетиций", content))


def rehearsal_detail(request, rehearsal_id: int):
    """Детальная страница репетиции."""
    rooms = load_rooms("data/rooms.json")
    bands = load_bands("data/bands.json")
    rehearsals_list = load_rehearsals("data/rehearsals.json", bands, rooms)

    rehearsal = find_rehearsal_by_id(rehearsals_list, rehearsal_id)

    if rehearsal is None:
        content = """
        <h1 class="text-danger">Репетиция не найдена</h1>
        <a href="/rehearsals/" class="btn btn-outline-secondary">← к списку</a>
        """
        return HttpResponse(page("Ошибка 404", content), status=404)

    status = "Отменена" if rehearsal.is_cancelled else "Активна"
    badge = "bg-secondary" if rehearsal.is_cancelled else "bg-success"

    content = f"""
    <div class="card shadow-sm">
        <div class="card-body">
            <h2 class="card-title">Репетиция №{rehearsal.id}</h2>
            <p class="card-text"><strong>Группа:</strong> {rehearsal.band.name}</p>
            <p class="card-text"><strong>Помещение:</strong> {rehearsal.room.name}</p>
            <p class="card-text"><strong>Дата:</strong> {rehearsal.rehearsal_date}</p>
            <p class="card-text"><strong>Время:</strong> {rehearsal.start_time}</p>
            <p class="card-text">
                <strong>Статус:</strong>
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="/rehearsals/" class="btn btn-outline-secondary mt-3">← Назад</a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Репетиция №{rehearsal.id}", content))
