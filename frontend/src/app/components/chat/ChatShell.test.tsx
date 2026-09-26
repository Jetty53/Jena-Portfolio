import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatShell from './ChatShell';

function sseResponse(body: string) {
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(body));
      controller.close();
    },
  });
  return { ok: true, body: stream, text: async () => body };
}

describe('ChatShell', () => {
  it('shows Jena empty state', () => {
    render(<ChatShell />);
    expect(screen.getByText(/Ask Jena if I'm a fit/i)).toBeInTheDocument();
    expect(screen.getByText(/Suggested questions/i)).toBeInTheDocument();
  });

  it('streams retriever tokens into the answer', async () => {
    const sse =
      'event: meta\ndata: {"session_id":"11111111-1111-1111-1111-111111111111","sources":[{"filename":"Resume.pdf","chunk_index":0,"score":0.7,"source_type":"cv"}]}\n\n' +
      'event: token\ndata: {"t":"From the "}\n\n' +
      'event: token\ndata: {"t":"knowledge base."}\n\n' +
      'event: done\ndata: {"answer":"From the knowledge base.","sources":[{"filename":"Resume.pdf","chunk_index":0,"score":0.7,"source_type":"cv"}]}\n\n';
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(sseResponse(sse)));
    render(<ChatShell />);
    fireEvent.change(screen.getByLabelText('Chat message'), { target: { value: 'Hello' } });
    fireEvent.click(screen.getByLabelText('Send message'));
    await waitFor(() => {
      expect(screen.getByText('From the knowledge base.')).toBeInTheDocument();
    });
    expect(screen.getByText(/Sources: Resume.pdf/i)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(expect.stringMatching(/\/v1\/ask\/stream/), expect.any(Object));
    vi.unstubAllGlobals();
  });
});
