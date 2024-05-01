from typing import Optional

from urllib3 import BaseHTTPResponse, PoolManager, Timeout, Retry


# Wraps a PoolManager and:
#   - keeps track of the latest response
#   - adds our timeout and retry configuration to every request
class ZamzarPoolManager(PoolManager):
    def __init__(self, delegate: PoolManager, timeout: Timeout, retries: Retry):
        super().__init__()
        self.delegate = delegate
        self.timeout = timeout
        self.retries = retries
        self.latest_response: Optional[BaseHTTPResponse] = None

    def request(self, method, url, *args, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = self.timeout
        if kwargs.get("retries") is None:
            kwargs["retries"] = self.retries
        self.latest_response = self.delegate.request(method, url, *args, **kwargs)
        return self.latest_response

    def get_header_from_latest_response(self, name, default=None):
        if self.latest_response is None:
            return default
        return self.latest_response.headers.get(name, default)

    def __getattr__(self, name):
        # Delegate all attribute accesses to the delegate object
        return getattr(self.delegate, name)
