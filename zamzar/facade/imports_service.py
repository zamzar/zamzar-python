from typing import Optional

from zamzar.api import ImportsApi
from zamzar.models.model_import import ModelImport
from zamzar.pagination import Paged, Anchor
from .import_manager import ImportManager
from ..api_client import ApiClient


class ImportsService:
    """Starts imports -- and retrieves information about existing imports -- on the Zamzar API servers."""

    def __init__(self, zamzar, client: ApiClient):
        self._zamzar = zamzar
        self._api = ImportsApi(client)

    def find(self, import_id: int) -> ImportManager:
        """Retrieves an import request by its ID."""
        return self.__to_import(self._api.get_import_by_id(import_id=import_id))

    def list(self, anchor: Optional[Anchor] = None, limit: Optional[int] = None) -> Paged[ImportManager]:
        """
        Retrieves a list of import requests.

        :param anchor: indicates the position in the list from which to start retrieving import requests
        :param limit: indicates the maximum number of import requests to retrieve
        """
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_imports(after=after, before=before, limit=limit)
        imports = [self.__to_import(_import) for _import in (response.data or [])]
        return Paged(self, imports, response.paging)

    def start(self, url: str, filename: Optional[str] = None) -> ImportManager:
        """
        Starts an import request.

        :param url: the URL of the file to import
        :param filename: the name to give the file on the Zamzar API servers (defaults to the name of the file in the
        path of the URL)
        """
        return self.__to_import(self._api.start_import(url, filename))

    def __to_import(self, model: ModelImport) -> ImportManager:
        return ImportManager(self._zamzar, model)
