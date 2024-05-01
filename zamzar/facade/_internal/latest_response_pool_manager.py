from typing import Optional

from urllib3 import BaseHTTPResponse, PoolManager


class LatestResponsePoolManager(PoolManager):
    def __init__(self, delegate: PoolManager):
        super().__init__()
        self.__delegate = delegate
        self.latest_response: Optional[BaseHTTPResponse] = None

    def request(self, method, url, *args, **kwargs):
        self.latest_response = self.__delegate.request(method, url, *args, **kwargs)
        return self.latest_response

    def get_header_from_latest_response(self, name, default=None):
        if self.latest_response is None:
            return default
        return self.latest_response.headers.get(name, default)

    def __getattr__(self, name):
        # Delegate all attribute accesses to the delegate object
        return getattr(self.__delegate, name)
