export interface RAGDocument {
  id: string;
  filename: string;
  status: "pending" | "processing" | "indexed" | "failed";
  chunkCount: number;
  createdAt: string;
}
