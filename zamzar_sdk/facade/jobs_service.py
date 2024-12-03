from pathlib import Path
from typing import Union, Optional, Any, Dict
from urllib.parse import urlparse

from zamzar_sdk.api import JobsApi
from zamzar_sdk.facade.job_manager import JobManager
from zamzar_sdk.models import Job
from zamzar_sdk.pagination import Paged, Anchor
from .successful_jobs_service import SuccessfulJobsService
from .. import ApiException
from ..api_client import ApiClient


class JobsService:
    """Starts jobs -- and retrieves information about existing jobs -- on the Zamzar API servers."""

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

    def __init__(self, zamzar, client: ApiClient):
        self._zamzar = zamzar
        self._api = JobsApi(client)
        self.successful = SuccessfulJobsService(self._zamzar, client)

    def cancel(self, job_id: int) -> JobManager:
        """Immediately cancels a job by its ID."""
        return self.__to_job(self._api.cancel_job_by_id(job_id))

    def create(
            self,
            source: Union[Path, str, int],
            target_format: str,
            source_format: Optional[str] = None,
            export_url: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None
    ) -> JobManager:
        """
        Starts a job to convert a local file, returning once the job has been created. Call `await_completion` on the
        returned JobManager to wait for the job to complete.

        :param source: the path to the file to convert, the ID of the file to convert, or the URL of the file to convert
        :param target_format: the format to convert the file to
        :param source_format: the format of the file to convert (defaults to the extension of the source)
        :param export_url: an optional URL to which to export the converted file
        :param options: optional parameters to customize the conversion
        """
        job = self._api.submit_job(
            source_file=self.__prepare_source(source, source_format),
            target_format=target_format,
            source_format=source_format,
            export_url=export_url,
            options=options,
        )
        return JobManager(self._zamzar, job)

    def find(self, job_id: int) -> JobManager:
        """Retrieves a job by its ID."""
        return self.__to_job(self._api.get_job_by_id(job_id))

    def list(self, anchor: Optional[Anchor] = None, limit: Optional[int] = None) -> Paged[JobManager]:
        """
        Retrieves a list of jobs.

        :param anchor: indicates the position in the list from which to start retrieving jobs
        :param limit: indicates the maximum number of jobs to retrieve
        """
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_jobs(after=after, before=before, limit=limit)
        jobs = [self.__to_job(job) for job in (response.data or [])]
        return Paged(self, jobs, response.paging)

    def __to_job(self, model: Job) -> JobManager:
        return JobManager(self._zamzar, model)

    def __prepare_source(self, source, source_format) -> int:
        if isinstance(source, int):
            source_file_id = source
        elif isinstance(source, str) and self.__is_url(source):
            filename = JobsService._infer_filename(source, source_format)
            source_file_id = self._zamzar.imports.start(source, filename).await_completion().imported_file.id
        elif Path(source).exists():
            source_file_id = self._zamzar.upload(source).id
        else:
            raise ValueError(f"Source {source} is not a valid URL or file path")
        return source_file_id
