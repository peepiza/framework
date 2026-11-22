from uuid import uuid4

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Room(models.Model):
    """Помещение для репетиций."""

    name = models.CharField("Название", max_length=200)
    capacity = models.PositiveIntegerField("Вместимость")
    address = models.TextField("Адрес", blank=True, null=True)

    image = models.ImageField("Фотография", upload_to="rooms/", blank=True)
    slug = models.SlugField("Слаг", max_length=120, unique=True, editable=False)
    is_large = models.GeneratedField(
        verbose_name="Помещение на 50 человек и больше",
        expression=models.Case(
            models.When(capacity__gte=50, then=models.Value(True)),
            default=models.Value(False),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            stem = slugify(self.name)[:80].strip("-_") or "room"
            self.slug = f"{stem}-{uuid4().hex}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:room_slug", kwargs={"slug": self.slug})

    def is_suitable_for(self, people_count: int) -> bool:
        return self.capacity >= people_count
