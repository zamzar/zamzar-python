from typing import TypeVar, Generic, List

from .anchor import after, before
from .paging import Paging

ID = TypeVar('ID')
ITEM = TypeVar('ITEM')


class Paged(Generic[ITEM, ID]):
    def __init__(
            self,
            lister,
            items: List[ITEM],
            paging: Paging[ID],
    ):
        self._lister = lister
        self._items = items
        self._paging = paging

    def get_items(self):
        return self._items

    def next_page(self):
        return self._lister.list(anchor=after(self._paging.last), limit=self._paging.limit)

    def previous_page(self):
        return self._lister.list(anchor=before(self._paging.first), limit=self._paging.limit)
