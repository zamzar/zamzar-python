import pytest

from zamzar import ApiException


class TestImportManager:
    """Test class for the ImportManager module."""

    def test_await(self, zamzar, succeeding_import_id):
        """Test the await method."""
        assert zamzar.imports.find(succeeding_import_id).await_completion().has_succeeded()
        assert zamzar.imports.find(succeeding_import_id).await_completion().failure is None
        assert zamzar.imports.find(succeeding_import_id).await_completion(throw_on_failure=True).has_succeeded()

    def test_await_failing(self, zamzar, failing_import_id):
        """Test the await method for a failing import."""
        assert zamzar.imports.find(failing_import_id).await_completion().has_failed()
        assert zamzar.imports.find(failing_import_id).await_completion().failure.code is not None
        assert zamzar.imports.find(failing_import_id).await_completion().failure.message is not None
        with pytest.raises(ApiException):
            zamzar.imports.find(failing_import_id).await_completion(throw_on_failure=True)

    def test_throw_when_awaited_not_found(self, zamzar, mock_server, succeeding_import_id):
        """Test that an ApiException is thrown when an import is not found."""
        _import = zamzar.imports.find(succeeding_import_id)
        mock_server.destroy(f"/imports/{succeeding_import_id}")
        with pytest.raises(ApiException):
            _import.await_completion()
