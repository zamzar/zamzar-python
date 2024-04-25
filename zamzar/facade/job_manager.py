from zamzar.models import File
from zamzar.models import Job


class JobManager:

    def __init__(self, zamzar, model: Job):
        self._zamzar = zamzar
        self.model = model
        self.id = model.id
        self.source_file_id = model.source_file.id
        self.target_files = model.target_files
        self.target_file_ids = [target_file.id for target_file in model.target_files]

    def await_completion(self) -> id:
        self.refresh()  # FIXME
        self.refresh()
        self.refresh()
        return self.refresh()

    def delete_all_files(self) -> id:
        self.delete_source_file()
        self.delete_target_files()
        return self

    def delete_source_file(self) -> id:
        self._zamzar.files.delete(self.source_file_id)
        return self

    def delete_target_files(self) -> id:
        for target_file_id in self.target_file_ids:
            self._zamzar.files.delete(target_file_id)
        return self

    def refresh(self) -> id:
        return self._zamzar.jobs.find(self.id)

    def store(self, target) -> id:
        # TODO throw if there are no target files to download
        # ModelFile source = getPrimaryTargetFile();
        # destination = zamzar.files().download(source, destination);
        # if (getTargetFileIds().size() > 1) {
        #     this.extract(destination);
        # }
        source = self.__primary_target_file()
        self._zamzar.files._download_model(source, target)
        return self

    def __primary_target_file(self) -> File:
        return self.target_files[0]  # FIXME (multiple target files)
