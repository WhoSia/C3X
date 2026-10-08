# C3X 0.13 P5 — Frozen September Broadcast Source-Acquisition Receipt

Stage: C3X 0.13 P5; state: SOURCE_SCAN_AND_PRECOMMIT_ONLY; no chess preferences or concept transport adjudicated.

- Original Drive raw file: `lichess_db_broadcast_2026-09.pgn.zst`, ID `1GTQWzz33Cp0FFaTKIkLyaxRWGFh1fUGh`.
- Exact compressed bytes: 18,414,369, SHA256 `27a39d035767a30901b89602f33f2a7b27d4ab5025842071165fa079f8fff1df`.
- Decoded bytes: 127,144,095; event-header blocks: 28,638. Unique September standard-tagged Lichess broadcast game URLs: 27,503; unique BroadcastName values: 299. 422 records have other dates; 713 lack required source/standard tags; no outcome-based exclusion.
- Deterministic fixed sample: among each distinct BroadcastName, choose lexicographically smallest GameURL after Date begins 2026.09 and Variant=Standard; sort groups by SHA256(BroadcastName) then GameURL; retain first 16 distinct broadcast groups, never replace failures after legal replay or engine outcomes.
- Frozen 16 ordered raw-game-segment SHA256 concatenation digest: `7f9e865ced89aa47ed06aac5fa0d40ff02481f8ff4e696f12769fdcffbc9fa1b`; ordered GameURL concatenation digest: `7ab9cb6a2996b6f982bcdf39417a293f8ae5c7b5a6f9e45d99c1799951a92d31`. One selected event is labeled `CAMPEONATO NACIONAL 960` despite Variant=Standard: chess legal replay MUST adjudicate this discrepancy; no adaptive replacement.
- External corpus source: https://database.lichess.org/broadcast/lichess_db_broadcast_2026-09.pgn.zst ; provider: Lichess; source license CC BY-SA 4.0 per official broadcast database https://database.lichess.org/ ; maintain Lichess attribution and terms for derivative published excerpts.
- Selection does not use [%eval], time controls, score, outcomes, human concept or Stockfish. No claims of independent provider/engine ecology; selected 16 broadcast groups, not proved statistically independent people/events/positions. Exact six C3X 0.12 frozen FEN hashes must be excluded at new ply32 position.
- Source independence relative to P16 August and 0.12 six events is only provisional until immutable GameURL/event/FEN equality audit. Do not merge 16 PGNs into a confirmatory cohort without that audit.

Next: execute read-only legal replay and board-rule concept predicates with adversarial counterexamples. A PASS here authorizes board semantics only, not a mechanism-concept causal explanation.