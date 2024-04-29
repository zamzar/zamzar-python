from typing import Optional

from zamzar.models import Failure
from zamzar.models import ModelImport
from .file_manager import FileManager
from .internal import Awaitable
from .job_status import JobStatus


class ImportManager(Awaitable):
    __TERMINAL_STATUSES = [JobStatus.SUCCESSFUL.value, JobStatus.FAILED.value]

    def __init__(self, zamzar, model: ModelImport):
        self._zamzar = zamzar
        self.model = model
        self.id = model.id

    def has_completed(self) -> bool:
        return self.model.status in self.__TERMINAL_STATUSES

    def has_succeeded(self) -> bool:
        return self.model.status == JobStatus.SUCCESSFUL.value

    def get_failure(self) -> Optional[Failure]:
        return self.model.failure

    def refresh(self) -> id:
        return self._zamzar.imports.find(self.id)

    def get_imported_file(self) -> FileManager:
        return FileManager(self._zamzar, self.model.file)
