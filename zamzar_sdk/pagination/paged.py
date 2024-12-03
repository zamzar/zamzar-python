from typing import TypeVar, Generic, List, Union, Optional

from zamzar_sdk.models import PagingNumeric, PagingString
from .anchor import after, before

ITEM = TypeVar('ITEM')


class Paged(Generic[ITEM]):
    def __init__(
            self,
            lister,
            items: List[ITEM],
            paging: Union[Optional[PagingNumeric], Optional[PagingString]]
    ):
        if not paging:
            raise ValueError("Paging information is required")

        self._lister = lister
        self._items = items
        self._paging = paging

    @property
    def items(self) -> List[ITEM]:
        return self._items

    def next_page(self):
        return self._lister.list(anchor=after(self._paging.last), limit=self._paging.limit)

    def previous_page(self):
        return self._lister.list(anchor=before(self._paging.first), limit=self._paging.limit)
