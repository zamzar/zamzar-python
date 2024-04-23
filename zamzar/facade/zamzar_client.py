from zamzar.api_client import ApiClient
from zamzar.configuration import Configuration
from zamzar.api.welcome_api import WelcomeApi


class ZamzarClient:
    def __init__(self, api_key: str):
        configuration = Configuration(access_token=api_key)
        self.client = ApiClient(configuration=configuration)
        self.default = WelcomeApi(self.client)

    def test_connection(self) -> str:
        return self.default.welcome().message
