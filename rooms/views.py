import sqlite3
from django.shortcuts import render

DB_PATH = "data/rehearsal_planner.sqlite"

def rooms(request):
    """Список помещений из базы данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Чтобы в шаблоне работало room.name
    rooms_data = conn.execute("SELECT id, name, capacity, address FROM rooms ORDER BY name").fetchall()
    conn.close()
    
    return render(request, "rooms/room_list.html", {"rooms": rooms_data})


def available_rooms(request):
    """Поиск свободных помещений на выбранную дату."""
    booking_date = request.GET.get("date")
    rooms_data = []
    
    if booking_date:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Параметризованный запрос (безопасный)
        query = """
            SELECT id, name, capacity FROM rooms 
            WHERE id NOT IN (
                SELECT room_id FROM rehearsals 
                WHERE rehearsal_date = ? AND is_cancelled = 0
            )
        """
        rooms_data = conn.execute(query, [booking_date]).fetchall()
        conn.close()
        
    return render(request, "rooms/available.html", {
        "rooms": rooms_data, 
        "booking_date": booking_date
    })


# --- ДОБАВЛЯЕМ ЭТУ ФУНКЦИЮ ---
def room_detail(request, room_id: int):
    """Детальная страница помещения из базы данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = "SELECT id, name, capacity, address FROM rooms WHERE id = ?"
    
    # Параметризованный запрос
    room = conn.execute(query, [room_id]).fetchone()
    conn.close()
    
    context = {"room": room}
    return render(
        request, 
        "rooms/room_detail.html", 
        context, 
        status=404 if room is None else 200
    )