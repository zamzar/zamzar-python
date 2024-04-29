from typing import Generic, TypeVar

from zamzar.models import PagingNumeric

T = TypeVar('T')


class Paging(Generic[T]):
    def __init__(self, first: T, last: T, limit: int):
        self.first = first
        self.last = last
        self.limit = limit

    @classmethod
    def from_numeric(cls, paging: PagingNumeric) -> 'Paging[int]':
        return cls(paging.first, paging.last, paging.limit)
