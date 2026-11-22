from django.db import models


class Band(models.Model):
    """Музыкальная группа."""

    name = models.CharField("Название", max_length=200)
    genre = models.CharField("Жанр", max_length=100)
    members_count = models.PositiveIntegerField("Количество участников")

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self) -> str:
        return self.name


class RehearsalQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        return self.filter(rehearsal_date=selected_date)


class Rehearsal(models.Model):
    """Репетиция группы в помещении на выбранную дату."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        CANCELLED = "cancelled", "Отменена"
        COMPLETED = "completed", "Завершена"

    objects = RehearsalQuerySet.as_manager()

    band = models.ForeignKey(
        Band,
        on_delete=models.PROTECT,
        related_name="rehearsals",
        verbose_name="Группа",
    )
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.PROTECT,
        related_name="rehearsals",
        verbose_name="Помещение",
    )
    rehearsal_date = models.DateField("Дата репетиции")
    start_time = models.TimeField("Время начала")
    status = models.CharField(
        "Статус", max_length=10, choices=Status.choices, default=Status.ACTIVE,
    )

    class Meta:
        ordering = ("-rehearsal_date", "pk")
        verbose_name = "Репетиция"
        verbose_name_plural = "Репетиции"

    def __str__(self) -> str:
        return f"{self.band} — {self.room}, {self.rehearsal_date}"

    def cancel(self) -> None:
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
