import pytest

from test.facade.assertions import assert_non_empty_file
from zamzar import ApiException


class TestJobManager:
    """Test class for the JobManager module."""

    def test_await(self, zamzar, succeeding_job_id):
        """Test that the JobManager waits for a succeeding job to finish."""
        assert zamzar.jobs.find(succeeding_job_id).await_completion().has_succeeded()
        assert zamzar.jobs.find(succeeding_job_id).await_completion().failure is None
        assert zamzar.jobs.find(succeeding_job_id).await_completion(throw_on_failure=True).has_succeeded()

    def test_await_respects_exports(self, zamzar, succeeding_multi_output_job_id):
        """Test that the JobManager respects exports."""
        finished_job_with_exports = zamzar.jobs.find(succeeding_multi_output_job_id).await_completion()
        assert len(finished_job_with_exports.model.exports) > 0, "Sanity check: there should be at least 1 export"
        for export in finished_job_with_exports.model.exports:
            assert export.status == "successful" or export.status == "failed"

    def test_await_failing(self, zamzar, failing_job_id):
        assert zamzar.jobs.find(failing_job_id).await_completion().has_failed()
        assert zamzar.jobs.find(failing_job_id).await_completion().failure.code is not None
        assert zamzar.jobs.find(failing_job_id).await_completion().failure.message is not None
        with pytest.raises(ApiException):
            zamzar.jobs.find(failing_job_id).await_completion(throw_on_failure=True)

    def test_throw_when_awaited_not_found(self, zamzar, mock_server, succeeding_job_id):
        """Test that an ApiException is thrown when a job is not found."""
        job = zamzar.jobs.find(succeeding_job_id)
        mock_server.destroy(f"/jobs/{succeeding_job_id}")
        with pytest.raises(ApiException):
            job.await_completion()

    def test_store_multi_file_job(self, zamzar, succeeding_multi_output_job_id, tmp_path):
        """Test that a multi-file job can be stored."""
        output = tmp_path / "output"

        job = zamzar.jobs.find(succeeding_multi_output_job_id)
        job.await_completion().store(output)
        assert_non_empty_file(output)

        pngs = list(tmp_path.glob('*.png'))
        assert len(pngs) == 3
        for png in pngs:
            assert_non_empty_file(png)

    def test_store_multi_file_job_to_directory(self, zamzar, succeeding_multi_output_job_id, tmp_path):
        """Test that a multi-file job can be stored to a directory."""
        pngs = list(tmp_path.glob('*.png'))
        assert len(pngs) == 0, "Sanity check: expected output files not to exist yet"

        job = zamzar.jobs.find(succeeding_multi_output_job_id)
        job.await_completion().store(tmp_path)
        pngs = list(tmp_path.glob('*.png'))
        assert len(pngs) == 3
        for png in pngs:
            assert_non_empty_file(png)

    def test_store_multi_file_job_no_extract(self, zamzar, succeeding_multi_output_job_id, tmp_path):
        """Test that a multi-file job can be stored without extracting the ZIP file."""
        output = tmp_path / "output.zip"

        job = zamzar.jobs.find(succeeding_multi_output_job_id)
        job.await_completion().store(output, extract_multiple_file_output=False)
        assert_non_empty_file(output)

        # The PNG files should NOT exist since we did not extract the ZIP
        pngs = list(tmp_path.glob('*.png'))
        assert len(pngs) == 0

    def test_store_throws_when_no_target_files(self, zamzar, failing_job_id, tmp_path):
        """Test that an exception is thrown when trying to store a job with no target files."""
        with pytest.raises(ApiException):
            zamzar.jobs.find(failing_job_id).await_completion().store(tmp_path)
