from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.db import OperationalError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import SORTS, RehearsalFilterForm, RehearsalForm
from .models import Band, Rehearsal


def rehearsal_queryset(filters):
    queryset = Rehearsal.objects.all()
    if filters.get("date"):
        queryset = queryset.for_date(filters["date"])
    if filters.get("room"):
        queryset = queryset.filter(room=filters["room"])
    if filters.get("band"):
        queryset = queryset.filter(band=filters["band"])
    status = filters.get("status")
    if status:
        queryset = queryset.filter(status=status)
    if filters.get("q"):
        queryset = queryset.filter(
            Q(band__name__icontains=filters["q"]) | Q(room__name__icontains=filters["q"]),
        )
    return queryset.order_by(*SORTS.get(filters.get("sort"), SORTS["recent"]))


def rehearsals(request):
    form = RehearsalFilterForm(request.GET if request.GET else None)
    queryset = Rehearsal.objects.all()
    if form.is_bound:
        queryset = rehearsal_queryset(form.cleaned_data) if form.is_valid() else queryset.none()
    items = queryset.annotate(band_name=F("band__name"), room_name=F("room__name"))
    page = Paginator(items, 5).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "rehearsals/rehearsal_list.html", {
        "rehearsals": page, "page": page, "params": params.urlencode(), "filter_form": form,
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


def _rehearsal_form(request, rehearsal=None):
    form = RehearsalForm(
        request.POST if request.method == "POST" else None,
        instance=rehearsal,
        initial={"rehearsal_date": timezone.localdate()} if rehearsal is None else None,
    )
    if request.method == "POST":
        try:
            with transaction.atomic():
                if rehearsal is not None:
                    rehearsal.refresh_from_db(fields=["status"])
                if form.is_valid():
                    saved = form.save(commit=False)
                    saved.save(update_fields=form.Meta.fields if rehearsal is not None else None)
                    return redirect("rehearsals:rehearsal_detail", rehearsal_id=saved.pk)
        except OperationalError as error:
            if "locked" not in str(error).lower():
                raise
            form.add_error(None, "База занята. Повторите попытку.")
    return render(request, "rehearsals/rehearsal_form.html", {
        "form": form, "rehearsal": rehearsal,
    })


@permission_required("rehearsals.add_rehearsal", raise_exception=True)
@require_http_methods(["GET", "POST"])
def rehearsal_create(request):
    return _rehearsal_form(request)


@permission_required("rehearsals.change_rehearsal", raise_exception=True)
@require_http_methods(["GET", "POST"])
def rehearsal_edit(request, rehearsal_id):
    rehearsal = get_object_or_404(Rehearsal, pk=rehearsal_id)
    return _rehearsal_form(request, rehearsal)


@permission_required("rehearsals.change_rehearsal", raise_exception=True)
@require_POST
def rehearsal_cancel(request, rehearsal_id):
    rehearsal = get_object_or_404(Rehearsal, pk=rehearsal_id)
    Rehearsal.objects.active().filter(pk=rehearsal.pk).update(status=Rehearsal.Status.CANCELLED)
    return redirect("rehearsals:rehearsal_detail", rehearsal_id=rehearsal.pk)
