from __future__ import annotations

from typing import List

from urllib3 import BaseHTTPResponse, PoolManager


class TrackingPoolManager(PoolManager):
    def __init__(self, delegate: PoolManager):
        super().__init__()
        self.__delegate = delegate
        self.history: List[RequestResponse] = []

    def request(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers", {})
        body = kwargs.get("body", None) or kwargs.get("fields", None)
        request = HTTPRequest(method, url, headers, body)
        response = self.__delegate.request(method, url, *args, **kwargs)
        self.history.append(RequestResponse(request, response))
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
    def __init__(self, method, url, headers, body):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def body_contains(self, needle: str) -> bool:
        # if the body is a string, check if the needle is in the body
        if needle in self.body:
            return True

        # if the body is a list of tuples, check each tuple
        if isinstance(self.body, list):
            for item in self.body:
                if needle in item:
                    return True

        return False
