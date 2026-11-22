"""Перенос данных репетиционного сервиса из базы ПР7."""

import sqlite3
from contextlib import closing
from datetime import date, time
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, connection, transaction

from rehearsals.models import Band, Rehearsal
from rooms.models import Room


TABLES = (
    (Room, "rooms", ("id", "name", "capacity", "address")),
    (Band, "bands", ("id", "name", "genre", "members_count")),
    (
        Rehearsal,
        "rehearsals",
        ("id", "band_id", "room_id", "rehearsal_date", "start_time", "is_cancelled"),
    ),
)


def rehearsal_values(row):
    pk, band_id, room_id, raw_date, raw_time, raw_cancelled = row
    rehearsal_date = date.fromisoformat(raw_date)
    start_time = time.fromisoformat(raw_time)
    if start_time.tzinfo is not None:
        raise ValueError("Ожидается время без часового пояса.")
    if type(raw_cancelled) is not int or raw_cancelled not in (0, 1):
        raise ValueError("Ожидается признак отмены 0 или 1.")
    status = Rehearsal.Status.CANCELLED if raw_cancelled else Rehearsal.Status.ACTIVE
    return pk, band_id, room_id, rehearsal_date, start_time, status


class Command(BaseCommand):
    help = "Переносит помещения, группы и репетиции ПР7 в пустые таблицы Django."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=Path,
            default=settings.BASE_DIR / "data" / "rehearsal_planner.sqlite",
            help="Путь к исходной базе SQLite ПР7.",
        )

    def handle(self, *args, source, **options):
        try:
            source_uri = Path(source).resolve(strict=True).as_uri() + "?mode=ro"
            with closing(sqlite3.connect(source_uri, uri=True)) as legacy:
                legacy.execute("BEGIN")
                with transaction.atomic():
                    existing_tables = set(connection.introspection.table_names())
                    for model, _, _ in TABLES:
                        if model._meta.db_table not in existing_tables:
                            raise CommandError(
                                "Таблицы ORM отсутствуют. Сначала примените миграции."
                            )
                    if any(model.objects.exists() for model, _, _ in TABLES):
                        raise CommandError("Целевые таблицы должны быть пустыми.")

                    expected = {
                        table: self.import_table(legacy, model, table, fields)
                        for model, table, fields in TABLES
                    }
                    for model, table, fields in TABLES:
                        target_fields = (*fields[:-1], "status") if model is Rehearsal else fields
                        actual = list(model.objects.order_by("pk").values_list(*target_fields))
                        if actual != expected[table]:
                            raise CommandError(
                                f"{table}: данные после переноса отличаются от источника."
                            )
                    connection.check_constraints(
                        table_names=[model._meta.db_table for model, _, _ in TABLES],
                    )
        except (OSError, sqlite3.Error, DatabaseError) as error:
            raise CommandError(f"Перенос прерван: {error}") from error

        summary = ", ".join(f"{table}: {len(rows)}" for table, rows in expected.items())
        self.stdout.write(self.style.SUCCESS(f"Перенос проверен и сохранён ({summary})."))

    @staticmethod
    def import_table(legacy, model, table, fields):
        columns = ", ".join(fields)
        expected = []
        records = []
        for row in legacy.execute(f"SELECT {columns} FROM {table} ORDER BY id"):
            try:
                values = rehearsal_values(row) if model is Rehearsal else row
                target_fields = (*fields[:-1], "status") if model is Rehearsal else fields
                record = model(**dict(zip(target_fields, values, strict=True)))
                record.full_clean(validate_unique=False)
            except (TypeError, ValueError, ValidationError) as error:
                raise CommandError(
                    f"{table}, ID {row[0]}: некорректные данные ({error})."
                ) from error
            expected.append(values)
            records.append(record)

        if model is Room:
            for record in records:
                record.save(force_insert=True)
        else:
            model.objects.bulk_create(records)
        return expected
