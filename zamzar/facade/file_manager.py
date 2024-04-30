from zamzar.models import File


class FileManager:

    def __init__(self, zamzar, model: File):
        self._zamzar = zamzar
        self.model = model
        self.id = model.id

    def delete(self) -> id:
        self._zamzar.files.delete(self.id)
        return self

    def download(self, target) -> id:
        self._zamzar.files._download_model(self.model, target)
        return self
