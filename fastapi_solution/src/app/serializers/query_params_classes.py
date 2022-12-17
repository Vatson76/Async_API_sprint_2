from fastapi.params import Query

from app.core.config import settings


class PaginationDataParams:
    def __init__(
        self,
        sort: str = Query('', description='Sorting by imdb_rating', regex='^-?imdb_rating$'),
        page_size: int = Query(settings.DEFAULT_PAGE_SIZE, description='Number of filmworks on page',
                               alias='page[size]', ge=1),
        page: int = Query(settings.DEFAULT_PAGE_NUMBER, description='Page number', alias='page[number]', ge=1)
    ):
        self.sort = sort
        self.page_size = page_size
        self.page = page
