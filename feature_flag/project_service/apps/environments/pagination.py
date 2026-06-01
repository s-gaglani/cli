from rest_framework.pagination import PageNumberPagination


class ProjectPagination(PageNumberPagination):
    """Pagination for Project list endpoints."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class EnvironmentPagination(PageNumberPagination):
    """Pagination for Environment list endpoints."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
