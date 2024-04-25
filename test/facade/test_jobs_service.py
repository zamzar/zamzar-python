class TestJobsService:
    """Test class for the JobsService module."""

    def test_find(self, zamzar, succeeding_job_id):
        """Test that the JobsService can find a job by its ID."""
        job = zamzar.jobs.find(succeeding_job_id)
        assert job.id == succeeding_job_id, "Should find a job by its ID"

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
