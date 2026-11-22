"""Маршруты приложения rehearsals."""
from django.urls import path
from . import views

app_name = "rehearsals"

urlpatterns = [
    path("", views.rehearsals, name="rehearsals"),
    path("statistics/", views.statistics, name="statistics"),
    path("new/", views.rehearsal_create, name="rehearsal_create"),
    path("<int:rehearsal_id>/", views.rehearsal_detail, name="rehearsal_detail"),
    path("<int:rehearsal_id>/edit/", views.rehearsal_edit, name="rehearsal_edit"),
    path("<int:rehearsal_id>/cancel/", views.rehearsal_cancel, name="rehearsal_cancel"),
]
