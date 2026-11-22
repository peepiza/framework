from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Q

from .models import Band, Rehearsal


class RehearsalInline(admin.TabularInline):
    model = Rehearsal
    fields = ("rehearsal_date", "start_time", "band", "room", "status")
    readonly_fields = fields
    show_change_link = True
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Band)
class BandAdmin(admin.ModelAdmin):
    list_display = ("name", "genre", "members_count")
    search_fields = ("name", "genre")
    list_filter = ("genre",)
    ordering = ("name", "pk")
    list_per_page = 20
    inlines = (RehearsalInline,)


@admin.register(Rehearsal)
class RehearsalAdmin(admin.ModelAdmin):
    list_display = ("id", "rehearsal_date", "start_time", "band", "room", "status")
    list_filter = ("status", "rehearsal_date", "room")
    search_fields = ("band__name", "room__name")
    list_select_related = ("band", "room")
    ordering = ("-rehearsal_date", "pk")
    list_per_page = 20
    readonly_fields = ("id",)
    actions = ("cancel_rehearsals", "restore_rehearsals")

    @admin.action(permissions=["change"], description="Отменить выбранные репетиции")
    def cancel_rehearsals(self, request, queryset):
        count = queryset.active().update(status=Rehearsal.Status.CANCELLED)
        self.message_user(request, f"Отменено репетиций: {count}.")

    @admin.action(permissions=["change"], description="Вернуть отменённые репетиции в активные")
    def restore_rehearsals(self, request, queryset):
        restored = skipped = 0
        with transaction.atomic():
            for rehearsal in queryset.cancelled().select_related("room", "band").order_by("pk"):
                conflicts = Rehearsal.objects.active().for_date(rehearsal.rehearsal_date).filter(
                    Q(room_id=rehearsal.room_id) | Q(band_id=rehearsal.band_id),
                )
                if conflicts.exists() or not rehearsal.room.is_suitable_for(
                    rehearsal.band.members_count,
                ):
                    skipped += 1
                    continue
                rehearsal.status = Rehearsal.Status.ACTIVE
                rehearsal.save(update_fields=["status"])
                restored += 1
        self.message_user(
            request, f"Восстановлено: {restored}. Пропущено из-за конфликта или вместимости: {skipped}.",
            level=messages.WARNING if skipped else messages.SUCCESS,
        )
