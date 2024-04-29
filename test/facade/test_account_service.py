class TestAccountService:
    """Test class for the AccountService module."""

    def test_account(self, zamzar):
        """Test that the AccountService can get an account."""
        account = zamzar.account.get()

        assert account.plan is not None, "Should have a plan"
        assert account.credits_remaining is not None, "Should have credits remaining"
        assert account.test_credits_remaining is not None, "Should have test credits remaining"
