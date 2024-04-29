import pytest

from zamzar import ApiException


class TestJobManager:
    """Test class for the JobManager module."""

    def test_await(self, zamzar, succeeding_job_id):
        """Test that the JobManager waits for a succeeding job to finish."""
        assert zamzar.jobs.find(succeeding_job_id).await_completion().has_succeeded()
        assert zamzar.jobs.find(succeeding_job_id).await_completion().get_failure() is None
        assert zamzar.jobs.find(succeeding_job_id).await_completion(throw_on_failure=True).has_succeeded()

    def test_await_failing(self, zamzar, failing_job_id):
        assert zamzar.jobs.find(failing_job_id).await_completion().has_failed()
        assert zamzar.jobs.find(failing_job_id).await_completion().get_failure().code is not None
        assert zamzar.jobs.find(failing_job_id).await_completion().get_failure().message is not None
        with pytest.raises(ApiException):
            zamzar.jobs.find(failing_job_id).await_completion(throw_on_failure=True)
