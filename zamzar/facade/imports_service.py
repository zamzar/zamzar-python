from typing import Optional

from zamzar.api import ImportsApi
from zamzar.models.model_import import ModelImport
from zamzar.pagination import Paged
from .import_manager import ImportManager


class ImportsService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = ImportsApi(client)

    def find(self, import_id) -> ImportManager:
        return self.__to_import(self._api.get_import_by_id(import_id=import_id))

    def list(self, anchor=None, limit=None) -> Paged[ImportManager]:
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_imports(after=after, before=before, limit=limit)
        imports = [self.__to_import(_import) for _import in (response.data or [])]
        return Paged(self, imports, response.paging)

    def start(self, url: str, filename: Optional[str] = None) -> ImportManager:
        return self.__to_import(self._api.start_import(url, filename))

    def __to_import(self, model: ModelImport):
        return ImportManager(self._zamzar, model)
