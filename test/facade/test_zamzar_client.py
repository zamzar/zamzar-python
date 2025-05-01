import pytest

from zamzar import Environment, ZamzarClient
from zamzar.exceptions import NotFoundException
from .assertions import assert_non_empty_file


class TestZamzarClient:
    """Test class for the ZamzarClient module."""

    def test_convert_store_delete_all(self, zamzar, tmp_path):
        """Test that the ZamzarClient can convert, store, and delete files."""
        source = tmp_path / "source"
        source.touch()

        target = tmp_path / "target"

        job = zamzar.convert(
            source=source,
            target_format="txt",
            source_format="pdf",
            options={
                "quality": "50",
                "ocr": "true"
            },
            export_url="s3://bucket-name/path/to/export"
        )

        # Now download the converted file
        job.store(target)
        assert_non_empty_file(target)

        # Now delete the source and target files
        job.delete_all_files()
        with pytest.raises(NotFoundException):
            zamzar.files.find(job.source_file_id)

        for target_file_id in job.target_file_ids:
            with pytest.raises(NotFoundException):
                zamzar.files.find(target_file_id)

    def test_upload_convert_download_delete(self, zamzar, tmp_path):
        """Test that the ZamzarClient can upload, convert, download, and delete files."""
        source = tmp_path / "source"
        source.touch()

        target = tmp_path / "target"

        uploaded = zamzar.upload(source)
        job = zamzar.convert(uploaded.id, "txt").await_completion()
        downloaded = zamzar.download(job.target_file_ids[0], target)
        uploaded.delete()
        downloaded.delete()

        assert_non_empty_file(target)

        # Check that source and target have been deleted
        with pytest.raises(NotFoundException):
            zamzar.files.find(job.source_file_id)

        with pytest.raises(NotFoundException):
            zamzar.files.find(job.target_file_ids[0])

    def test_download_and_delete_when_multiple_target_files(self, zamzar, succeeding_multi_output_job_id, tmp_path):
        """Test that the ZamzarClient can download and delete multiple target files."""
        output = tmp_path / "output"

        job = (
            zamzar
            .jobs
            .find(succeeding_multi_output_job_id)
            .await_completion()
            .store(output)
            .delete_all_files()
        )

        # Check that a non-empty file has been downloaded
        assert_non_empty_file(output)

        # Check that the directory contains 3 non-empty pngs
        pngs = list(tmp_path.glob("*.png"))
        assert len(pngs) == 3
        for png in pngs:
            assert_non_empty_file(png)

        # Check that the source and target files no longer exist
        with pytest.raises(NotFoundException):
            zamzar.files.find(job.source_file_id)

        for target_file_id in job.target_file_ids:
            with pytest.raises(NotFoundException):
                zamzar.files.find(target_file_id)

    def test_convert_url_with_source_format(self, zamzar, tmp_path):
        """Test that the ZamzarClient can convert a URL with a source format."""
        output = tmp_path / "output"

        job = zamzar.convert(
            # URLs containing "unknown" cause a 422 from the mock if filename (i.e., source format) is not supplied
            source="https://example.org/unknown",
            source_format="pdf",
            target_format="txt",
        )

        # Now download the converted file
        job.store(output)
        assert_non_empty_file(output)

    def test_can_hit_production(self, api_key):
        """Test that the ZamzarClient returns a welcome message when directed at the production environment."""
        zamzar = ZamzarClient(api_key=api_key, environment=Environment.PRODUCTION)
        assert zamzar.test_connection() is not None, "Should return a welcome message"

    def test_can_hit_sandbox(self, api_key):
        """Test that the ZamzarClient returns a welcome message when directed at the production environment."""
        zamzar = ZamzarClient(api_key=api_key, environment=Environment.SANDBOX)
        assert zamzar.test_connection() is not None, "Should return a welcome message"

    def test_has_user_agent(self, zamzar_tracked):
        """Test that the ZamzarClient sends HTTP requests with a user agent."""
        zamzar_tracked.account.get()
        assert "zamzar-python-v1" == zamzar_tracked.pool_manager.history[0].request.headers["User-Agent"]

    def test_has_timeouts(self, zamzar):
        assert zamzar.timeout.connect_timeout == 15.0
        assert zamzar.timeout.read_timeout == 30.0

    def test_retries_on_server_error(self, zamzar, set_fake_responses, create_mock_response):
        """Test that the ZamzarClient retries on server error."""
        set_fake_responses([
            create_mock_response(503),
            create_mock_response(503),
            create_mock_response(200, json_body={"credits_remaining": 42}),
        ])

        account = zamzar.account.get()
        assert account.credits_remaining is not None

    def test_retries_on_rate_limited(self, zamzar, set_fake_responses, create_mock_response):
        """Test that the ZamzarClient retries on server error."""
        set_fake_responses([
            create_mock_response(429, json_body={"message": "Rate limit exceeded"}),
            create_mock_response(429, json_body={"message": "Rate limit exceeded"}),
            create_mock_response(200, json_body={"credits_remaining": 42}),
        ])

        account = zamzar.account.get()
        assert account.credits_remaining is not None

    def test_captures_latest_credit_usage(self, zamzar, set_fake_responses, create_mock_response):
        """Test that the ZamzarClient captures the latest credit usage."""
        # should be None before any request has been made
        assert zamzar.last_production_credits_remaining is None
        assert zamzar.last_sandbox_credits_remaining is None

        set_fake_responses([
            create_mock_response(
                200,
                headers={"Zamzar-Credits-Remaining": "42", "Zamzar-Test-Credits-Remaining": "24"},
                json_body={"data": [], "paging": {"total_count": 0}},
            ),
        ])

        # make a request
        zamzar.jobs.list()

        # should capture the latest credit usage
        assert zamzar.last_production_credits_remaining == 42
        assert zamzar.last_sandbox_credits_remaining == 24
