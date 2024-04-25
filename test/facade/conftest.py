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
def succeeding_job_id() -> int:
    """The ID of a job that is guaranteed to succeed in the mock server."""
    return 1


@pytest.fixture
def file_id() -> int:
    """The ID of a file that is guaranteed to exist in the mock server."""
    return 1


@pytest.fixture(autouse=True)
def reset_mock(api_key, test_host):
    # Make a POST request to "/__admin/scenarios/reset"
    http = urllib3.PoolManager()
    headers = {'Authorization': f'Bearer {api_key}'}
    reset_endpoint = f'{base_url(test_host)}/__admin/scenarios/reset'
    response = http.request("POST", reset_endpoint, headers=headers)
    assert response.status == 200, f"Failed to reset mock server: {response.data}"


def base_url(host: str) -> str:
    """Return the base of a URL, for example http://foo.com:8080/bar?baz becomes http://foo.com:8080"""
    parsed = urlparse(host)
    parsed = parsed._replace(fragment="")
    parsed = parsed._replace(path="")
    parsed = parsed._replace(params="")
    parsed = parsed._replace(query="")
    return parsed.geturl()
