"""Точка запуска сервиса планирования репетиций."""
from bands import add_band
from members import get_members_by_band
from rooms import add_room, find_room, sort_rooms
from rehearsals import (
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


def show_bands(bands: list[dict]) -> None:
    """Вывести список групп."""
    if not bands:
        print("Список групп пуст.")
        return
    print("\n--- Группы ---")
    for band in bands:
        print(
            f"[{band['id']}] {band['name']} | "
            f"жанр: {band['genre']} | "
            f"участников: {band['members_count']}"
        )


def show_rooms(rooms: list[dict]) -> None:
    """Вывести список помещений."""
    if not rooms:
        print("Список помещений пуст.")
        return
    print("\n--- Помещения ---")
    for room in rooms:
        print(
            f"[{room['id']}] {room['name']} | "
            f"вместимость: {room['capacity']} | "
            f"адрес: {room['address']}"
        )


def show_rehearsals(
    rehearsals: list[dict],
    bands: list[dict],
    rooms: list[dict],
) -> None:
    """Вывести список репетиций с расшифровкой группы и помещения."""
    if not rehearsals:
        print("Список репетиций пуст.")
        return
    print("\n--- Репетиции ---")
    for rehearsal in rehearsals:
        band = next(
            (b for b in bands if b["id"] == rehearsal["band_id"]),
            None,
        )
        room = next(
            (r for r in rooms if r["id"] == rehearsal["room_id"]),
            None,
        )
        band_name = band["name"] if band else "—"
        room_name = room["name"] if room else "—"
        print(
            f"[{rehearsal['id']}] {band_name} | "
            f"{room_name} | "
            f"{rehearsal['rehearsal_date']} "
            f"{rehearsal['start_time']}"
        )


def menu() -> None:
    """Главный цикл меню приложения."""
    bands = load_bands(BANDS_FILE)
    members = load_members(MEMBERS_FILE)
    rooms = load_rooms(ROOMS_FILE)
    rehearsals = load_rehearsals(REHEARSALS_FILE)

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
                print(
                    f"{member['name']} — {member['instrument']}"
                )
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
                print(
                    f"[{room['id']}] {room['name']} | "
                    f"вместимость: {room['capacity']}"
                )
            else:
                print("Помещение не найдено.")
        elif choice == 7:
            show_rooms(rooms)
            room_id = input_int("Введите id помещения: ")
            rehearsal_date = input_date("Дата (ДД.ММ.ГГГГ): ")
            available = is_room_available(
                rehearsals, room_id, rehearsal_date
            )
            print(get_rehearsal_status(available))
        elif choice == 8:
            show_bands(bands)
            band_id = input_int("Введите id группы: ")
            show_rooms(rooms)
            room_id = input_int("Введите id помещения: ")
            rehearsal_date = input_date("Дата (ДД.ММ.ГГГГ): ")
            start_time = input_time("Время начала (ЧЧ:ММ): ")
            rehearsal = create_rehearsal(
                rehearsals, bands, rooms,
                band_id, room_id,
                rehearsal_date, start_time.strftime("%H:%M"),
            )
            if rehearsal:
                save_rehearsals(REHEARSALS_FILE, rehearsals)
                print("Репетиция создана.")
        elif choice == 9:
            show_rehearsals(rehearsals, bands, rooms)
            rehearsal_id = input_int("Введите id репетиции: ")
            if cancel_rehearsal(rehearsals, rehearsal_id):
                save_rehearsals(REHEARSALS_FILE, rehearsals)
                print("Репетиция отменена.")
            else:
                print("Репетиция не найдена.")
        elif choice == 10:
            show_rehearsals(rehearsals, bands, rooms)
        elif choice == 11:
            for room in sort_rooms(rooms):
                print(
                    f"[{room['id']}] {room['name']} | "
                    f"вместимость: {room['capacity']}"
                )
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
