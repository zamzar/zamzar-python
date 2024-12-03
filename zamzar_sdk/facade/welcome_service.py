from zamzar_sdk import ApiException
from zamzar_sdk.api.welcome_api import WelcomeApi
from zamzar_sdk.api_client import ApiClient


class WelcomeService:
    """Checks connectivity to the Zamzar API."""

    def __init__(self, zamzar, client: ApiClient):
        self._zamzar = zamzar
        self._api = WelcomeApi(client)

    def get(self) -> str:
        """Returns a welcome message if the Zamzar API is reachable, available and you are authenticated."""
        message = self._api.welcome().message
        if message is None:
            raise ApiException("No welcome message was received.")
        return message
