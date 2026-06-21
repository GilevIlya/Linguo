import math

from api.v1.configs.pagination import pagination_config


class Pagination:
    def __init__(
            self,
            total: int,
            current_page: int,
            per_page: int = pagination_config.DEFAULT_PER_PAGE):
        self.total = total
        self.current_page = current_page
        self.per_page = per_page
    
    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.per_page) if self.per_page else 0
    
    @property
    def has_next(self) -> bool:
        return self.current_page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        return self.current_page > 1
    
    @property
    def next_page(self) -> int | None:
        return self.current_page + 1 if self.has_next else None
    
    @property
    def previous_page(self) -> int | None:
        return self.current_page - 1 if self.has_previous else None
    
    @property
    def start(self) -> int:
        """offset for SQL queries, which specifies how many records to skip before fetching data."""
        return (self.current_page - 1) * self.per_page