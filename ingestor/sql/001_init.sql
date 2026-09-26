CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS ingest_requests (
    id UUID PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'queued',
    source_type TEXT NOT NULL DEFAULT 'other',
    origin TEXT NOT NULL DEFAULT 'upload',
    r2_prefix TEXT,
    last_ok_step TEXT,
    error TEXT,
    retry_count INT NOT NULL DEFAULT 0,
    file_count INT NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES ingest_requests(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    mime_type TEXT,
    byte_size BIGINT,
    sha256 TEXT NOT NULL,
    r2_key TEXT,
    parser TEXT,
    char_count INT,
    language TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS documents_sha256_uidx ON documents (sha256);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    request_id UUID NOT NULL REFERENCES ingest_requests(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    text TEXT NOT NULL,
    token_count INT,
    heading_path TEXT,
    page_start INT,
    page_end INT,
    source_type TEXT NOT NULL,
    uri TEXT,
    embed_model TEXT NOT NULL,
    embed_dim INT NOT NULL,
    chunker_version TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunks_source_type_idx ON chunks (source_type);
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON chunks (document_id);

CREATE TABLE IF NOT EXISTS ingest_audit (
    id BIGSERIAL PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES ingest_requests(id) ON DELETE CASCADE,
    document_id UUID,
    step TEXT NOT NULL,
    status TEXT NOT NULL,
    detail JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ingest_audit_request_idx
    ON ingest_audit (request_id, created_at);
