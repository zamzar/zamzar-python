import pytest

from zamzar import ApiException
from zamzar.facade.job_status import JobStatus
from zamzar.facade.jobs_service import JobsService
from zamzar.pagination import before


class TestJobsService:
    """Test class for the JobsService module."""

    filenames_can_be_inferred = [
        ("https://example.com/file.txt", None, "file.txt"),
        ("https://example.com/file.txt", "unused", "file.txt"),
        ("https://example.com/file", "txt", "file.txt"),
        ("https://example.com/file.txt?query=param", None, "file.txt"),
        ("https://example.com/file.txt?query=param", "unused", "file.txt"),
        ("https://example.com/file?query=param", "txt", "file.txt"),
    ]

    filenames_cannot_be_inferred = [
        ("https://example.com/file", None),
        ("https://example.com/file?query=param", None),
        ("https://example.com/", "txt"),
        ("https://example.com/", None),
        ("https://example.com", "txt"),
        ("https://example.com", None),
    ]

    @pytest.mark.parametrize("source_url, source_format, expected", filenames_can_be_inferred)
    def test_can_infer_filename(self, zamzar, source_url, source_format, expected):
        """Test that the JobsService tries to infer filenames from URLs and source formats."""
        assert expected == JobsService._infer_filename(source_url, source_format)

    @pytest.mark.parametrize("source_url, source_format", filenames_cannot_be_inferred)
    def test_cannot_infer_filename(self, zamzar, source_url, source_format):
        """Test that the JobsService fails to infer filenames from URLs and source formats that lack information."""
        with pytest.raises(ApiException):
            JobsService._infer_filename(source_url, source_format)

    def test_find(self, zamzar, succeeding_job_id):
        """Test that the JobsService can find a job by its ID."""
        job = zamzar.jobs.find(succeeding_job_id)
        assert job.id == succeeding_job_id, "Should find a job by its ID"

    def test_list(self, zamzar):
        """Test that the JobsService can list."""
        jobs = zamzar.jobs.list()
        assert 0 < len(jobs.items), "Should list jobs"
        for i in jobs.items:
            assert i.id > 0, "Should have an id"

    def test_list_successful(self, zamzar):
        """Test that the JobsService can list successful jobs."""
        jobs = zamzar.jobs.successful.list()
        for job in jobs.items:
            assert job.id > 0
            assert job.has_succeeded()

    def test_list_and_page_forwards(self, zamzar):
        """Test that the JobsService can list and page forwards."""
        number_of_pages = 0
        current = zamzar.jobs.list(limit=2)
        while len(current.items) > 0:
            number_of_pages += 1
            assert len(current.items) <= 2
            current = current.next_page()
        assert number_of_pages >= 2

    def test_list_and_page_backwards(self, zamzar):
        """Test that the JobsService can list and page backwards."""
        number_of_pages = 0
        current = zamzar.jobs.list(anchor=before(1), limit=1)
        while len(current.items) > 0:
            number_of_pages += 1
            assert len(current.items) <= 1
            current = current.previous_page()
        assert number_of_pages >= 2

    def test_create(self, zamzar, tmp_path):
        """Test that the JobsService can create a job."""
        source = tmp_path / "source"
        source.touch()
        source.write_text("Hello, world!")
        job = zamzar.jobs.create(
            source=source,
            target_format="txt"
        )
        assert job.id > 0, "Should have created a job"

    def test_create_with_source_format_and_options_and_export(self, zamzar, tmp_path):
        """Test that the JobsService can create a job with a source format, options, and export."""
        source = tmp_path / "source"
        source.touch()
        source.write_text("Hello, world!")
        job = zamzar.jobs.create(
            source=source,
            target_format="txt",
            source_format="pdf",
            options={
                "quality": "50",
                "ocr": "true"
            },
            export_url="s3://bucket-name/path/to/export"
        )
        assert job.id > 0, "Should have created a job"
        # FIXME how hard would it be to update the mock to mirror the submitted JSON? Would avoid need for spies here and in Java

    def test_create_from_url(self, zamzar):
        """Test that the JobsService can create a job from a URL."""
        job = zamzar.jobs.create(
            source="https://www.example.com/logo.png",
            target_format="jpg"
        )
        assert job.id > 0, "Should have created a job"

    def test_create_from_existing_file(self, zamzar, file_id):
        """Test that the JobsService can create a job from an existing file."""
        job = zamzar.jobs.create(
            source=file_id,
            target_format="jpg"
        )
        assert job.id > 0, "Should have created a job"

    def test_create_throws_when_target_format_is_unsupported(self, zamzar, tmp_path):
        """Test that the JobsService throws when the target format is unsupported."""
        source = tmp_path / "source"
        source.touch()
        source.write_text("Hello, world!")
        with pytest.raises(ApiException):
            zamzar.jobs.create(
                source=source,
                target_format="unsupported"
            )

    def test_cancel(self, zamzar, succeeding_job_id):
        """Test that the JobsService can cancel a job."""
        job = zamzar.jobs.cancel(succeeding_job_id)
        assert job.id == succeeding_job_id
        assert job.model.status == JobStatus.CANCELLED.value

        # Check that fresh requests return the updated status
        assert job.refresh().model.status == JobStatus.CANCELLED.value
