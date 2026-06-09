from saas_starter.rag.parsers.markdown import MarkdownDocumentParser

def test_markdown_parser(tmp_path):
    p = tmp_path / "test.md"
    p.write_text("# Hello World")
    parser = MarkdownDocumentParser()
    assert "# Hello World" in parser.parse(str(p))
