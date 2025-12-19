PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workspace (
  workspace_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL,
  owner_org_id TEXT,
  default_scope TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actor (
  actor_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  display_name TEXT NOT NULL,
  org_id TEXT,
  roles_json TEXT,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS artifact (
  artifact_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL,
  created_by_actor_id TEXT,
  meta_json TEXT,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS chunk (
  chunk_id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL,
  workspace_id TEXT NOT NULL,
  start_char INTEGER NOT NULL,
  end_char INTEGER NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (artifact_id) REFERENCES artifact(artifact_id),
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS embedding (
  embedding_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  owner_type TEXT NOT NULL,
  owner_id TEXT NOT NULL,
  dim INTEGER NOT NULL,
  vec_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS capsule (
  capsule_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  lens_tags_json TEXT,
  scope TEXT NOT NULL,
  evidence_level TEXT NOT NULL,
  confidence REAL NOT NULL,
  created_at TEXT NOT NULL,
  created_by_actor_id TEXT,
  provenance_json TEXT,
  is_published INTEGER NOT NULL DEFAULT 0,
  redaction_profile_id TEXT,
  content_hash TEXT,
  signer_key_id TEXT,
  signature_b64 TEXT,
  meta_json TEXT,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS edge (
  edge_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  src_id TEXT NOT NULL,
  dst_id TEXT NOT NULL,
  rel TEXT NOT NULL,
  weight REAL NOT NULL DEFAULT 0.5,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS profile (
  profile_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  owner_actor_id TEXT,
  lens_primary TEXT,
  assumption_signature_json TEXT,
  glossary_exposure_json TEXT,
  stance_refs_json TEXT,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS exposure (
  exposure_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  capsule_id TEXT NOT NULL,
  exposure_type TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  strength REAL NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS policy (
  workspace_id TEXT PRIMARY KEY,
  policy_json TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS redaction_profile (
  redaction_profile_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  name TEXT NOT NULL,
  rules_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS trust_key (
  key_id TEXT PRIMARY KEY,
  org_id TEXT,
  label TEXT,
  ed25519_pub_b64 TEXT NOT NULL,
  trust_level TEXT NOT NULL,
  added_at TEXT NOT NULL
);
