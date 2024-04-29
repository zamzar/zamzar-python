import time
from datetime import timedelta

import pytest

from zamzar import ApiException
from zamzar.facade.internal import Awaitable
from zamzar.models import Failure


class TestAwaitable:
    def test_await_on_failure(self):
        """Test that await_completion() returns or throws on failure."""
        awaitable = ImmediateFailure()
        assert awaitable == awaitable.await_completion()
        with pytest.raises(ApiException):
            awaitable.await_completion(throw_on_failure=True)

    def test_await_throws_when_refresh_throws(self):
        """Test that await_completion() throws if refresh() throws."""
        awaitable = Unrefreshable()
        with pytest.raises(ApiException):
            awaitable.await_completion()

    def test_respects_timeout(self):
        """Test that await_completion() throws if it exceeds the deadline specified via timeout."""
        awaitable = NeverCompletes()
        with pytest.raises(ApiException):
            awaitable.await_completion(timeout=timedelta(seconds=5))

    def test_respects_backoff(self, mocker):
        """Test that await_completion() uses the provided backoff policy."""
        spy = mocker.spy(time, 'sleep')

        backoff = [
            timedelta(milliseconds=5),
            timedelta(milliseconds=10),
            timedelta(milliseconds=20),
        ]
        awaitable = EventualSuccess(succeeds_after=5)
        awaitable.await_completion(timeout=timedelta(seconds=5), backoff=backoff)

        assert spy.call_count == 5, "Expected 5 calls to time.sleep()"
        assert spy.call_args_list == [
            mocker.call(0.005),
            mocker.call(0.01),
            mocker.call(0.02),
            mocker.call(0.02),
            mocker.call(0.02),
        ]


class ImmediateFailure(Awaitable):
    def has_completed(self):
        return True

    def has_succeeded(self):
        return False

    def get_failure(self):
        return Failure()

    def refresh(self):
        return self


class Unrefreshable(Awaitable):
    def has_completed(self):
        return False

    def has_succeeded(self):
        return False

    def get_failure(self):
        return None

    def refresh(self):
        raise ApiException("BOOM!")


class NeverCompletes(Awaitable):
    def has_completed(self):
        return False

    def has_succeeded(self):
        return False

    def get_failure(self):
        return None

    def refresh(self):
        return self


class EventualSuccess(Awaitable):
    def __init__(self, succeeds_after):
        self._succeeds_after = succeeds_after
        self._attempts = 0

    def has_completed(self):
        return self._attempts >= self._succeeds_after

    def has_succeeded(self):
        return self.has_completed()

    def get_failure(self):
        return None

    def refresh(self):
        self._attempts += 1
        return self
