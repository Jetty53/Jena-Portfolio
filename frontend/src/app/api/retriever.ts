import { services } from '../config/services';

type AskBody = {
  question: string;
  session_id?: string;
  history?: { role: 'user' | 'assistant'; content: string }[];
  source_type?: string;
};

export type AskSource = {
  filename: string;
  chunk_index: number;
  score: number;
  source_type: string;
};

export type AskResponse = {
  question: string;
  used_question: string;
  corrected: boolean;
  session_id: string | null;
  answer: string;
  sources: AskSource[];
};

export type StreamHandlers = {
  onMeta?: (data: { session_id?: string | null; used_question?: string; sources?: AskSource[] }) => void;
  onToken?: (t: string) => void;
  onDone?: (data: { session_id?: string | null; answer: string; sources?: AskSource[] }) => void;
  onError?: (message: string) => void;
};

function authHeaders() {
  return {
    Authorization: `Bearer ${services.retriever.token}`,
    'Content-Type': 'application/json',
  };
}

export function parseSseBuffer(buffer: string): { events: { event: string; data: string }[]; rest: string } {
  const events: { event: string; data: string }[] = [];
  const parts = buffer.split('\n\n');
  const rest = parts.pop() ?? '';
  for (const block of parts) {
    if (!block.trim()) continue;
    let event = 'message';
    const dataLines: string[] = [];
    for (const line of block.split('\n')) {
      if (line.startsWith('event:')) event = line.slice(6).trim();
      else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
    }
    events.push({ event, data: dataLines.join('\n') });
  }
  return { events, rest };
}

export async function askRetriever(body: AskBody): Promise<AskResponse> {
  const res = await fetch(`${services.retriever.baseUrl}/v1/ask`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `retrieve failed (${res.status})`);
  }
  return res.json();
}

export async function askRetrieverStream(body: AskBody, handlers: StreamHandlers): Promise<void> {
  const res = await fetch(`${services.retriever.baseUrl}/v1/ask/stream`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok || !res.body) {
    const detail = await res.text();
    throw new Error(detail || `retrieve stream failed (${res.status})`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parsed = parseSseBuffer(buf);
    buf = parsed.rest;
    for (const ev of parsed.events) {
      let payload: Record<string, unknown> = {};
      try {
        payload = ev.data ? JSON.parse(ev.data) : {};
      } catch {
        continue;
      }
      if (ev.event === 'meta') handlers.onMeta?.(payload as never);
      else if (ev.event === 'token' && typeof payload.t === 'string') handlers.onToken?.(payload.t);
      else if (ev.event === 'done') handlers.onDone?.(payload as never);
      else if (ev.event === 'error') handlers.onError?.(String(payload.message || 'stream error'));
    }
  }
}

export async function retrieverHealth() {
  const res = await fetch(`${services.retriever.baseUrl}/health`);
  if (!res.ok) throw new Error(`retriever health ${res.status}`);
  return res.json();
}
