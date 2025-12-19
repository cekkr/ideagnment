CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks
USING fts5(text, chunk_id UNINDEXED, workspace_id UNINDEXED);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_capsules
USING fts5(title, body, capsule_id UNINDEXED, workspace_id UNINDEXED);
