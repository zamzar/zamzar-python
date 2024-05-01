import os
from pathlib import Path

from zamzar.api import FilesApi
from zamzar.facade.file_manager import FileManager
from zamzar.models import File
from zamzar.pagination import Paged


class FilesService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = FilesApi(client)

    def delete(self, file_id) -> FileManager:
        return self.__to_file(self._api.delete_file_by_id(file_id=file_id))

    def download(self, file_id, target: Path) -> FileManager:
        return self.find(file_id).download(target)

    def find(self, file_id) -> FileManager:
        return self.__to_file(self._api.get_file_by_id(file_id=file_id))

    def list(self, anchor=None, limit=None) -> Paged[FileManager]:
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_files(after=after, before=before, limit=limit)
        files = [self.__to_file(file) for file in (response.data or [])]
        return Paged(self, files, response.paging)

    def upload(self, source: Path) -> FileManager:
        file = self._api.upload_file(content=os.fspath(source))
        return FileManager(self._zamzar, file)

    def _download_model(self, model: File, target: Path) -> Path:
        if target.is_dir():
            name = model.name if model.name else f"{model.id}"
            target = target / name

        with open(target, "wb") as file:
            file.write(self._api.get_file_content_by_id(file_id=model.id))

        return target

    def __to_file(self, model: File):
        return FileManager(self._zamzar, model)
