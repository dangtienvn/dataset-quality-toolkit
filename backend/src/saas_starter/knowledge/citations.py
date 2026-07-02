import re

class CitationExtractor:
    def extract_citations(self, text: str) -> list:
        return re.findall(r"\[Source: ([^\]]+)\]", text)
