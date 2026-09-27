"""Точка запуска сервиса планирования репетиций."""
from models import Band, Room, Rehearsal
from models.bands import add_band, get_band_by_id
from models.members import get_members_by_band
from models.rooms import add_room, find_room, get_room_by_id, sort_rooms
from models.rehearsals import (
    create_rehearsal,
    cancel_rehearsal,
    is_room_available,
    get_rehearsal_status,
)
from storage import (
    load_bands, save_bands,
    load_members, save_members,
    load_rooms, save_rooms,
    load_rehearsals, save_rehearsals,
)
from utils import input_int, input_date, input_time

BANDS_FILE = "data/bands.json"
MEMBERS_FILE = "data/members.json"
ROOMS_FILE = "data/rooms.json"
REHEARSALS_FILE = "data/rehearsals.json"


def show_bands(bands: list[Band]) -> None:
    """Вывести список групп."""
    if not bands:
        print("Список групп пуст.")
        return
    print("\n--- Группы ---")
    for band in bands:
        print(band)


def show_rooms(rooms: list[Room]) -> None:
    """Вывести список помещений."""
    if not rooms:
        print("Список помещений пуст.")
        return
    print("\n--- Помещения ---")
    for room in rooms:
        print(room)


def show_rehearsals(rehearsals: list[Rehearsal]) -> None:
    """Вывести список репетиций."""
    if not rehearsals:
        print("Список репетиций пуст.")
        return
    print("\n--- Репетиции ---")
    for rehearsal in rehearsals:
        print(rehearsal)


def create_new_rehearsal(
    bands: list[Band],
    rooms: list[Room],
    rehearsals: list[Rehearsal],
) -> None:
    """Запросить данные и создать репетицию."""
    show_bands(bands)
    band_id = input_int("Введите id группы: ")
    band = get_band_by_id(bands, band_id)
    if band is None:
        print("Группа не найдена.")
        return

    show_rooms(rooms)
    room_id = input_int("Введите id помещения: ")
    room = get_room_by_id(rooms, room_id)
    if room is None:
        print("Помещение не найдено.")
        return

    rehearsal_date = input_date("Дата (ДД.ММ.ГГГГ): ")
    start_time = input_time("Время начала (ЧЧ:ММ): ")

    rehearsal = create_rehearsal(
        rehearsals,
        band,
        room,
        rehearsal_date,
        start_time.strftime("%H:%M"),
    )
    if rehearsal is not None:
        print(f"Репетиция создана: {rehearsal}")


def menu() -> None:
    """Главный цикл меню приложения."""
    bands = load_bands(BANDS_FILE)
    members = load_members(MEMBERS_FILE)
    rooms = load_rooms(ROOMS_FILE)
    rehearsals = load_rehearsals(REHEARSALS_FILE, bands, rooms)

    while True:
        print("\n=== Сервис планирования репетиций ===")
        print("1. Показать группы")
        print("2. Показать участников группы")
        print("3. Показать помещения")
        print("4. Добавить группу")
        print("5. Добавить помещение")
        print("6. Найти помещение по названию")
        print("7. Проверить доступность помещения на дату")
        print("8. Забронировать репетицию")
        print("9. Отменить репетицию")
        print("10. Показать репетиции")
        print("11. Сортировать помещения по вместимости")
        print("0. Выход")

        choice = input_int("Выберите действие: ")

        if choice == 1:
            show_bands(bands)
        elif choice == 2:
            show_bands(bands)
            band_id = input_int("Введите id группы: ")
            group = get_members_by_band(members, band_id)
            if not group:
                print("Участники не найдены.")
            for member in group:
                print(member)
        elif choice == 3:
            show_rooms(rooms)
        elif choice == 4:
            name = input("Название группы: ")
            genre = input("Жанр: ")
            members_count = input_int("Количество участников: ")
            add_band(bands, name, genre, members_count)
            save_bands(BANDS_FILE, bands)
            print("Группа добавлена.")
        elif choice == 5:
            name = input("Название помещения: ")
            capacity = input_int("Вместимость: ")
            address = input("Адрес: ")
            add_room(rooms, name, capacity, address)
            save_rooms(ROOMS_FILE, rooms)
            print("Помещение добавлено.")
        elif choice == 6:
            query = input("Подстрока названия: ")
            room = find_room(rooms, query)
            if room:
                print(room)
            else:
                print("Помещение не найдено.")
        elif choice == 7:
            show_rooms(rooms)
            room_id = input_int("Введите id помещения: ")
            room = get_room_by_id(rooms, room_id)
            if room is None:
                print("Помещение не найдено.")
                continue
            rehearsal_date = input_date("Дата (ДД.ММ.ГГГГ): ")
            available = is_room_available(
                rehearsals, room, rehearsal_date
            )
            print(get_rehearsal_status(available))
        elif choice == 8:
            create_new_rehearsal(bands, rooms, rehearsals)
            save_rehearsals(REHEARSALS_FILE, rehearsals)
        elif choice == 9:
            show_rehearsals(rehearsals)
            rehearsal_id = input_int("Введите id репетиции: ")
            if cancel_rehearsal(rehearsals, rehearsal_id):
                save_rehearsals(REHEARSALS_FILE, rehearsals)
                print("Репетиция отменена.")
            else:
                print("Репетиция не найдена.")
        elif choice == 10:
            show_rehearsals(rehearsals)
        elif choice == 11:
            for room in sort_rooms(rooms):
                print(room)
        elif choice == 0:
            save_bands(BANDS_FILE, bands)
            save_members(MEMBERS_FILE, members)
            save_rooms(ROOMS_FILE, rooms)
            save_rehearsals(REHEARSALS_FILE, rehearsals)
            print("Данные сохранены. Выход.")
            break
        else:
            print("Неизвестная команда.")


def main() -> None:
    """Точка запуска приложения."""
    menu()


if __name__ == "__main__":
    main()
