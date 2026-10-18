"""Представления для главной страницы и общий каркас."""
from django.http import HttpResponse


def page(title: str, content: str) -> str:
    """Единый HTML-каркас страницы."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body class="bg-light">
    <nav class="nav bg-dark p-3 mb-4">
        <a class="nav-link text-white" href="/">Главная</a>
        <a class="nav-link text-white" href="/rooms/">Помещения</a>
        <a class="nav-link text-white" href="/rehearsals/">Репетиции</a>
    </nav>
    <main class="container">
        {content}
    </main>
</body>
</html>"""


def index(request):
    """Главная страница."""
    content = """
    <div class="p-5 mb-4 bg-white rounded-3 shadow-sm">
        <h1 class="display-5">Сервис планирования репетиций</h1>
        <p class="lead">Приложение для музыкальных групп: управление помещениями
        и расписанием репетиций.</p>
        <hr>
        <a href="/rooms/" class="btn btn-primary btn-lg me-2">Помещения</a>
        <a href="/rehearsals/" class="btn btn-secondary btn-lg">Репетиции</a>
    </div>
    """
    return HttpResponse(page("Главная - Репетиции", content))


def page_not_found(request, exception):
    """Обработчик ошибки 404."""
    content = """
    <div class="text-center mt-5">
        <h1 class="text-danger display-4">404</h1>
        <p class="lead">Страница не найдена.</p>
        <a href="/" class="btn btn-primary">На главную</a>
    </div>
    """
    return HttpResponse(page("404 - Не найдено", content), status=404)
