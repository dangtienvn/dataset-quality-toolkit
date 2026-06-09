from saas_starter.rag.parsers.base import BaseDocumentParser

class DocxDocumentParser(BaseDocumentParser):
    def parse(self, file_path: str) -> str:
        return "DOCX text content..."
