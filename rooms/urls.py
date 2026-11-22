"""Маршруты приложения rooms."""
from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path("", views.rooms, name="rooms"),
    path("available/", views.available_rooms, name="available"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
    path("<int:room_id>/photo/", views.room_image, name="room_image"),
    path("<slug:slug>/", views.room_by_slug, name="room_slug"),
]
