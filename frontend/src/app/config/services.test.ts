import { services } from '../config/services';

describe('services config', () => {
  it('points at local ingestor and retriever', () => {
    expect(services.ingestor.baseUrl).toMatch(/8000/);
    expect(services.retriever.baseUrl).toMatch(/8001/);
    expect(services.ingestor.token).toBeTruthy();
    expect(services.retriever.token).toBeTruthy();
  });
});
