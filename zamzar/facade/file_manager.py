from zamzar.models import File


class FileManager:

    def __init__(self, zamzar, model: File):
        self._zamzar = zamzar
        self.model = model
        self.id = model.id

    def download(self, target):
        return self._zamzar.files._download_model(self.model, target)
