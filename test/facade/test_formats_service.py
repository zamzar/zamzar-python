from zamzar.pagination import before


class TestFormatsService:
    """Test class for the FormatsService module."""

    def test_find(self, zamzar):
        """Test that the FormatsService can find a format by name."""
        actual = zamzar.formats.find("mp3")
        assert actual.name == "mp3", "Should find a format"
        assert 0 < len(actual.targets), "Expected at least one target format"

    def test_list(self, zamzar):
        """Test that the FormatsService can list formats."""
        formats = zamzar.formats.list()
        assert 0 < len(formats.items), "Should list formats"
        for f in formats.items:
            assert f.name is not None, "Should have a name"

    def test_list_and_page_forwards(self, zamzar):
        """Test that the FormatsService can list and page forwards."""
        number_of_pages = 0
        current = zamzar.formats.list(limit=50)
        while len(current.items) > 0:
            number_of_pages += 1
            assert len(current.items) <= 50
            current = current.next_page()
        assert number_of_pages > 1

    def test_list_and_page_backwards(self, zamzar):
        """Test that the FormatsService can list and page backwards."""
        number_of_pages = 0
        current = zamzar.formats.list(anchor=before("zip"), limit=50)
        while len(current.items) > 0:
            number_of_pages += 1
            assert len(current.items) <= 50
            current = current.previous_page()
        assert number_of_pages > 1
