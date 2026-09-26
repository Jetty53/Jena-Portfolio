/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_INGESTOR_URL?: string;
  readonly VITE_RETRIEVER_URL?: string;
  readonly VITE_INGEST_TOKEN?: string;
  readonly VITE_RETRIEVE_TOKEN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
