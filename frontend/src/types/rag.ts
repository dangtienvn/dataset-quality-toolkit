export interface RAGDocument {
  id: string;
  filename: string;
  status: "pending" | "processing" | "indexed" | "failed";
  chunkCount: number;
  createdAt: string;
}

# Updated audit checkpoint 2026-08-31 09:30
