-- 1. Список всех помещений (SELECT)
SELECT id, name, capacity FROM rooms ORDER BY name;

-- 2. Список групп (SELECT)
SELECT id, name, genre, members_count FROM bands ORDER BY name;

-- 3. Поиск помещений по вместимости (WHERE)
SELECT id, name, capacity FROM rooms WHERE capacity >= 10 ORDER BY capacity;

-- 4. Поиск репетиций на конкретную дату (WHERE)
SELECT id, band_id, room_id, rehearsal_date FROM rehearsals WHERE rehearsal_date = '2026-09-15' AND is_cancelled = 0;

-- 5. Полная информация о репетициях (JOIN двух таблиц)
SELECT rehearsals.id, bands.name AS band_name, rooms.name AS room_name, rehearsals.rehearsal_date, rehearsals.start_time 
FROM rehearsals 
JOIN bands ON rehearsals.band_id = bands.id 
JOIN rooms ON rehearsals.room_id = rooms.id
WHERE rehearsals.is_cancelled = 0;

-- 6. Свободные помещения на дату (Подзапрос + NOT IN)
SELECT rooms.id, rooms.name 
FROM rooms 
WHERE rooms.id NOT IN (
    SELECT rehearsals.room_id 
    FROM rehearsals 
    WHERE rehearsals.rehearsal_date = '2026-09-15' AND rehearsals.is_cancelled = 0
);

-- 7. Общее количество активных репетиций (COUNT)
SELECT COUNT(*) AS active_rehearsals FROM rehearsals WHERE is_cancelled = 0;

-- 8. Количество участников во всех группах (SUM)
SELECT SUM(members_count) AS total_members FROM bands;

-- 9. Статистика: сколько репетиций у каждой группы (GROUP BY + JOIN)
SELECT bands.name AS band_name, COUNT(rehearsals.id) AS rehearsals_count 
FROM bands 
LEFT JOIN rehearsals ON bands.id = rehearsals.band_id AND rehearsals.is_cancelled = 0
GROUP BY bands.id, bands.name
ORDER BY rehearsals_count DESC;

-- 10. Помещения, у которых больше 1 репетиции (GROUP BY + HAVING)
SELECT rooms.name AS room_name, COUNT(rehearsals.id) AS rehearsals_count
FROM rooms
JOIN rehearsals ON rooms.id = rehearsals.room_id
WHERE rehearsals.is_cancelled = 0
GROUP BY rooms.id, rooms.name
HAVING COUNT(rehearsals.id) > 1;