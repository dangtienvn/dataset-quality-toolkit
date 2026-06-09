from saas_starter.rag.parsers.base import BaseDocumentParser

class MarkdownDocumentParser(BaseDocumentParser):
    def parse(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
