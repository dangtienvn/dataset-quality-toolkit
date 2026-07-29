import html

class HTMLSanitizer:
    def sanitize(self, raw_html: str) -> str:
        return html.escape(raw_html)
