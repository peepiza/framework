from datetime import date, time

band_name = "Рок-группа «Эхо»"
room_name = "Репетиционная база «Ритм»"
participants = 5
rehearsal_date = date(2026, 9, 15)
rehearsal_time = time(19, 0)

room_is_free = True
band_is_free = True


def check_room_available(is_available):
    if is_available:
        return "Помещение свободно"
    return "Помещение занято"


def check_band_free(are_free):
    if are_free:
        return "Все участники свободны"
    return "Не все участники свободны"


def get_rehearsal_decision(room_free, band_free):
    if room_free and band_free:
        return "Репетиция подтверждена"
    return "Репетицию необходимо перенести"


room_status = check_room_available(room_is_free)
band_status = check_band_free(band_is_free)
decision = get_rehearsal_decision(room_is_free, band_is_free)

print(f"Группа: {band_name}")
print(f"Помещение: {room_name}")
print(f"Участников: {participants}")
print(f"Дата: {rehearsal_date}, время: {rehearsal_time}")
print(f"Помещение: {room_status}")
print(f"Участники: {band_status}")
print(f"Решение: {decision}")