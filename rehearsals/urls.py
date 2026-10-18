"""Маршруты приложения rehearsals."""
from django.urls import path
from . import views

app_name = "rehearsals"

urlpatterns = [
    path("", views.rehearsals, name="rehearsals"),
    path("<int:rehearsal_id>/", views.rehearsal_detail, name="rehearsal_detail"),
]
