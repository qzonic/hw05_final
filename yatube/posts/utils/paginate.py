from django.core.paginator import Paginator
from ..constants import TEN_POSTS


def paginate(request, query):
    paginator = Paginator(query, TEN_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
