import pytest

from zamzar.exceptions import NotFoundException
from zamzar.facade.pagination.anchor import after, before
from .assertions import assert_non_empty_file


class TestFilesService:
    """Test class for the FilesService module."""

    def test_find(self, zamzar, file_id):
        """Test that the FilesService can find a file."""
        actual = zamzar.files.find(file_id)
        assert actual.id == file_id, "Should find a file"

    def test_list(self, zamzar):
        """Test that the FilesService can list files."""
        files = zamzar.files.list()
        assert 0 < len(files.get_items()), "Should list files"
        for file in files.get_items():
            assert file.id is not None, "Should have an ID"

    def test_list_and_page_forwards(self, zamzar):
        """Test that the FilesService can list and page forwards."""
        # Note the zamzar-mock provides at least 7 precanned files
        # See: https://github.com/zamzar/zamzar-mock/blob/main/README.md

        first_page = zamzar.files.list(anchor=after(6), limit=2)
        assert [5, 4] == [file.id for file in first_page.get_items()]

        second_page = first_page.next_page()
        assert [3, 2] == [file.id for file in second_page.get_items()]

        third_page = second_page.next_page()
        assert [1] == [file.id for file in third_page.get_items()]

        past_end = third_page.next_page()
        assert 0 == len(past_end.get_items())

    def test_list_and_page_backwards(self, zamzar):
        """Test that the FilesService can list and page backwards."""
        # Note the zamzar-mock provides at least 7 precanned files
        # See: https://github.com/zamzar/zamzar-mock/blob/main/README.md

        first_page = zamzar.files.list(anchor=before(1), limit=2)
        assert [3, 2] == [file.id for file in first_page.get_items()]

        second_page = first_page.previous_page()
        assert [5, 4] == [file.id for file in second_page.get_items()]

        third_page = second_page.previous_page()
        assert [7, 6] == [file.id for file in third_page.get_items()]

        past_end = third_page.previous_page()
        assert 0 == len(past_end.get_items())

    def test_delete(self, zamzar, file_id):
        """Test that the FilesService can delete a file."""
        deleted = zamzar.files.delete(file_id)
        assert deleted.id == file_id, "Should have deleted specified file"
        with pytest.raises(NotFoundException):
            zamzar.files.find(file_id)

    def test_delete_non_existent(self, zamzar):
        """Test that the FilesService raises an exception when trying to delete a non-existent file."""
        with pytest.raises(NotFoundException):
            zamzar.files.delete(999999)

    def test_download(self, zamzar, file_id, tmp_path):
        """Test that the FilesService can download a file."""
        target = tmp_path / "target"
        downloaded = zamzar.files.download(file_id, target)
        assert_non_empty_file(downloaded)

    def test_download_to_directory(self, zamzar, file_id, tmp_path):
        """Test that the FilesService can download a file to a directory."""
        target = tmp_path / "target-dir"
        target.mkdir()
        assert 0 == len(list(target.iterdir())), "Should be an empty directory"
        zamzar.files.download(file_id, target)
        assert 1 == len(list(target.iterdir())), "Should have downloaded a file"

    def test_upload(self, zamzar, tmp_path):
        """Test that the FilesService can upload a file."""
        source = tmp_path / "source"
        source.touch()
        source.write_text("Hello, world!")
        uploaded = zamzar.files.upload(source)
        assert uploaded.id is not None, "Should have uploaded a file"
