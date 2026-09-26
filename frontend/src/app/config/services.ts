const env = import.meta.env;

export const services = {
  ingestor: {
    baseUrl: env.VITE_INGESTOR_URL ?? 'http://127.0.0.1:8000',
    token: env.VITE_INGEST_TOKEN ?? 'change-me',
  },
  retriever: {
    baseUrl: env.VITE_RETRIEVER_URL ?? 'http://127.0.0.1:8001',
    token: env.VITE_RETRIEVE_TOKEN ?? 'change-me',
  },
} as const;
