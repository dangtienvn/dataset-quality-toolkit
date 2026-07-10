class ChunkPreviewer:
    def preview_chunk(self, chunk_id: str, text: str, highlight_terms: list = None):
        return {"id": chunk_id, "text": text, "highlights": highlight_terms or []}
