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
