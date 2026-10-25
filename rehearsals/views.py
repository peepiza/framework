import sqlite3
from django.shortcuts import render

DB_PATH = "data/rehearsal_planner.sqlite"


def rehearsals(request):
    """Список репетиций с названиями групп и помещений из БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = """
        SELECT r.id, b.name AS band_name, ro.name AS room_name, 
               r.rehearsal_date, r.start_time, r.is_cancelled 
        FROM rehearsals r
        JOIN bands b ON r.band_id = b.id
        JOIN rooms ro ON r.room_id = ro.id
        ORDER BY r.rehearsal_date DESC
    """
    rehearsals_data = conn.execute(query).fetchall()
    conn.close()
    
    return render(request, "rehearsals/rehearsal_list.html", {"rehearsals": rehearsals_data})


def rehearsal_detail(request, rehearsal_id: int):
    """Детальная страница репетиции из БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = """
        SELECT r.id, b.name AS band_name, ro.name AS room_name, 
               r.rehearsal_date, r.start_time, r.is_cancelled 
        FROM rehearsals r
        JOIN bands b ON r.band_id = b.id
        JOIN rooms ro ON r.room_id = ro.id
        WHERE r.id = ?
    """
    # Параметризованный запрос
    rehearsal = conn.execute(query, [rehearsal_id]).fetchone()
    conn.close()
    
    context = {"rehearsal": rehearsal}
    return render(
        request, 
        "rehearsals/rehearsal_detail.html", 
        context, 
        status=404 if rehearsal is None else 200
    )


def statistics(request):
    """Статистика: сколько репетиций у каждой группы."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = """
        SELECT bands.name AS band_name, COUNT(rehearsals.id) AS rehearsals_count 
        FROM bands 
        LEFT JOIN rehearsals ON bands.id = rehearsals.band_id AND rehearsals.is_cancelled = 0
        GROUP BY bands.id, bands.name
        ORDER BY rehearsals_count DESC
    """
    stats_data = conn.execute(query).fetchall()
    conn.close()
    
    return render(request, "rehearsals/statistics.html", {"statistics": stats_data})