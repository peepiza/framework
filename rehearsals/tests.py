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
            "id", "band_id", "room_id", "rehearsal_date", "start_time", "status",
        )
        self.assertEqual(
            list(rehearsals),
            [
                (30, 20, 10, date(2026, 9, 15), time(19, 0), Rehearsal.Status.ACTIVE),
                (40, 20, 10, date(2026, 9, 15), time(19, 0), Rehearsal.Status.ACTIVE),
                (50, 20, 10, date(2026, 9, 15), time(19, 0), Rehearsal.Status.CANCELLED),
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
                start_time=time(19),
                status=Rehearsal.Status.CANCELLED if day == 6 else Rehearsal.Status.ACTIVE,
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


class AdminAndStatusTests(TestCase):
    def test_room_computed_size_and_both_addresses(self):
        room = Room.objects.create(name="Зал", capacity=49)
        other = Room.objects.create(name="Зал", capacity=50)
        self.assertNotEqual(room.slug, other.slug)
        self.assertFalse(room.is_large)
        room.capacity = 50
        room.save(update_fields=["capacity"])
        room.refresh_from_db()
        self.assertTrue(room.is_large)
        self.assertContains(self.client.get(room.get_absolute_url()), "Зал")
        self.assertContains(self.client.get(f"/rooms/{room.pk}/"), "Зал")
        self.assertEqual(self.client.get("/rooms/missing-slug/").status_code, 404)

    def test_admin_read_only_staff_permissions(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Permission

        staff = get_user_model().objects.create_user("reader", is_staff=True)
        staff.user_permissions.add(
            Permission.objects.get(content_type__app_label="rooms", codename="view_room"),
        )
        self.client.force_login(staff)
        self.assertEqual(self.client.get("/admin/rooms/room/").status_code, 200)
        self.assertEqual(self.client.get("/admin/rooms/room/add/").status_code, 403)
        self.assertEqual(self.client.get("/admin/rehearsals/rehearsal/").status_code, 403)

    def test_completed_rehearsal_does_not_block_room(self):
        room = Room.objects.create(name="Зал", capacity=30)
        band = Band.objects.create(name="Группа", genre="Рок", members_count=4)
        selected_date = date(2026, 9, 15)
        Rehearsal.objects.create(
            room=room, band=band, rehearsal_date=selected_date,
            start_time=time(19), status=Rehearsal.Status.COMPLETED,
        )
        self.assertEqual(Rehearsal.objects.completed().for_date(selected_date).count(), 1)
        self.assertFalse(Rehearsal.objects.active().exists())
        response = self.client.get("/rooms/available/", {"date": selected_date})
        self.assertContains(response, "Зал")
        response = self.client.get("/rehearsals/statistics/")
        self.assertEqual(response.context["totals"]["completed"], 1)


class RehearsalFormsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model

        cls.operator = get_user_model().objects.create_user(
            "operator", is_staff=True, is_superuser=True,
        )
        cls.room = Room.objects.create(name="Зал", capacity=30)
        cls.other_room = Room.objects.create(name="Студия", capacity=20)
        cls.band = Band.objects.create(name="Группа", genre="Джаз", members_count=5)
        cls.other_band = Band.objects.create(name="Трио", genre="Фолк", members_count=3)

    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        self.client.force_login(self.operator)
        self.selected_date = timezone.localdate() + timedelta(days=1)
        self.payload = {
            "room": self.room.pk, "band": self.band.pk,
            "rehearsal_date": self.selected_date.isoformat(), "start_time": "19:00",
        }

    def test_create_edit_cancel_and_reuse_room(self):
        self.assertContains(self.client.get("/rehearsals/new/"), "Новая репетиция")
        response = self.client.post("/rehearsals/new/", self.payload)
        current = Rehearsal.objects.get()
        url = f"/rehearsals/{current.pk}/"
        self.assertRedirects(response, url)
        self.assertContains(self.client.get(url + "edit/"), "19:00:00")
        self.assertRedirects(
            self.client.post(url + "edit/", {**self.payload, "start_time": "20:00"}), url,
        )
        self.assertEqual(Rehearsal.objects.count(), 1)
        current.refresh_from_db()
        self.assertEqual(current.start_time, time(20))
        self.assertEqual(self.client.get(url + "cancel/").status_code, 405)
        self.assertEqual(self.client.get("/rehearsals/999/edit/").status_code, 404)
        self.assertRedirects(self.client.post(url + "cancel/"), url)
        current.refresh_from_db()
        self.assertEqual(current.status, Rehearsal.Status.CANCELLED)
        self.assertEqual(self.client.post("/rehearsals/new/", self.payload).status_code, 302)
        self.assertEqual(Rehearsal.objects.count(), 2)

    def test_validation_rejects_past_dates_capacity_and_conflicts(self):
        from datetime import timedelta
        from django.utils import timezone

        url = "/rehearsals/new/"
        past = timezone.localdate() - timedelta(days=1)
        response = self.client.post(url, {**self.payload, "rehearsal_date": past.isoformat()})
        self.assertContains(response, "Дата репетиции не может быть в прошлом")
        small = Room.objects.create(name="Кабинет", capacity=1)
        response = self.client.post(url, {**self.payload, "room": small.pk})
        self.assertContains(response, "недостаточно мест")
        self.assertFalse(Rehearsal.objects.exists())

        self.client.post(url, self.payload)
        for change in ({"band": self.other_band.pk}, {"room": self.other_room.pk}):
            response = self.client.post(url, {**self.payload, **change})
            self.assertContains(response, "уже заняты")
        self.assertEqual(Rehearsal.objects.count(), 1)
        self.client.post(url, {**self.payload, "room": self.other_room.pk, "band": self.other_band.pk})
        other = Rehearsal.objects.get(band=self.other_band)
        response = self.client.post(f"/rehearsals/{other.pk}/edit/", self.payload)
        self.assertContains(response, "уже заняты")
        other.refresh_from_db()
        self.assertEqual(other.room, self.other_room)

    def test_permission_and_csrf_protection(self):
        from django.test import Client

        anonymous = Client()
        self.assertEqual(anonymous.get("/rehearsals/new/").status_code, 403)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.operator)
        self.assertEqual(client.post("/rehearsals/new/", self.payload).status_code, 403)
        self.assertFalse(Rehearsal.objects.exists())
        client.get("/rehearsals/new/")
        self.assertEqual(
            client.post("/rehearsals/new/", {
                **self.payload, "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
            }).status_code,
            302,
        )
        rehearsal = Rehearsal.objects.get()
        self.assertEqual(client.post(f"/rehearsals/{rehearsal.pk}/cancel/").status_code, 403)
