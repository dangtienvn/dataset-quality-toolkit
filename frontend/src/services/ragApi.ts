export async function fetchDocuments(): Promise<any[]> {
  const res = await fetch("/api/v1/rag/documents");
  return res.json();
}

# Updated audit checkpoint 2026-08-31 14:15
