-- Enable pgvector extension for vector similarity search
-- This should be run as a superuser or with appropriate permissions

CREATE EXTENSION IF NOT EXISTS vector;

-- Verify the extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';
