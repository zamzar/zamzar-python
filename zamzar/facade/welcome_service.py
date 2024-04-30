from zamzar import ApiException
from zamzar.api.welcome_api import WelcomeApi


class WelcomeService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = WelcomeApi(client)

    def get(self) -> str:
        message = self._api.welcome(_request_timeout=self._zamzar.timeout).message

        if message is None:
            raise ApiException("No welcome message was received.")

        return message
