export async function getDatasets(): Promise<any[]> {
  const res = await fetch("/api/v1/knowledge/datasets");
  return res.json();
}
