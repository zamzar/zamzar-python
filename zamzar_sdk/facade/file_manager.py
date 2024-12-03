from __future__ import annotations

from pathlib import Path
from typing import Union

from zamzar_sdk.models import File


class FileManager:
    """Provides operations that can be performed on a file resident on the Zamzar API servers."""

    def __init__(self, zamzar, model: File):
        self._zamzar = zamzar
        self.model = model
        self.id = model.id

    def delete(self) -> FileManager:
        """Immediately deletes the file from the Zamzar API servers."""
        self._zamzar.files.delete(self.id)
        return self

    def download(self, target: Union[str, Path]) -> FileManager:
        """Downloads the file to the specified destination, blocking until the download is complete."""
        self._zamzar.files._download_model(self.model, Path(target))
        return self

    def to_str(self) -> str:
        return f"FileManager(id={self.id})"
