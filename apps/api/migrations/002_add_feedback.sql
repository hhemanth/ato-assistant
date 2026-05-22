-- Run in Supabase SQL editor after 001_add_hybrid_search.sql.
-- Creates a feedback table for "Report incorrect answer" submissions.

CREATE TABLE feedback (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_query   text NOT NULL,
  response     text NOT NULL,
  created_at   timestamptz DEFAULT now()
);

-- No anon/authenticated policies: only the service_role key (used by the API) can write here.
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
