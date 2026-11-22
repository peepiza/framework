from django.db import models


class Room(models.Model):
    """Помещение для репетиций."""

    name = models.CharField("Название", max_length=200)
    capacity = models.PositiveIntegerField("Вместимость")
    address = models.TextField("Адрес", blank=True, null=True)

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"

    def __str__(self) -> str:
        return self.name

    def is_suitable_for(self, people_count: int) -> bool:
        return self.capacity >= people_count
