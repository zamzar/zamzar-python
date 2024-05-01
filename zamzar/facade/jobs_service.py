from pathlib import Path
from typing import Union
from urllib.parse import urlparse

from zamzar.api import JobsApi
from zamzar.facade.job_manager import JobManager
from zamzar.models import Job
from zamzar.pagination import Paged
from .successful_jobs_service import SuccessfulJobsService
from .. import ApiException


class JobsService:

    @staticmethod
    def _infer_filename(source: str, source_format: str) -> str:
        path = urlparse(source).path
        filename = Path(path).name

        if not filename:
            raise ApiException(f"Could not infer filename from URL ({source}). Provide a URL that contains a path.")

        if "." in filename:
            return filename

        if source_format:
            return f"{filename}.{source_format}"

        raise ApiException(f"Could not infer filename from URL ({source}). Provide an extension to disambiguate.")

    @staticmethod
    def __is_url(string: str) -> bool:
        result = urlparse(string)
        return all([result.scheme, result.netloc])

    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = JobsApi(client)
        self.successful = SuccessfulJobsService(self._zamzar, client)

    def cancel(self, job_id) -> JobManager:
        return self.__to_job(self._api.cancel_job_by_id(job_id, _request_timeout=self._zamzar.timeout))

    def create(
            self,
            source: Union[Path, str, int],
            target_format,
            source_format=None,
            export_url=None,
            options=None
    ) -> JobManager:
        job = self._api.submit_job(
            source_file=self.__prepare_source(source, source_format),
            target_format=target_format,
            source_format=source_format,
            export_url=export_url,
            options=options,  # FIXME pass through
            _request_timeout=self._zamzar.timeout,
        )
        return JobManager(self._zamzar, job)

    def find(self, job_id) -> JobManager:
        return self.__to_job(self._api.get_job_by_id(job_id, _request_timeout=self._zamzar.timeout))

    def list(self, anchor=None, limit=None) -> Paged[JobManager]:
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_jobs(
            after=after,
            before=before,
            limit=limit,
            _request_timeout=self._zamzar.timeout
        )
        jobs = [self.__to_job(job) for job in (response.data or [])]
        return Paged(self, jobs, response.paging)

    def __to_job(self, model: Job):
        return JobManager(self._zamzar, model)

    def __prepare_source(self, source, source_format):
        if isinstance(source, int):
            source_file_id = source
        elif isinstance(source, str) and self.__is_url(source):
            filename = JobsService._infer_filename(source, source_format)
            source_file_id = self._zamzar.imports.start(source, filename).await_completion().get_imported_file().id
        elif Path(source).exists():
            source_file_id = self._zamzar.upload(source).id
        else:
            raise ValueError(f"Source {source} is not a valid URL or file path")
        return source_file_id
