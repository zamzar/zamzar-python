from zamzar.api import FormatsApi
from zamzar.api_client import ApiClient
from zamzar.models.format import Format
from zamzar.pagination import Paged


class FormatsService:
    """Retrieves information about the file formats supported by the Zamzar API."""

    def __init__(self, zamzar, client: ApiClient):
        self._zamzar = zamzar
        self._api = FormatsApi(client)

    def find(self, name: str) -> Format:
        """Retrieves a file format by its name."""
        return self._api.get_format_by_id(format=name)

    def list(self, anchor=None, limit=None) -> Paged[Format]:
        """
        Retrieves a list of file formats.

        :param anchor: indicates the position in the list from which to start retrieving file formats
        :param limit: indicates the maximum number of file formats to retrieve
        """
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_formats(after=after, before=before, limit=limit)
        return Paged(self, (response.data or []), response.paging)
