from zamzar.facade.pagination.anchor import before


class TestImportsService:
    """Test class for the ImportsService module."""

    def test_find(self, zamzar, succeeding_import_id):
        """Test that the ImportsService can find by id."""
        actual = zamzar.imports.find(succeeding_import_id)
        assert actual.id == succeeding_import_id, "Should find an import"

    def test_list(self, zamzar):
        """Test that the ImportsService can list."""
        imports = zamzar.imports.list()
        assert 0 < len(imports.get_items()), "Should list imports"
        for i in imports.get_items():
            assert i.id > 0, "Should have an id"

    def test_list_and_page_forwards(self, zamzar):
        """Test that the ImportsService can list and page forwards."""
        number_of_pages = 0
        current = zamzar.imports.list(limit=2)
        while len(current.get_items()) > 0:
            number_of_pages += 1
            assert len(current.get_items()) <= 2
            current = current.next_page()
        assert number_of_pages >= 2

    def test_list_and_page_backwards(self, zamzar):
        """Test that the ImportsService can list and page backwards."""
        number_of_pages = 0
        current = zamzar.imports.list(anchor=before(1), limit=1)
        while len(current.get_items()) > 0:
            number_of_pages += 1
            assert len(current.get_items()) <= 1
            current = current.previous_page()
        assert number_of_pages >= 2