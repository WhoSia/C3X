# C3X 0.24-P3 — 128-Game September2025 Fresh Chess-Source Trial and Frozen M3-v2 Gate

**PRE-EXTRACTION DESIGN LOCK — 2026-10-11 KST. 0.24 ACTIVE; NO new archive bytes opened / no new native treatment outcomes viewed at time of design.**

## Power and independence

Collect **128 distinct real Standard chess games** from official Lichess **2025-09 broadcast** PGN archive `https://database.lichess.org/broadcast/lichess_db_broadcast_2025-09.pgn.zst` (CC BY-SA 4.0). Original complete games and identifying headers stay private. 128 source-independent games improve empirical precision over the 16-game Aug2025 pilot but do not make 512 correlated O/F × STRICT/BROAD role cells independent.

Before archive fetch: scan **maximum first 20,000 games**, select the **first 4,096 eligible records** under deterministic source-only rules; eligible = Standard chess (no variant), no PGN parser errors, legal initial board, ≥70 halfmoves, unique complete-game SHA256 of (all original headers + full legal played UCI sequence) kept as hash only, deterministic root ply = `30 + int(first_8_hex(game_sha),16) % 15`, legal original played root move without promotion, ≥3 legal alternatives and no duplicate FEN4 or prior historical FEN4. Once first4096 eligible found, **sort by complete-game SHA256 and take the smallest 128 distinct games**. No source-based cherry-picking for likely engine flip or positive M3. If quota unmet, HOLD; no arbitrary replacements or altered game selection.

Read-only verify complete prior source cohort receipts for P4 + 10 historic Oct–May source groups **and August2025 16 selected legal roots** (at least 12 source manifests); maintain exact original raw SHA256 gates in CI, and exclude every prior FEN4. Scan against historical source FEN4 before selection; report overlap and unavailable historical data as HOLD, not success. Exact user-facing original source data is not redistributed.

## Truthfulness about features / M3-v2

New `M3-v2` must use only pre-treatment native original StageA and source features (TT actual physical pre-dose writer-reader candidate, first reader role, untreated O/F depth ladder instability, root candidate and full source-key path, passive SEE pre-dose evidence). Avoid post-FIRST or SEE-flip causal outcomes. Existing Aug2025 P1 evaluation is DEVELOPMENT-EXPOSED and M3 previously gave **58/64**, identical M0 **58/64**, so cannot be re-used as a test. Make M3-v2 implementation, model version, exact sources and all 128×4 literal UCI forecast strings immutable in human-authored Git **BEFORE any September physical TT/SEE interventions**. M3-v2 model is required to give a nonzero predeclared positive trigger rate or it will be considered no improvement; do not condition experimental unit inclusion on trigger status.

## Evaluation

Separate source-only P3-S, untreated native P3-A, literal pretreated 4/5-model seal P3-F, and physical TT FIRST P3-B (and additional legally grounded SEE probes only as separate precommits). Evaluate M0 unchanged, failed M1 opposite-order, failed M2-depth11, failed M3-v1, M3-v2 per role but infer at game level (128 clusters), with pairwise exact-match wins/losses and uncertainty. Technical source contact PASS is not model superiority. Report number with no physical TT contact, source root path divergence, censored SEE, no prediction. No new engine/PGN provider cognitive generalization from a single SF16 engine.

## Publication / governance

Read-only GitHub Actions `permissions: contents: read`; no bot-authored/committer/co-author commits. Do not include full source PGN, headers, player names, complete original move lists, private TWIC rights communications, or modified Stockfish binary in GitHub public outputs. BY-SA credit/notice and license source metadata; technical scanner PASS not legal opinion.

**Important:** This preregistration authorizes *source-only* extraction next; it does NOT authorize a new 128-game treated experiment without separate Git-literal M0/M3-v2 forecasts and original source/StageA SHA witnesses.