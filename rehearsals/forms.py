from django import forms
from django.db.models import Q
from django.utils import timezone

from rooms.models import Room
from .models import Band, Rehearsal


SORTS = {
    "recent": ("-rehearsal_date", "pk"),
    "oldest": ("rehearsal_date", "pk"),
    "room": ("room__name", "rehearsal_date", "pk"),
}
SORT_CHOICES = (
    ("recent", "Сначала новые"), ("oldest", "Сначала ранние"), ("room", "По помещению"),
)


class RehearsalFilterForm(forms.Form):
    date = forms.DateField(
        label="Дата", required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    room = forms.ModelChoiceField(
        label="Помещение", queryset=Room.objects.all(), required=False,
        empty_label="Все", widget=forms.Select(attrs={"class": "form-select"}),
    )
    band = forms.ModelChoiceField(
        label="Группа", queryset=Band.objects.all(), required=False,
        empty_label="Все", widget=forms.Select(attrs={"class": "form-select"}),
    )
    q = forms.CharField(
        label="Поиск", required=False, max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    sort = forms.ChoiceField(
        label="Сортировка", required=False, choices=SORT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        label="Статус", required=False, choices=[("", "Все"), *Rehearsal.Status.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class RehearsalForm(forms.ModelForm):
    class Meta:
        model = Rehearsal
        fields = ("band", "room", "rehearsal_date", "start_time")
        help_texts = {
            "room": "Вместимость помещения должна быть не меньше числа участников группы.",
            "rehearsal_date": "Укажите сегодняшнюю или будущую дату.",
        }
        widgets = {
            "band": forms.Select(attrs={"class": "form-select"}),
            "room": forms.Select(attrs={"class": "form-select"}),
            "rehearsal_date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"},
            ),
            "start_time": forms.TimeInput(
                format="%H:%M:%S", attrs={"type": "time", "step": "1", "class": "form-control"},
            ),
        }

    def clean_rehearsal_date(self):
        selected_date = self.cleaned_data["rehearsal_date"]
        if selected_date < timezone.localdate():
            raise forms.ValidationError("Дата репетиции не может быть в прошлом.")
        return selected_date

    def clean(self):
        data = super().clean()
        room, band, selected_date = (data.get(key) for key in ("room", "band", "rehearsal_date"))
        if room and band and not room.is_suitable_for(band.members_count):
            self.add_error("room", "В помещении недостаточно мест для группы.")
        if room and band and selected_date and self.instance.status == Rehearsal.Status.ACTIVE:
            conflicts = Rehearsal.objects.active().for_date(selected_date).exclude(
                pk=self.instance.pk,
            ).filter(Q(room=room) | Q(band=band))
            if conflicts.exists():
                raise forms.ValidationError("Помещение или группа уже заняты на выбранную дату.")
        return data
