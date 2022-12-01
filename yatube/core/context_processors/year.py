from datetime import datetime


def year(request):
    """Добавляет в контекст переменную year с текущим годом."""
    return {
        'year': datetime.now().year
    }
