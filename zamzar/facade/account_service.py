from zamzar.api import AccountApi
from zamzar.api_client import ApiClient
from zamzar.models import Account


class AccountService:
    """Retrieve account information."""

    def __init__(self, zamzar, client: ApiClient):
        self._zamzar = zamzar
        self._api = AccountApi(client)

    def get(self) -> Account:
        """
        Retrieves the current status of your Zamzar API account, including your available conversion credits and
        current plan.
        """
        return self._api.get_account()
