PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS source_world (
  world_id TEXT PRIMARY KEY,
  canonical_fen TEXT NOT NULL,
  fen_sha256 TEXT NOT NULL CHECK(length(fen_sha256)=64),
  source_kind TEXT NOT NULL CHECK(source_kind IN ('SYNTHETIC_FIXTURE','FROZEN_PGN','HISTORICAL')),
  source_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS measurement (
  measurement_id TEXT PRIMARY KEY,
  world_id TEXT NOT NULL REFERENCES source_world(world_id),
  move_a TEXT NOT NULL, move_b TEXT NOT NULL,
  engine_sha256 TEXT NOT NULL CHECK(length(engine_sha256)=64),
  uci_id TEXT NOT NULL,
  run_index INTEGER NOT NULL CHECK(run_index>=1),
  requested_depth INTEGER NOT NULL CHECK(requested_depth>=1),
  emitted_depth INTEGER NOT NULL CHECK(emitted_depth>=1),
  score_perspective TEXT NOT NULL CHECK(score_perspective IN ('WHITE','BLACK','SIDE_TO_MOVE')),
  a_cp INTEGER, b_cp INTEGER,
  status TEXT NOT NULL CHECK(status IN ('RAW_UCI_ONLY','COMPARABLE_CP','HOLD')),
  explanation_authority INTEGER NOT NULL DEFAULT 0 CHECK(explanation_authority=0),
  UNIQUE(world_id,move_a,move_b,engine_sha256,run_index),
  CHECK(move_a<>move_b),
  CHECK((status<>'COMPARABLE_CP') OR (a_cp IS NOT NULL AND b_cp IS NOT NULL AND emitted_depth=requested_depth))
);
CREATE VIEW paired_repeats AS SELECT world_id,move_a,move_b,engine_sha256,requested_depth,
 COUNT(*) AS repeats, MIN(a_cp-b_cp) AS min_delta_cp, MAX(a_cp-b_cp) AS max_delta_cp
 FROM measurement WHERE status='COMPARABLE_CP' GROUP BY world_id,move_a,move_b,engine_sha256,requested_depth;
