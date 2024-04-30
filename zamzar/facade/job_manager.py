import zipfile
from pathlib import Path
from typing import Optional

from zamzar.models import Failure
from zamzar.models import File
from zamzar.models import Job
from .internal import Awaitable
from .job_status import JobStatus
from .. import ApiException


class JobManager(Awaitable):
    __TERMINAL_STATUSES = [JobStatus.SUCCESSFUL.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]
    __TERMINAL_EXPORT_STATUSES = [JobStatus.SUCCESSFUL.value, JobStatus.FAILED.value]

    @staticmethod
    def __extract(path: Path):
        try:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(path.parent)
        except zipfile.BadZipFile:
            raise ApiException("Could not extract target zip file, it may be corrupted or not a zip file")

    def __init__(self, zamzar, model: Job):
        self._zamzar = zamzar
        self.model = model
        self.id = model.id
        self.source_file_id = model.source_file.id
        self.target_files = model.target_files
        self.target_file_ids = [target_file.id for target_file in model.target_files] if model.target_files else []

    def delete_all_files(self) -> id:
        self.delete_source_file()
        self.delete_target_files()
        return self

    def delete_source_file(self) -> id:
        self._zamzar.files.delete(self.source_file_id)
        return self

    def delete_target_files(self) -> id:
        for target_file_id in self.target_file_ids:
            self._zamzar.files.delete(target_file_id)
        return self

    def has_completed(self) -> bool:
        return self.__job_has_completed() and self.__all_exports_have_completed()

    def has_succeeded(self) -> bool:
        return self.model.status == JobStatus.SUCCESSFUL.value

    def get_failure(self) -> Optional[Failure]:
        return self.model.failure

    def refresh(self) -> id:
        return self._zamzar.jobs.find(self.id)

    def store(self, target) -> id:
        if not self.target_files:
            raise ApiException("No target files to download")

        source = self.__primary_target_file()
        destination = self._zamzar.files._download_model(source, target)
        if len(self.target_file_ids) > 1:
            JobManager.__extract(destination)
        return self

    def __primary_target_file(self) -> File:
        return self.target_files[0] if len(self.target_files) == 1 else self.__target_file_zip()

    def __target_file_zip(self) -> File:
        try:
            return next(filter(lambda f: f.name.endswith(".zip"), self.target_files))
        except StopIteration:
            raise ApiException("Expected a zip file to be present in the target files, but none was found")

    def __job_has_completed(self):
        return self.model.status in self.__TERMINAL_STATUSES

    def __all_exports_have_completed(self) -> bool:
        # If there's no export URL, no exports have been requested => they are all complete
        if not self.model.export_url:
            return True

        # If we're expecting exports but none have been created => they are not yet complete
        if not self.model.exports:
            return False

        # Return true if and only if all exports have completed
        return all(export.status in self.__TERMINAL_EXPORT_STATUSES for export in self.model.exports)
