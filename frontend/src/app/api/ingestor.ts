import { services } from '../config/services';

function authHeaders() {
  return { Authorization: `Bearer ${services.ingestor.token}` };
}

export async function uploadIngest(files: File[], sourceType = 'other') {
  const form = new FormData();
  form.append('source_type', sourceType);
  for (const file of files) {
    form.append('files', file);
  }
  const res = await fetch(`${services.ingestor.baseUrl}/v1/ingest/upload`, {
    method: 'POST',
    headers: authHeaders(),
    body: form,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `ingest failed (${res.status})`);
  }
  return res.json() as Promise<{ request_id: string; status: string; poll_url: string; files: string[] }>;
}

export async function pollIngest(requestId: string) {
  const res = await fetch(`${services.ingestor.baseUrl}/v1/ingest/${requestId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `ingest status failed (${res.status})`);
  }
  return res.json();
}

export async function ingestorHealth() {
  const res = await fetch(`${services.ingestor.baseUrl}/health`);
  if (!res.ok) throw new Error(`ingestor health ${res.status}`);
  return res.json();
}
