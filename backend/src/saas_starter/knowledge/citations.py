import re

class CitationExtractor:
    def extract_citations(self, text: str) -> list:
        return re.findall(r"\[Source: ([^\]]+)\]", text)


class FootnoteFormatter:
    def format(self, text: str, sources: list) -> str:
        formatted_sources = "\n".join([f"[{i+1}] {s}" for i, s in enumerate(sources)])
        return f"{text}\n\nSources:\n{formatted_sources}"

# Updated audit checkpoint 2026-09-07 14:15

# Updated audit checkpoint 2026-09-08 09:30
