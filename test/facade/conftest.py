import json
from http.client import HTTPMessage
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import pytest
import urllib3

from test.facade.tracking_pool_manager import TrackingPoolManager
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
def zamzar_tracked(zamzar) -> ZamzarClient:
    zamzar.pool_manager = TrackingPoolManager(zamzar.pool_manager)
    return zamzar


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
def set_fake_responses(mocker):
    def _set_fake_responses(responses):
        getconn_mock = mocker.patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
        getconn_mock.return_value.getresponse.side_effect = responses

    return _set_fake_responses


@pytest.fixture
def create_mock_response(mocker):
    def _create_mock_response(
            status: int,
            headers: Optional[Dict[str, str]] = None,
            json_body: Optional[Dict[str, Any]] = None
    ):
        if headers is None:
            headers = {}
        if json_body is None:
            json_body = {}
        response = mocker.Mock(status=status, msg=HTTPMessage(), headers=headers)
        response.data = json.dumps(json_body).encode("utf-8")
        # Need to satisfy the urllib3 response interface
        response.get_redirect_location.return_value = None
        return response

    return _create_mock_response


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
        assert response.status == 200, f"Failed to destroy resource ({path})"

    def reset(self):
        reset_endpoint = f'{self._base_url}/__admin/scenarios/reset'
        response = self._http.request("POST", reset_endpoint, headers=self._headers)
        assert response.status == 200, f"Failed to reset mock server"

    @staticmethod
    def __base_url(host: str) -> str:
        """Return the base of a URL, for example http://foo.com:8080/bar?baz becomes http://foo.com:8080"""
        parsed = urlparse(host)
        parsed = parsed._replace(fragment="")
        parsed = parsed._replace(path="")
        parsed = parsed._replace(params="")
        parsed = parsed._replace(query="")
        return parsed.geturl()
