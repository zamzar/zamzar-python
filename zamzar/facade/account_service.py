from zamzar.api import AccountApi
from zamzar.models import Account


class AccountService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = AccountApi(client)

    def get(self) -> Account:
        return self._api.get_account(_request_timeout=self._zamzar.timeout)
