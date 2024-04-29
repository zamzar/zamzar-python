from enum import Enum
from typing import Tuple

from zamzar.api_client import ApiClient
from zamzar.configuration import Configuration
from .account_service import AccountService
from .file_manager import FileManager
from .files_service import FilesService
from .formats_service import FormatsService
from .job_manager import JobManager
from .jobs_service import JobsService
from .welcome_service import WelcomeService


class Environment(Enum):
    PRODUCTION = "https://api.zamzar.com"
    SANDBOX = "https://sandbox.zamzar.com"


HTTP_CONNECTION_TIMEOUT = 15.0
HTTP_READ_TIMEOUT = 30.0


class ZamzarClient:
    def __init__(
            self,
            api_key: str,
            environment: Environment = Environment.PRODUCTION,
            host: str = None,
            timeout: Tuple[float, float] = (HTTP_CONNECTION_TIMEOUT, HTTP_READ_TIMEOUT),
    ):
        self.timeout = timeout

        host = host or environment.value
        configuration = Configuration(access_token=api_key, host=host)
        self._client = ApiClient(configuration=configuration)

        self.account = AccountService(self, self._client)
        self.files = FilesService(self, self._client)
        self.formats = FormatsService(self, self._client)
        self.jobs = JobsService(self, self._client)
        self.welcome = WelcomeService(self, self._client)

    def convert(
            self,
            source,
            target_format,
            source_format=None,
            export_url=None,
            options=None
    ) -> JobManager:
        return (
            self.jobs
            .create(
                source=source,
                target_format=target_format,
                source_format=source_format,
                export_url=export_url,
                options=options
            ).await_completion()
        )

    def test_connection(self) -> str:
        return self.welcome.get()

    def upload(self, source) -> FileManager:
        return self.files.upload(source)
