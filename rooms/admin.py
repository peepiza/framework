from django.contrib import admin

from rehearsals.admin import RehearsalInline
from .forms import RoomImageForm
from .models import Room


class RoomAdminForm(RoomImageForm):
    class Meta(RoomImageForm.Meta):
        model = Room
        fields = "__all__"
        help_texts = {
            **RoomImageForm.Meta.help_texts,
            "capacity": "Количество человек, которое вмещает помещение.",
        }


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    form = RoomAdminForm
    list_display = ("name", "capacity", "address", "is_large")
    list_editable = ("capacity",)
    search_fields = ("name", "address")
    list_filter = ("is_large",)
    ordering = ("name", "pk")
    list_per_page = 20
    readonly_fields = ("id", "slug", "is_large")
    inlines = (RehearsalInline,)
