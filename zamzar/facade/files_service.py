import os
from pathlib import Path

from zamzar.api import FilesApi
from zamzar.facade.file_manager import FileManager
from zamzar.facade.pagination import Paged
from zamzar.models import File


class FilesService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = FilesApi(client)

    def delete(self, file_id) -> FileManager:
        return self.__to_file(self._api.delete_file_by_id(file_id=file_id, _request_timeout=self._zamzar.timeout))

    def download(self, file_id, target: Path) -> Path:
        return self.find(file_id).download(target)

    def find(self, file_id) -> FileManager:
        return self.__to_file(self._api.get_file_by_id(file_id=file_id, _request_timeout=self._zamzar.timeout))

    def list(self, anchor=None, limit=None) -> Paged[FileManager]:
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_files(
            after=after,
            before=before,
            limit=limit,
            _request_timeout=self._zamzar.timeout
        )
        files = [self.__to_file(file) for file in response.data]
        return Paged(self, files, response.paging)

    def upload(self, file: Path) -> FileManager:
        file = self._api.upload_file(content=os.fspath(file), _request_timeout=self._zamzar.timeout)
        return FileManager(self._zamzar, file)

    def _download_model(self, model: File, target: Path) -> Path:
        if target.is_dir():
            name = model.name if model.name else model.id
            target = target / name

        with open(target, "wb") as file:
            file.write(self._api.get_file_content_by_id(file_id=model.id, _request_timeout=self._zamzar.timeout))

        return target

    def __to_file(self, model: File):
        return FileManager(self._zamzar, model)
