CREATE TABLE IF NOT EXISTS skill (
  skill_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  skill_name TEXT NOT NULL,
  claim_type TEXT NOT NULL,          -- reported|earned
  level REAL,
  confidence REAL NOT NULL,
  visibility TEXT NOT NULL,          -- scope for sharing
  evidence_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id),
  FOREIGN KEY (actor_id) REFERENCES actor(actor_id)
);
