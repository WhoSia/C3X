# C3X 0.14 P1 — Prospective S29 Official-Game Development-Only Native TT Cutoff Transfer Precommit

**Signed before analysis of source-disjoint Stockfish root score responses.** Frozen source: [public 4-game S29 intake](https://github.com/WhoSia/C3X/actions/runs/37800438225), exact `P1_source_eligible_development.json` SHA256 `bbaef73beda60d9e03c9f83324651db3b130606be4c84cb9f8a170a958a96274`. Four independent opening-prefix groups in the same official TCEC S29 Superfinal source file. Four additional sealed groups are **not allowed** as development inputs; the separate holdout artifact may not be downloaded by this engine job.

## Test and primary outcome
For each of the four development root FENs at exactly 18 historical plies, with a legal same-original-square pawn single vs double advance pair, run pinned official SF16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Threads=1, Hash=16MiB, `MultiPV=2`, and exact UCI `go depth D searchmoves a b`, D ∈ {8,12}, 2 independent cold engine processes per root/depth. Freeze source file and pair orientation before engine calls.

Compare unmodified SF16 vs same-source EP9 observational sham at `OFF` with exact bestmove, two root scores, PV and nodes. If sham diverges, invalidate any causal reading for that cell and keep failure. If identical, measure EP9 `MAIN` early TT-bound-return-family suppression, `QSEARCH` suppression, and `BOTH`. This intentionally tests **coarse source-native path family susceptibility**, NOT the EP10/EP11 CECLUB key or specific 32nd cutoff event. Never transport a Zobrist key from one chess position to another.

Primary outcome across source games: count which of the 4 distinct game groups have at least one first-choice flip in either depth for the MAIN-only intervention. Secondary: count by depth and arm, signed within-Stockfish two-legal-root cp gap, mode-specific blocked TT returns, native first PV changes and nodes. Do not compare mate and cp or stop on a positive flip. Both cold processes are determinism controls, NOT extra games. Keep ALL negative results.

No new control over chess semantic mediation is introduced by a legal single/double pawn push; tactic/capture/free-reply rivals remain. Even an observed flip is an algorithmic implementation-path response, not proof of passed-pawn creation or human positional value. Future sealed-holdout test must be a *different precommitted job* with no developmental selection feedback.

Prior relevant works: Méndez et al. 2023 output-level chess metamorphic consistency, Martin et al. 2025 corrected real-game and depth-selection sensitivity, Clark et al. 2023 DAG-guided metamorphic relations; Geiger et al. 2025 causal abstraction and Zhang & Nanda 2024 intervention metrics are methodological comparators.

GitHub Actions contents:read; no bot commits. Preserve source data SHA, binary hashes, patches, native telemetry, original GPL license, artifact ZIP hash and independent group IDs. 0.14 P1 may PASS for a methodologically sound development pilot even if zero root flips; transport of semantic concept and independent holdout remain HOLD.
