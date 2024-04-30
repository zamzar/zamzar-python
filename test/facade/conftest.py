from urllib.parse import urlparse

import pytest
import urllib3

from zamzar import ZamzarClient


@pytest.fixture()
def test_host() -> str:
    return "http://mock:8080/v1"


@pytest.fixture()
def api_key() -> str:
    return "GiVUYsF4A8ssq93FR48H"


@pytest.fixture
def zamzar(api_key, test_host) -> ZamzarClient:
    return ZamzarClient(api_key=api_key, host=test_host)


@pytest.fixture
def succeeding_import_id() -> int:
    """The ID of an import that is guaranteed to succeed in the mock server."""
    return 1


@pytest.fixture
def failing_import_id() -> int:
    """The ID of an import that is guaranteed to fail in the mock server."""
    return 2


@pytest.fixture
def succeeding_job_id() -> int:
    """The ID of a job that is guaranteed to succeed in the mock server."""
    return 1


@pytest.fixture
def succeeding_multi_output_job_id() -> int:
    """The ID of a job that is guaranteed to succeed in the mock server and have multiple outputs."""
    return 2


@pytest.fixture
def failing_job_id() -> int:
    """The ID of a job that is guaranteed to fail in the mock server."""
    return 3


@pytest.fixture
def file_id() -> int:
    """The ID of a file that is guaranteed to exist in the mock server."""
    return 1


@pytest.fixture
def mock_server(api_key, test_host):
    return MockServer(api_key=api_key, api_url=test_host)


@pytest.fixture(autouse=True)
def reset_mock(mock_server):
    mock_server.reset()


class MockServer:
    def __init__(self, api_key, api_url):
        self._api_url = api_url
        self._base_url = MockServer.__base_url(api_url)
        self._http = urllib3.PoolManager()
        self._headers = {'Authorization': f'Bearer {api_key}'}

    def destroy(self, path: str):
        destroy_endpoint = f'{self._api_url}{path}/destroy'
        response = self._http.request("POST", destroy_endpoint, headers=self._headers)
        assert response.status == 200, f"Failed to destroy resource ({path}): {response.data}"

    def reset(self):
        reset_endpoint = f'{self._base_url}/__admin/scenarios/reset'
        response = self._http.request("POST", reset_endpoint, headers=self._headers)
        assert response.status == 200, f"Failed to reset mock server: {response.data}"

    @staticmethod
    def __base_url(host: str) -> str:
        """Return the base of a URL, for example http://foo.com:8080/bar?baz becomes http://foo.com:8080"""
        parsed = urlparse(host)
        parsed = parsed._replace(fragment="")
        parsed = parsed._replace(path="")
        parsed = parsed._replace(params="")
        parsed = parsed._replace(query="")
        return parsed.geturl()
