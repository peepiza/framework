import sqlite3
from contextlib import closing
from datetime import date, time
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.management import call_command, CommandError
from django.test import TestCase

from rehearsals.models import Band, Rehearsal
from rooms.models import Room


class ImportPR7DataTests(TestCase):
    def setUp(self):
        self.source = Path(self.enterContext(TemporaryDirectory())) / "source.sqlite"
        schema = (settings.BASE_DIR / "sql" / "schema.sql").read_text(encoding="utf-8")
        with closing(sqlite3.connect(self.source)) as db, db:
            db.executescript(schema)
            db.execute("INSERT INTO rooms VALUES (10, 'Зал', 12, NULL)")
            db.execute("INSERT INTO bands VALUES (20, 'Группа', 'рок', 4)")
            db.executemany(
                "INSERT INTO rehearsals VALUES (?, 20, 10, '2026-09-15', '19:00', ?)",
                [(30, 0), (40, 0), (50, 1)],
            )

    def import_data(self):
        call_command("import_pr7_data", source=self.source, stdout=StringIO())

    def change_source(self, query):
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute(query)

    def test_import_preserves_records_and_conflicting_rehearsals(self):
        original = self.source.read_bytes()
        self.import_data()
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(
            list(Room.objects.values_list("id", "name", "capacity", "address")),
            [(10, "Зал", 12, None)],
        )
        self.assertEqual(
            list(Band.objects.values_list("id", "name", "genre", "members_count")),
            [(20, "Группа", "рок", 4)],
        )
        rehearsals = Rehearsal.objects.order_by("pk").values_list(
            "id", "band_id", "room_id", "rehearsal_date", "start_time", "is_cancelled",
        )
        self.assertEqual(
            list(rehearsals),
            [
                (30, 20, 10, date(2026, 9, 15), time(19, 0), False),
                (40, 20, 10, date(2026, 9, 15), time(19, 0), False),
                (50, 20, 10, date(2026, 9, 15), time(19, 0), True),
            ],
        )

    def test_repeat_is_rejected_without_changing_data(self):
        self.import_data()
        original = list(Rehearsal.objects.order_by("pk").values())
        self.change_source("UPDATE rooms SET capacity = 50")
        with self.assertRaisesMessage(CommandError, "Целевые таблицы должны быть пустыми"):
            self.import_data()
        self.assertEqual(list(Rehearsal.objects.order_by("pk").values()), original)
        self.assertEqual(Room.objects.get(pk=10).capacity, 12)

    def test_invalid_data_rolls_back_all_tables(self):
        for change in (
            "rehearsal_date = '2026-02-30'",
            "start_time = '25:00'",
            "is_cancelled = 2",
            "band_id = 999",
        ):
            with self.subTest(change=change):
                self.change_source(
                    "UPDATE rehearsals SET rehearsal_date = '2026-09-15', "
                    "start_time = '19:00', is_cancelled = 1, band_id = 20 WHERE id = 50"
                )
                self.change_source(f"UPDATE rehearsals SET {change} WHERE id = 50")
                with self.assertRaisesMessage(CommandError, "rehearsals, ID 50"):
                    self.import_data()
                self.assertFalse(Room.objects.exists())
                self.assertFalse(Band.objects.exists())
                self.assertFalse(Rehearsal.objects.exists())


class RehearsalPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Большой зал", capacity=20, address="Центр")
        cls.spare = Room.objects.create(name="Малый зал", capacity=8)
        cls.band = Band.objects.create(name="Ансамбль", genre="Рок", members_count=4)
        Band.objects.create(name="Оркестр", genre="Джаз", members_count=5)
        for day in range(1, 7):
            Rehearsal.objects.create(
                room=cls.room, band=cls.band, rehearsal_date=date(2026, 9, day),
                start_time=time(19), is_cancelled=day == 6,
            )

    def test_filters_and_pagination(self):
        response = self.client.get("/rehearsals/", {
            "room": self.room.pk, "band": self.band.pk, "q": "Ансамбль", "sort": "oldest",
        })
        self.assertEqual(response.context["page"].paginator.count, 6)
        self.assertEqual(response.context["page"][0].rehearsal_date, date(2026, 9, 1))
        self.assertContains(response, "sort=oldest&amp;page=2")
        response = self.client.get("/rehearsals/", {"date": "invalid"})
        self.assertEqual(response.context["page"].paginator.count, 0)

    def test_available_rooms_and_statistics(self):
        for day, expected in ((1, {self.spare.pk}), (6, {self.spare.pk, self.room.pk})):
            response = self.client.get("/rooms/available/", {"date": f"2026-09-0{day}"})
            self.assertEqual({room.pk for room in response.context["rooms"]}, expected)
        response = self.client.get("/rehearsals/statistics/")
        self.assertEqual(response.context["totals"]["total"], 5)
        self.assertIn(0, [row.rehearsals_count for row in response.context["statistics"]])

    def test_existing_details_and_missing_records(self):
        self.assertContains(self.client.get(f"/rooms/{self.room.pk}/"), "Большой зал")
        pk = Rehearsal.objects.first().pk
        self.assertContains(self.client.get(f"/rehearsals/{pk}/"), "Ансамбль")
        for url in ("/rooms/999/", "/rehearsals/999/"):
            self.assertEqual(self.client.get(url).status_code, 404)
