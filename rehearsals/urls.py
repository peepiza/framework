"""Маршруты приложения rehearsals."""
from django.urls import path
from . import views

app_name = "rehearsals"

urlpatterns = [
    # Список всех репетиций
    path("", views.rehearsals, name="rehearsals"),
    
    # Статистика (должна идти ДО маршрута с ID, чтобы "statistics" не воспринималось как число)
    path("statistics/", views.statistics, name="statistics"),
    
    # Детальная страница репетиции
    path("<int:rehearsal_id>/", views.rehearsal_detail, name="rehearsal_detail"),
]