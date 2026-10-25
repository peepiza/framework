"""Маршруты приложения rooms."""
from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path("", views.rooms, name="rooms"),
    path("available/", views.available_rooms, name="available"),
    # Добавьте вот эту строку:
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]