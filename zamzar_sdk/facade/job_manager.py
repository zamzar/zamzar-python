from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Optional, Union

from zamzar_sdk.models import Failure
from zamzar_sdk.models import File
from zamzar_sdk.models import Job
from ._internal import Awaitable
from .job_status import JobStatus
from .. import ApiException


class JobManager(Awaitable):
    """Provides operations that can be performed on a job running on the Zamzar API servers."""

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
        self.target_files = model.target_files

    def delete_all_files(self) -> JobManager:
        """Immediately deletes the source file and all target files from the Zamzar API servers."""
        self.delete_source_file()
        self.delete_target_files()
        return self

    def delete_source_file(self) -> JobManager:
        """Immediately deletes the source file from the Zamzar API servers."""
        if self.source_file_id:
            self._zamzar.files.delete(self.source_file_id)
        return self

    def delete_target_files(self) -> JobManager:
        """Immediately deletes all target files from the Zamzar API servers."""
        for target_file_id in self.target_file_ids:
            self._zamzar.files.delete(target_file_id)
        return self

    def has_completed(self) -> bool:
        """Indicates whether the job has completed."""
        return self.__job_has_completed() and self.__all_exports_have_completed()

    def has_succeeded(self) -> bool:
        """ Indicates whether the job has successfully completed."""
        return self.model.status == JobStatus.SUCCESSFUL.value

    @property
    def failure(self) -> Optional[Failure]:
        """If the job has failed, returns the reason for the failure."""
        return self.model.failure

    def refresh(self) -> JobManager:
        """Performs an API request to determine the current state of the job."""
        return self._zamzar.jobs.find(self.id)

    @property
    def source_file_id(self) -> Optional[int]:
        """Returns the ID of the source file being converted."""
        return self.model.source_file.id if self.model.source_file else None

    def store(self, target: Union[str, Path]) -> JobManager:
        """
        Downloads all the target files produced by the conversion to the specified destination, blocking until the
        download is complete.
        """
        source = self.__primary_target_file()
        target = Path(target)
        destination = self._zamzar.files._download_model(source, target)
        if len(self.target_file_ids) > 1:
            JobManager.__extract(destination)
        return self

    @property
    def target_file_ids(self) -> list[int]:
        """Returns the IDs of the target files produced by the job."""
        return [target_file.id for target_file in self.model.target_files] if self.model.target_files else []

    def __primary_target_file(self) -> File:
        if not self.target_files:
            raise ApiException("No target files to download")

        return self.target_files[0] if len(self.target_files) == 1 else self.__target_file_zip()

    def __target_file_zip(self) -> File:
        if not self.target_files:
            raise ApiException("No target files to download")

        try:
            return next(filter(lambda f: f.name.endswith(".zip"), self.target_files))
        except StopIteration:
            raise ApiException("Expected a zip file to be present in the target files, but none was found")

    def __job_has_completed(self) -> bool:
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

    def to_str(self) -> str:
        return f"JobManager(id={self.id})"
