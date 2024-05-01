from enum import Enum
from typing import Optional

import urllib3

from zamzar.api_client import ApiClient
from zamzar.configuration import Configuration
from ._internal import ZamzarPoolManager
from .account_service import AccountService
from .file_manager import FileManager
from .files_service import FilesService
from .formats_service import FormatsService
from .imports_service import ImportsService
from .job_manager import JobManager
from .jobs_service import JobsService
from .welcome_service import WelcomeService


class Environment(Enum):
    PRODUCTION = "https://api.zamzar.com"
    SANDBOX = "https://sandbox.zamzar.com"


DEFAULT_RETRY_POLICY = urllib3.Retry(
    # Retry all HTTP methods
    allowed_methods=None,
    # Exponential backoff at 2^x seconds (i.e., 1s, 2s, 4s, 8s, 16s, ...)
    backoff_factor=1,
    # Never exceed 60 seconds between retries
    backoff_max=60,
    # Return the response once all retries have been exhausted
    raise_on_status=False,
    # Respect the Retry-After header if present
    respect_retry_after_header=True,
    # Retry on these status codes
    status_forcelist=[429, 502, 503, 504],
    # Retry at most 10 times (meaning maximum elapsed time of approx. 5 minutes)
    # 1 + 2 + 4 + 8 + 16 + 32 + 60 + 60 + 60 + 60 = 303 seconds
    total=10,
)

HTTP_CONNECTION_TIMEOUT = 15.0
HTTP_READ_TIMEOUT = 30.0
DEFAULT_TIMEOUT_POLICY = urllib3.Timeout(connect=HTTP_CONNECTION_TIMEOUT, read=HTTP_READ_TIMEOUT)

CREDITS_REMAINING_HEADER = "Zamzar-Credits-Remaining";
TEST_CREDITS_REMAINING_HEADER = "Zamzar-Test-Credits-Remaining";


class ZamzarClient:
    def __init__(
            self,
            api_key: str,
            environment: Environment = Environment.PRODUCTION,
            host: Optional[str] = None,
            retries: urllib3.Retry = DEFAULT_RETRY_POLICY,
            timeout: urllib3.Timeout = DEFAULT_TIMEOUT_POLICY,
    ):
        host = host or environment.value
        configuration = Configuration(access_token=api_key, host=host)
        self._client = ApiClient(configuration=configuration)

        # Replace the pool manager with ours (to track the latest request and add timeout/retry configuration)
        self.pool_manager = ZamzarPoolManager(self.pool_manager, timeout, retries)

        self.account = AccountService(self, self._client)
        self.files = FilesService(self, self._client)
        self.formats = FormatsService(self, self._client)
        self.imports = ImportsService(self, self._client)
        self.jobs = JobsService(self, self._client)
        self.welcome = WelcomeService(self, self._client)

    @property
    def timeout(self) -> urllib3.Timeout:
        return self.pool_manager.timeout

    @timeout.setter
    def timeout(self, value: urllib3.Timeout):
        self.pool_manager.timeout = value

    @property
    def retries(self) -> urllib3.Retry:
        return self.pool_manager.retries

    @retries.setter
    def retries(self, value: urllib3.Retry):
        self.pool_manager.retries = value

    @property
    def last_production_credits_remaining(self) -> Optional[int]:
        value = self.pool_manager.get_header_from_latest_response(CREDITS_REMAINING_HEADER, None)
        return int(value) if value is not None else None

    @property
    def last_sandbox_credits_remaining(self) -> Optional[int]:
        value = self.pool_manager.get_header_from_latest_response(TEST_CREDITS_REMAINING_HEADER, None)
        return int(value) if value is not None else None

    @property
    def pool_manager(self):
        return self._client.rest_client.pool_manager

    @pool_manager.setter
    def pool_manager(self, value):
        self._client.rest_client.pool_manager = value

    def convert(
            self,
            source,
            target_format,
            source_format=None,
            export_url=None,
            options=None
    ) -> JobManager:
        return self.jobs \
            .create(source, target_format, source_format, export_url, options) \
            .await_completion()

    def download(self, file_id, target) -> FileManager:
        return self.files.download(file_id, target)

    def get_production_credits_remaining(self) -> int:
        return self.account.get().credits_remaining or 0

    def get_sandbox_credits_remaining(self) -> int:
        return self.account.get().test_credits_remaining or 0

    def test_connection(self) -> str:
        return self.welcome.get()

    def upload(self, source) -> FileManager:
        return self.files.upload(source)
