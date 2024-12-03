import os
from pathlib import Path
from typing import Union, Optional

from zamzar_sdk.api import FilesApi
from zamzar_sdk.api_client import ApiClient
from zamzar_sdk.facade.file_manager import FileManager
from zamzar_sdk.models import File
from zamzar_sdk.pagination import Paged, Anchor


class FilesService:
    """Uploads to, downloads from, and retrieves files on the Zamzar API servers."""

    def __init__(self, zamzar, client: ApiClient):
        self._zamzar = zamzar
        self._api = FilesApi(client)

    def delete(self, file_id: int) -> FileManager:
        """
        Immediately deletes a file from the Zamzar API servers.
        """
        return self.__to_file(self._api.delete_file_by_id(file_id=file_id))

    def download(self, file_id: int, target: Union[str, Path]) -> FileManager:
        """
        Downloads a file to the specified destination. Blocks until the download is complete.
        """
        return self.find(file_id).download(Path(target))

    def find(self, file_id: int) -> FileManager:
        """Retrieves a file by its ID."""
        return self.__to_file(self._api.get_file_by_id(file_id=file_id))

    def list(self, anchor: Optional[Anchor] = None, limit: Optional[int] = None) -> Paged[FileManager]:
        """
        Retrieves a list of files.

        :param anchor: indicates the position in the list from which to start retrieving files
        :param limit: indicates the maximum number of files to retrieve
        """
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_files(after=after, before=before, limit=limit)
        files = [self.__to_file(file) for file in (response.data or [])]
        return Paged(self, files, response.paging)

    def upload(self, source: Union[str, Path], name: Optional[str] = None) -> FileManager:
        """
        Uploads a file to the Zamzar API servers. Blocks until the upload is complete.

        :param source: the path to the file to upload
        :param name: the name to give the file on the Zamzar API servers (defaults to the name of the file at the
        source path)
        """
        file = self._api.upload_file(content=os.fspath(Path(source)), name=name)
        return FileManager(self._zamzar, file)

    def _download_model(self, model: File, target: Path) -> Path:
        if target.is_dir():
            name = model.name if model.name else f"{model.id}"
            target = target / name

        with open(target, "wb") as file:
            file.write(self._api.get_file_content_by_id(file_id=model.id))

        return target

    def __to_file(self, model: File) -> FileManager:
        return FileManager(self._zamzar, model)
