from datetime import date

from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from rehearsals.models import Rehearsal
from .forms import RoomImageForm
from .models import Room


def rooms(request):
    query = request.GET.get("q", "").strip()
    room_list = Room.objects.all()
    if query:
        room_list = room_list.filter(Q(name__icontains=query) | Q(address__icontains=query))
    return render(request, "rooms/room_list.html", {"rooms": room_list, "query": query})


def available_rooms(request):
    raw_date = request.GET.get("date", "")
    booking_date = None
    error = ""
    room_list = Room.objects.none()
    if raw_date:
        try:
            booking_date = date.fromisoformat(raw_date)
        except ValueError:
            error = "Введите корректную дату."
        else:
            occupied = Rehearsal.objects.active().for_date(booking_date).values("room_id")
            room_list = Room.objects.exclude(pk__in=occupied)
    return render(request, "rooms/available.html", {
        "rooms": room_list, "booking_date": raw_date, "date_error": error,
    })


def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, "rooms/room_detail.html", {"room": room})


def room_by_slug(request, slug):
    room = get_object_or_404(Room, slug=slug)
    return render(request, "rooms/room_detail.html", {"room": room})


@permission_required("rooms.change_room", raise_exception=True)
@require_http_methods(["GET", "POST"])
def room_image(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == "POST":
        form = RoomImageForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save(commit=False)
            room.save(update_fields=["image"])
            return redirect(room)
    else:
        form = RoomImageForm(instance=room)
    return render(request, "rooms/room_image_form.html", {"form": form, "room": room})
