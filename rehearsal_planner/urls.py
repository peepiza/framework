"""Корневая маршрутизация проекта."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("rooms/", include("rooms.urls")),
    path("rehearsals/", include("rehearsals.urls")),
]

# Обработчик 404 ошибки
handler404 = "homepage.views.page_not_found"
