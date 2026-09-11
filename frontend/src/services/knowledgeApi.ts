export async function getDatasets(): Promise<any[]> {
  const res = await fetch("/api/v1/knowledge/datasets");
  return res.json();
}

# Updated audit checkpoint 2026-09-11 14:15
