from enum import Enum
from pathlib import Path
from typing import Optional, Union, Dict, Any

import urllib3

from zamzar_sdk.api_client import ApiClient
from zamzar_sdk.configuration import Configuration
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
    """
    The set of environments available for the Zamzar API.

    PRODUCTION: The production Zamzar API environment; used for production workloads.
    SANDBOX: The sandbox Zamzar API environment; used for testing and development.
    """
    PRODUCTION = "https://api.zamzar.com/v1"
    SANDBOX = "https://sandbox.zamzar.com/v1"


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
    """
    The primary entrypoint for making request against the Zamzar API.

    The client will automatically retry failed and timed out HTTP requests. You can customise this behaviour by
    providing urllib3.Retry and urllib3.Timeout objects to the client on instantiation.

    Example usage:

        ```python
        from zamzar_sdk import ZamzarClient

        zamzar_sdk = ZamzarClient("YOUR_API_KEY_GOES_HERE")

        zamzar_sdk \
            .convert("/tmp/example.docx", "pdf") \
            .store("/tmp/") \
            .delete_all_files()
        ```

    See https://developers.zamzar.com/docs for more information on the Zamzar API.
    """

    def __init__(
            self,
            api_key: str,
            environment: Environment = Environment.PRODUCTION,
            host: Optional[str] = None,
            retries: urllib3.Retry = DEFAULT_RETRY_POLICY,
            timeout: urllib3.Timeout = DEFAULT_TIMEOUT_POLICY,
    ):
        """
        Create a new instance of the Zamzar client.

        :param api_key: The API key to use for authenticating requests.
        :param environment: The environment to use for making requests. Defaults to PRODUCTION.
        :param host: The host to use for making requests. Used when mocking the API.
        :param retries: The retry policy to use for making requests. Defaults to a reasonable exponential backoff.
        :param timeout: The timeout policy to use for making requests. Defaults to 15s connect and 30s read.
        """
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
        """
         Returns the remaining production credits for the last request made by the client.
         Will return None if no successful request has been made yet.
        """
        value = self.pool_manager.get_header_from_latest_response(CREDITS_REMAINING_HEADER, None)
        return int(value) if value is not None else None

    @property
    def last_sandbox_credits_remaining(self) -> Optional[int]:
        """
        Returns the remaining sandbox credits for the last request made by the client.
        Will return None if no successful request has been made yet.
        """
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
            source: Union[Path, str, int],
            target_format: str,
            source_format: Optional[str] = None,
            export_url: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None
    ) -> JobManager:
        """
        Converts a local file to the specified format, blocking until the conversion is complete.

        :param source: the path to the file to convert, the ID of the file to convert, or the URL of the file to convert
        :param target_format: the format to convert the file to
        :param source_format: the format of the file to convert (defaults to the extension of the source)
        :param export_url: an optional URL to which to export the converted file
        :param options: optional parameters to customize the conversion

        Example usage:

                    ```python
                    zamzar_sdk = ZamzarClient("YOUR_API_GOES_HERE")

                    zamzar_sdk.convert("path/to/source.pdf", "jpg").store("path/to/destination.jpg).delete_all_files()
                    ```
        """
        return self.jobs \
            .create(source, target_format, source_format, export_url, options) \
            .await_completion()

    def download(self, file_id: int, target: Union[str, Path]) -> FileManager:
        """
        Downloads a file from Zamzar's API servers to the given destination, blocking until the download is complete.

        :param source: the path to the file to upload
        :param name: the name to give the file on the Zamzar API servers (defaults to the name of the file at the
        source path)

        Example usage:

                ```python
                zamzar_sdk = ZamzarClient("YOUR_API_KEY_GOES_HERE")

                zamzar_sdk.download(1234, "path/to/destination.jpg")
                ```
        """
        return self.files.download(file_id, Path(target))

    def get_production_credits_remaining(self) -> int:
        """Makes a request to the API to retrieve the remaining production credits for the client's API key."""
        return self.account.get().credits_remaining or 0

    def get_sandbox_credits_remaining(self) -> int:
        """Makes a request to the API to retrieve the remaining sandbox credits for the client's API key."""
        return self.account.get().test_credits_remaining or 0

    def test_connection(self) -> str:
        """Checks whether the client can connect to the Zamzar API; useful for testing your API key."""
        return self.welcome.get()

    def upload(self, source: Union[str, Path], name: Optional[str] = None) -> FileManager:
        """
        Uploads a local file to Zamzar's API servers with the given name, blocking until the upload is complete.

        :param source: the path to the file to upload
        :param name: the name to give the file on the Zamzar API servers (defaults to the name of the file at the
        source path)

        Example usage:

                ```python
                zamzar_sdk = ZamzarClient("YOUR_API_KEY_GOES_HERE")

                uploaded_file_id = zamzar_sdk.upload("path/to/source", "source.pdf").id
                ```
        """
        return self.files.upload(source, name)
