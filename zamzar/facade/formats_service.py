from zamzar.api import FormatsApi
from zamzar.facade.pagination import Paged
from zamzar.models.format import Format


class FormatsService:
    def __init__(self, zamzar, client):
        self._zamzar = zamzar
        self._api = FormatsApi(client)

    def find(self, name) -> Format:
        return self._api.get_format_by_id(format=name, _request_timeout=self._zamzar.timeout)

    def list(self, anchor=None, limit=None) -> Paged[Format]:
        after = anchor.get_after_parameter_value() if anchor else None
        before = anchor.get_before_parameter_value() if anchor else None
        response = self._api.list_formats(
            after=after,
            before=before,
            limit=limit,
            _request_timeout=self._zamzar.timeout
        )
        return Paged(self, (response.data or []), response.paging)
