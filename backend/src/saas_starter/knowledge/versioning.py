class DatasetVersionControl:
    def create_version(self, dataset_id: str, version_tag: str):
        return {"dataset_id": dataset_id, "version": version_tag}
