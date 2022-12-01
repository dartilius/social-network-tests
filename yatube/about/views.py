from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Страница о Авторе."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Страница технологии."""
    template_name = 'about/tech.html'
