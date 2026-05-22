-- Run this once in your Supabase SQL editor before running the scraper pipeline.
-- Required: enable the pgvector extension first via Supabase Dashboard → Extensions → vector

create extension if not exists vector;

-- One row per ATO page scraped
create table ato_pages (
  id            uuid primary key default gen_random_uuid(),
  url           text unique not null,
  title         text,
  markdown      text not null,
  last_modified timestamptz,   -- from HTTP Last-Modified header, used to detect stale pages
  scraped_at    timestamptz default now()
);

-- One row per ~500-token chunk of a page
create table ato_chunks (
  id            uuid primary key default gen_random_uuid(),
  page_id       uuid references ato_pages(id) on delete cascade,

  -- Denormalized from ato_pages so retrieval queries need no JOIN
  url           text not null,
  page_title    text,

  chunk_index   int not null,
  heading_path  text[],         -- e.g. ["Medicare levy", "Reduction", "How it's calculated"]
  chunk_text    text not null,

  embedding     vector(1024),   -- voyage-3-large output dimension
  created_at    timestamptz default now()
);

-- NOTE: Add an IVFFlat index once the corpus exceeds ~10k chunks.
-- Below that threshold a sequential scan is faster than approximate search.
-- When ready: CREATE INDEX ON ato_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Helper: retrieve top-k chunks with citation fields in one query (no JOIN required)
-- Usage: select * from search_chunks($1::vector, 5);
create or replace function search_chunks(query_embedding vector(1024), match_count int)
returns table (
  id            uuid,
  url           text,
  page_title    text,
  heading_path  text[],
  chunk_text    text,
  similarity    float
)
language sql stable
as $$
  select
    id,
    url,
    page_title,
    heading_path,
    chunk_text,
    1 - (embedding <=> query_embedding) as similarity
  from ato_chunks
  where embedding is not null
  order by embedding <=> query_embedding
  limit match_count;
$$;
