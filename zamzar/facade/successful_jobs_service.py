from zamzar.api import JobsApi
from zamzar.facade.job_manager import JobManager
from zamzar.facade.pagination import Paged
from zamzar.models import Job


class SuccessfulJobsService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = JobsApi(client)

    def list(self, anchor=None, limit=None) -> Paged[JobManager]:
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_successful_jobs(
            after=after,
            before=before,
            limit=limit,
            _request_timeout=self._zamzar.timeout
        )
        jobs = [self.__to_job(job) for job in (response.data or [])]
        return Paged(self, jobs, response.paging)

    def __to_job(self, model: Job):
        return JobManager(self._zamzar, model)
