"""Вспомогательные функции безопасного ввода."""
from datetime import date, datetime, time


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число.

    При некорректном вводе запрос повторяется.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def input_date(prompt: str) -> date:
    """Запросить дату в формате ДД.ММ.ГГГГ.

    При некорректном формате запрос повторяется.
    """
    while True:
        raw = input(prompt)
        try:
            return datetime.strptime(raw, "%d.%m.%Y").date()
        except ValueError:
            print("Ошибка: используйте формат ДД.ММ.ГГГГ.")


def input_time(prompt: str) -> time:
    """Запросить время в формате ЧЧ:ММ.

    При некорректном формате запрос повторяется.
    """
    while True:
        raw = input(prompt)
        try:
            return datetime.strptime(raw, "%H:%M").time()
        except ValueError:
            print("Ошибка: используйте формат ЧЧ:ММ.")
