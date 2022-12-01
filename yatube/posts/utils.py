from django.core.paginator import Paginator


def get_page(request, item, limit):
    paginator = Paginator(item, limit)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
