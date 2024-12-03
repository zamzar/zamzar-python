from typing import Optional

from zamzar_sdk.api import JobsApi
from zamzar_sdk.api_client import ApiClient
from zamzar_sdk.facade.job_manager import JobManager
from zamzar_sdk.models import Job
from zamzar_sdk.pagination import Paged, Anchor


class SuccessfulJobsService:
    """Retrieves information about existing successful jobs on the Zamzar API servers."""

    def __init__(self, zamzar, client: ApiClient):
        self._zamzar = zamzar
        self._api = JobsApi(client)

    def list(self, anchor: Optional[Anchor] = None, limit: Optional[int] = None) -> Paged[JobManager]:
        """
        Retrieves a list of successful jobs.

        :param anchor: indicates the position in the list from which to start retrieving successful jobs
        :param limit: indicates the maximum number of successful jobs to retrieve
        """
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_successful_jobs(after=after, before=before, limit=limit)
        jobs = [self.__to_job(job) for job in (response.data or [])]
        return Paged(self, jobs, response.paging)

    def __to_job(self, model: Job) -> JobManager:
        return JobManager(self._zamzar, model)
