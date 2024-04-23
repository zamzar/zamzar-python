from zamzar import ZamzarClient

class TestZamzarClient:
    """Test class for the ZamzarClient module."""

    def test_can_hit_production(self):
        """Test that the ZamzarClient returns a welcome message when directed at the production environment."""
        zamzar = ZamzarClient("GiVUYsF4A8ssq93FR48H")
        assert zamzar.test_connection() is not None, "Should return a welcome message"
