from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, render

from rooms.models import Room
from .models import Band, Rehearsal


SORTS = {
    "recent": ("-rehearsal_date", "pk"),
    "oldest": ("rehearsal_date", "pk"),
    "room": ("room__name", "rehearsal_date", "pk"),
}
SORT_LABELS = {"recent": "Сначала новые", "oldest": "Сначала ранние", "room": "По помещению"}


def rehearsal_queryset(filters):
    queryset = Rehearsal.objects.all()
    if filters.get("date"):
        queryset = queryset.for_date(filters["date"])
    if filters.get("room"):
        queryset = queryset.filter(room_id=filters["room"])
    if filters.get("band"):
        queryset = queryset.filter(band_id=filters["band"])
    status = filters.get("status")
    if status:
        queryset = queryset.filter(status=status)
    if filters.get("q"):
        queryset = queryset.filter(
            Q(band__name__icontains=filters["q"]) | Q(room__name__icontains=filters["q"]),
        )
    return queryset.order_by(*SORTS.get(filters.get("sort"), SORTS["recent"]))


def rehearsals(request):
    raw = {key: request.GET.get(key, "") for key in ("date", "room", "band", "q", "sort", "status")}
    filters = {**raw, "q": raw["q"].strip()}
    errors = []
    if raw["date"]:
        try:
            filters["date"] = date.fromisoformat(raw["date"])
        except ValueError:
            errors.append("Введите корректную дату.")
    for key in ("room", "band"):
        if raw[key]:
            try:
                value = int(raw[key])
                if not 0 < value <= 2**63 - 1:
                    raise ValueError
                filters[key] = value
            except ValueError:
                errors.append("Некорректное помещение или группа.")
    if raw["sort"] and raw["sort"] not in SORTS:
        errors.append("Неизвестный порядок сортировки.")
    if raw["status"] and raw["status"] not in Rehearsal.Status.values:
        errors.append("Неизвестный статус.")
    queryset = Rehearsal.objects.none() if errors else rehearsal_queryset(filters)
    items = queryset.annotate(band_name=F("band__name"), room_name=F("room__name"))
    page = Paginator(items, 5).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "rehearsals/rehearsal_list.html", {
        "rehearsals": page, "page": page, "params": params.urlencode(), "filters": raw,
        "filter_errors": errors, "rooms": Room.objects.all(), "bands": Band.objects.all(),
        "sort_options": SORT_LABELS.items(), "statuses": Rehearsal.Status.choices,
    })


def rehearsal_detail(request, rehearsal_id):
    queryset = Rehearsal.objects.select_related("room", "band")
    rehearsal = get_object_or_404(queryset, pk=rehearsal_id)
    return render(request, "rehearsals/rehearsal_detail.html", {"rehearsal": rehearsal})


def statistics(request):
    stats = Band.objects.annotate(
        band_name=F("name"),
        rehearsals_count=Count("rehearsals", filter=Q(rehearsals__status=Rehearsal.Status.ACTIVE)),
    ).order_by("-rehearsals_count", "name", "pk")
    totals = Rehearsal.objects.aggregate(
        total=Count("pk", filter=Q(status=Rehearsal.Status.ACTIVE)),
        cancelled=Count("pk", filter=Q(status=Rehearsal.Status.CANCELLED)),
        completed=Count("pk", filter=Q(status=Rehearsal.Status.COMPLETED)),
    )
    return render(request, "rehearsals/statistics.html", {"statistics": stats, "totals": totals})
