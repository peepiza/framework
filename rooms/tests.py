from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import Room


class RoomImageTests(TestCase):
    def setUp(self):
        self.media = Path(self.enterContext(TemporaryDirectory()))
        self.enterContext(override_settings(MEDIA_ROOT=self.media))
        self.room = Room.objects.create(name="Зал", capacity=15)
        self.user = get_user_model().objects.create_user(
            "photo-editor", is_staff=True, is_superuser=True,
        )
        self.client.force_login(self.user)

    @staticmethod
    def image(filename, color):
        data = BytesIO()
        Image.new("RGB", (2, 2), color=color).save(data, format="PNG")
        return SimpleUploadedFile(filename, data.getvalue(), content_type="image/png")

    def test_upload_through_form_and_replace_through_admin(self):
        self.assertContains(self.client.get(self.room.get_absolute_url()), "Фотография пока")
        response = self.client.post(
            f"/rooms/{self.room.pk}/photo/", {"image": self.image("room.png", "white")},
        )
        self.assertRedirects(response, self.room.get_absolute_url())
        self.room.refresh_from_db()
        original = self.room.image.name
        self.assertTrue((self.media / original).is_file())
        self.assertContains(self.client.get(self.room.get_absolute_url()), self.room.image.url)
        response = self.client.post(f"/admin/rooms/room/{self.room.pk}/change/", {
            "name": self.room.name, "capacity": self.room.capacity, "address": "",
            "image": self.image("updated.png", "black"), "_save": "Сохранить",
            "rehearsals-TOTAL_FORMS": "0", "rehearsals-INITIAL_FORMS": "0",
        })
        self.assertEqual(response.status_code, 302)
        self.room.refresh_from_db()
        self.assertNotEqual(self.room.image.name, original)
        self.assertTrue((self.media / self.room.image.name).is_file())

    def test_invalid_image_keeps_existing_room_unchanged(self):
        response = self.client.post(f"/rooms/{self.room.pk}/photo/", {
            "image": SimpleUploadedFile("bad.png", b"invalid", content_type="image/png"),
        })
        self.assertTrue(response.context["form"]["image"].errors)
        self.room.refresh_from_db()
        self.assertFalse(self.room.image)
