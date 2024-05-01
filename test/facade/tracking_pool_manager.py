from __future__ import annotations

from typing import List

from urllib3 import BaseHTTPResponse, PoolManager


class TrackingPoolManager(PoolManager):
    def __init__(self, delegate: PoolManager):
        super().__init__()
        self.__delegate = delegate
        self.history: List[RequestResponse] = []

    def request(self, method, url, *args, **kwargs):
        response = self.__delegate.request(method, url, *args, **kwargs)
        entry = RequestResponse(HTTPRequest(method, url, kwargs.get("headers", {})), response)
        self.history.append(entry)
        return response

    @property
    def latest(self) -> RequestResponse:
        if not self.history:
            raise ValueError("No requests have been made yet")
        return self.history[-1]

    def __getattr__(self, name):
        # Delegate all attribute accesses to the delegate object
        return getattr(self.__delegate, name)


class RequestResponse:
    def __init__(self, request: HTTPRequest, response: BaseHTTPResponse):
        self.request = request
        self.response = response


class HTTPRequest:
    def __init__(self, method, url, headers):
        self.method = method
        self.url = url
        self.headers = headers
