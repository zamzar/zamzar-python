import time
from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from typing import Optional

from zamzar import ApiException
from zamzar.models import Failure


class Awaitable(ABC):
    __DEFAULT_BACKOFF = [
        timedelta(milliseconds=100),
        timedelta(milliseconds=100),
        timedelta(milliseconds=200),
        timedelta(milliseconds=500),
        timedelta(milliseconds=1000),
        timedelta(milliseconds=1500),
        timedelta(seconds=2),
        timedelta(seconds=5),
        timedelta(seconds=10),
        timedelta(seconds=30),
        timedelta(seconds=30),
        timedelta(seconds=60)
    ]

    @abstractmethod
    def get_failure(self) -> Optional[Failure]:
        pass

    @abstractmethod
    def has_completed(self) -> bool:
        pass

    @abstractmethod
    def has_succeeded(self) -> bool:
        pass

    @abstractmethod
    def refresh(self):
        pass

    def has_failed(self) -> bool:
        return self.has_completed() and not self.has_succeeded()

    def await_completion(
            self,
            throw_on_failure=False,
            timeout=timedelta(minutes=20),
            backoff=None
    ):
        if backoff is None:
            backoff = Awaitable.__DEFAULT_BACKOFF

        deadline = datetime.now() + timeout
        attempt = 0
        current = self
        while not current.has_completed():
            # Wait for the next backoff period
            wait = backoff[min(attempt, len(backoff) - 1)]
            time.sleep(wait.total_seconds())

            # Blow up if we've waited too long
            if datetime.now() > deadline:
                raise ApiException("Timed out waiting for completion")

            attempt += 1
            current = current.refresh()

        if throw_on_failure and current.has_failed():
            raise ApiException("Waited for completion but failed")

        return current
