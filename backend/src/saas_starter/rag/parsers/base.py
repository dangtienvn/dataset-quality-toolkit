class BaseDocumentParser:
    def parse(self, file_path: str) -> str:
        raise NotImplementedError
