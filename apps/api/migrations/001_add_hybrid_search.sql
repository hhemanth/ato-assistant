-- Run this once in Supabase SQL editor (Dashboard → SQL Editor → New query).
-- Adds full-text search to ato_chunks and creates a hybrid retrieval function.

SET maintenance_work_mem = '64MB';

-- 1. Add generated tsvector column for full-text search
ALTER TABLE ato_chunks
  ADD COLUMN IF NOT EXISTS fts tsvector
    GENERATED ALWAYS AS (
      to_tsvector('english', coalesce(chunk_text, ''))
    ) STORED;

-- 2. GIN index for fast FTS queries
CREATE INDEX IF NOT EXISTS ato_chunks_fts_idx ON ato_chunks USING GIN (fts);

-- 3. Hybrid search function: vector similarity + BM25 combined via Reciprocal Rank Fusion (k=60)
CREATE OR REPLACE FUNCTION search_chunks_hybrid(
  query_embedding vector(1024),
  query_text      text,
  match_count     int DEFAULT 5
)
RETURNS TABLE (
  id           uuid,
  url          text,
  page_title   text,
  heading_path text[],
  chunk_text   text,
  similarity   float
)
LANGUAGE sql STABLE
AS $$
  WITH vector_ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (ORDER BY embedding <=> query_embedding) AS rank
    FROM ato_chunks
    WHERE embedding IS NOT NULL
    LIMIT match_count * 4
  ),
  fts_ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
             ORDER BY ts_rank(fts, websearch_to_tsquery('english', query_text)) DESC
           ) AS rank
    FROM ato_chunks
    WHERE fts @@ websearch_to_tsquery('english', query_text)
    LIMIT match_count * 4
  ),
  rrf AS (
    SELECT
      COALESCE(v.id, f.id)                        AS id,
      COALESCE(1.0 / (60 + v.rank), 0.0)
        + COALESCE(1.0 / (60 + f.rank), 0.0)     AS score
    FROM vector_ranked v
    FULL OUTER JOIN fts_ranked f ON v.id = f.id
  )
  SELECT
    c.id, c.url, c.page_title, c.heading_path, c.chunk_text,
    r.score AS similarity
  FROM rrf r
  JOIN ato_chunks c ON c.id = r.id
  ORDER BY r.score DESC
  LIMIT match_count;
$$;
