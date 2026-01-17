from rest_framework.pagination import PageNumberPagination


class PayoutsPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100
