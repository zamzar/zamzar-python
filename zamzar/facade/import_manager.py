from __future__ import annotations

from typing import Optional

from zamzar.models import Failure
from zamzar.models import ModelImport
from ._internal import Awaitable
from .file_manager import FileManager
from .job_status import JobStatus


class ImportManager(Awaitable):
    """Provides operations that can be performed on an import request running on the Zamzar API servers."""

    __TERMINAL_STATUSES = [JobStatus.SUCCESSFUL.value, JobStatus.FAILED.value]

    def __init__(self, zamzar, model: ModelImport):
        self._zamzar = zamzar
        self.model = model
        self.id = model.id

    def has_completed(self) -> bool:
        """Indicates whether the import request has completed."""

        return self.model.status in self.__TERMINAL_STATUSES

    def has_succeeded(self) -> bool:
        """Indicates whether the import request has successfully completed."""
        return self.model.status == JobStatus.SUCCESSFUL.value

    @property
    def failure(self) -> Optional[Failure]:
        """If the import request has failed, returns the reason for the failure."""
        return self.model.failure

    @property
    def imported_file(self) -> FileManager:
        """Returns a file manager for the imported file."""
        if not self.model.file:
            raise ValueError("Import has not completed yet")

        return FileManager(self._zamzar, self.model.file)

    def refresh(self) -> ImportManager:
        """Performs an API request to determine the current state of the import request."""
        return self._zamzar.imports.find(self.id)

    def to_str(self) -> str:
        return f"ImportManager(id={self.id})"
