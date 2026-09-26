import { parseSseBuffer } from './retriever';

describe('parseSseBuffer', () => {
  it('splits complete SSE events and keeps a partial tail', () => {
    const { events, rest } = parseSseBuffer('event: token\ndata: {"t":"Hi"}\n\nevent: to');
    expect(events).toEqual([{ event: 'token', data: '{"t":"Hi"}' }]);
    expect(rest).toBe('event: to');
  });
});
