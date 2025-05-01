import pytest

from test.facade.assertions import assert_non_empty_file
from zamzar import ApiException
from zamzar.pagination import before


class TestImportsService:
    """Test class for the ImportsService module."""

    def test_find(self, zamzar, succeeding_import_id):
        """Test that the ImportsService can find by id."""
        actual = zamzar.imports.find(succeeding_import_id)
        assert actual.id == succeeding_import_id, "Should find an import"

    def test_list(self, zamzar):
        """Test that the ImportsService can list."""
        imports = zamzar.imports.list()
        assert 0 < len(imports.items), "Should list imports"
        for i in imports.items:
            assert i.id > 0, "Should have an id"

    def test_list_and_page_forwards(self, zamzar):
        """Test that the ImportsService can list and page forwards."""
        number_of_pages = 0
        current = zamzar.imports.list(limit=2)
        while len(current.items) > 0:
            number_of_pages += 1
            assert len(current.items) <= 2
            current = current.next_page()
        assert number_of_pages >= 2

    def test_list_and_page_backwards(self, zamzar):
        """Test that the ImportsService can list and page backwards."""
        number_of_pages = 0
        current = zamzar.imports.list(anchor=before(1), limit=1)
        while len(current.items) > 0:
            number_of_pages += 1
            assert len(current.items) <= 1
            current = current.previous_page()
        assert number_of_pages >= 2

    def test_start(self, zamzar, tmp_path):
        """Test that the ImportsService can start an import."""
        downloaded = tmp_path / "imported-file.txt"
        _import = zamzar.imports.start("s3://bucket-name/path/to/import").await_completion()
        _import.imported_file.download(downloaded)
        assert_non_empty_file(downloaded)

    def test_start_for_url_with_unknown_filename_requires_filename_param(self, zamzar):
        """Test that starting an import with an unknown filename requires a filename param."""
        with pytest.raises(ApiException):
            zamzar.imports.start("s3://bucket-name/path/to/unknown")

        # this shouldn't raise an exception
        zamzar.imports.start("s3://bucket-name/path/to/unknown", "filename.txt")
