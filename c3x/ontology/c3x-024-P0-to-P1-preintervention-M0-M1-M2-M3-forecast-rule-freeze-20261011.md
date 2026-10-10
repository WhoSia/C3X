# C3X 0.24 — P0→P1 Literal Bestmove Forecast Models (PRE-TT/SEE-TREATMENT RULE FREEZE)

**Status:** MECHANISM_MODEL_ALGORITHM_PREREGISTERED_BEFORE_ANY C3X0.24 NEW FIRST / SEE TREATMENT. Git file creation must precede reading treated outcomes. The new Aug2025 source-only selected-16 literal game hashes were previously frozen at commit `c70735ea191365ec88b3fada9ff0e7cdc9d1042c`. The untreated native StageA at 16 legal source games is permitted to be read to instantiate literal values; it is NOT treatment data.

**New frozen source:** Official Lichess Aug2025 CC BY-SA 4.0 compressed SHA `f925d1f3b494517c8eae223976a886bed77a7b8627b17ec287e50cdda766dae8`; engineblind 16 source JSON SHA `76391058cae1fad8d23e3ae8556e48b63a0d991a051c59fef2df15e11c73f529`; 16 pre-native source SHA literal `c3x/forecasts/c3x-024-P0-Aug2025-16game-literal-source-Git-seal-before-native-20261011.json`.

## Population and experimental unit
- 16 distinct frozen August 2025 source games. Each supplies two possibly correlated O/F native root search orders and two STRICT/BROAD physical TT first-reader roles. **32 worlds or 64 role cells are NOT independent games.**
- Source-eligible role only when StageA passive exact TT source writer→reader identifies one literal first eligible physical pair. Ineligible or censored records remain excluded from intervention and forecast-score accuracy denominator only under the pre-specified eligibility rule; always report total 16 source games and all 64 potential role cells.
- Stockfish16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Threads1, Hash16MB, NNUE OFF, depth12, cold identical (same source standard as 0.23).

## Four **deterministic** candidate models, fixed before FIRST/SEE

For each eligible (game, order O/F, physical STRICT/BROAD) tuple, let `b_o` be the untreated final native root bestmove UCI of that order and `b_{other}` the baseline UCI for the opposite order; `r` the original first physical TT source reader's native `root_candidate_native`; `b_o^{native}` the same chess-legal root move encoded exactly as pinned Stockfish16 internal Move; `d11` the observable (if available) native root leader at depth 11; and `S_o` whether a passive, complete (noncensored) original first32 SEE source witness exists *for that same first physical STRICT root source*. These are pre-FIRST/SEE-treatment source facts only.

- **M0 (primary null):** forecast `b_o`, i.e. no change.
- **M1 (failed historical cross-order rival):** forecast `b_other}`. Retain earlier 0.23 M1 111/124 versus M0 117/124 FAIL; no refitting.
- **M2-depth11 (new explicitly named comparator, not rebranded earlier M2 algorithm):** forecast legal `d11` mapped to literal UCI using the source board + pinned engine move encoding. If absent, ambiguous or not legal, emit `NO_PREDICTION` before treatment; do NOT retroactively substitute the observed treated UCI or count a censored guess as correct. Historical TWIC1664 M2 result 54/64 = M0 54/64 remains FAIL.
- **M3 (precommitted source-bound sensitivity filter):** forecast `b_{other}` ONLY if all of: physical first-reader source eligible, `b_o != b_{other}`, `r == b_o^{native}`, STRICT role (because only STRICT source-root SEE watcher is populated in inherited StageA harness), and a noncensored original observed `S_o` SEE event at the strictly corresponding root-call. Otherwise forecast `b_o`. For BROAD, exact M3 reverts to M0 without inventing cross-role SEE contact. The source-guard event must **not** be artificially flipped for this predictor. The rule is not asserted to be theoretically sufficient.

**Failure rule:** if `root_candidate_native` or the baseline native bestmove cannot be securely encoded, flag `SOURCE_ENCODING_HOLD`; never infer match from text resemblance. Every emitted exact UCI must be chess legal in the frozen root board.

## Timing and scoring guard

The dedicated forecast Git artifact MUST preserve source JSON SHA, StageA raw SHA, all literal predicted UCI strings, role scope, source identity and model outputs **before any native TT FIRST or SEE FLIP on this new 2025-08 corpus**. A new code/model edit after treatment begins creates a distinct postoutcome exploratory variant and cannot rescue prospective M3.

For exact-choice evaluation, report each model's prediction vs physical FIRST terminal UCI per eligible role and distinct source game. Primary compare M3 vs M0 at **source-game clustered** granularity: number of games where M3 has at least one correct role and M0 does not, versus reverse. Report role-level too for diagnostics, not pseudo-independent statistical significance. Secondary among actual bestmove-flip games: conditional exact new-move accuracy and flip existence sensitivity. Preserve treatment no-contact/CENSORED/PATH_DIVERGED as explicit denominator accounting, not replacements.

If M3 does not beat M0 on newly selected distinct games, **scientific M3 FAIL or INCONCLUSIVE** even when native contact/CI succeed. M3's failure does not negate already verified local 0.23 T3/T4 causal effects.

## Immutable boundaries
- Original TWIC PGNs and personal source-letter stay private. Lichess broadcast BY-SA attribution/changes and modified Stockfish GPLv3 obligations apply; no raw PGN or patched binaries in GitHub artifact.
- GitHub Actions `contents: read` only; human WhoSia Git commits, never github-actions[bot] authorship/coauthor.
- No natural TT→SEE mediation, descendant survival or chess-engine cognition claim from scalar model accuracy.
