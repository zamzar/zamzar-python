from zamzar.api import JobsApi
from zamzar.facade.job_manager import JobManager


class JobsService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = JobsApi(client)

    def create(
            self,
            source,
            target_format,
            source_format=None,
            export_url=None,
            options=None
    ) -> JobManager:
        source_file_id = self._zamzar.upload(source).id
        job = self._api.submit_job(
            _request_timeout=self._zamzar.timeout,
            source_file=source_file_id,
            target_format=target_format,
            source_format=source_format,
            export_url=export_url,
            options=None  # FIXME pass through
        )
        return JobManager(self._zamzar, job)

    def find(self, job_id) -> JobManager:
        return JobManager(self._zamzar, self._api.get_job_by_id(job_id))
