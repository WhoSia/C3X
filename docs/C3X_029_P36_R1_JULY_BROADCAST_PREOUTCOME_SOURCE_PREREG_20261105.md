# C3X 0.29-P36/R1 — July 2026 External Game Source Intake and Pre-Outcome Court

**Date:** 2026-11-05 KST. **PRE-DATA DESIGN**: this GitHub document was committed BEFORE retrieving or inspecting the proposed July source data or its engine evaluations. July source is a candidate for game/event-disjoint external validation, not proven never seen by C3X historically.

## 1. Claim budget and source selection

Source candidate is the official Lichess broadcast [July 2026 PGN Zstandard corpus](https://database.lichess.org/broadcast/lichess_db_broadcast_2026-07.pgn.zst) from [official index](https://database.lichess.org/broadcast/), released 16-Aug-2026, approx 24.5MB compressed. Prior C3X 0.28 records directly show official June, August and September files, not the July file; a bounded Drive filename search for July returned no matching file. This is NOT proof of lifetime nonexposure. Correct label until verified: **SOURCE_CANDIDATE_NOT_ADMITTED_HELDOUT**. Retain Lichess CC BY-SA 4.0 attribution and original source checksum.

**Freeze BEFORE engine:** parse original July PGNs in file order, accept only complete, standard chess games with no parser errors and at least 60 halfmoves, original start position (no FEN/SetUp), usable unique event/date/players, nonempty valid match result, and deterministic source identity. Scan the first 1,000 valid eligible games, select the eight smallest SHA256 digests of canonical full game UCI history + source tags with deterministic tie break; pick a fixed board at historical ply 30 per selected game, only if legal and nonterminal. Count all exclusions explicitly; don't adjust the eight after seeing Stockfish outcomes. The selected cohort and source SHA are to be sealed and uploaded prior to any engine-based score/margin screening. **If only partly downloaded or source duplicate unknown, HOLD.**

Compare normalized full-game UCI digest against all accessible old C3X source ledgers before claiming independent games; the old 0.28 64-case registry must be checked by canonical source SHA or UCI fingerprints. Distinct month ≠ guaranteed independent tournament/player/event. Require independently recorded tournament/event family, not merely file month, before event-disjoint claims.

## 2. Predeclared experimental question

**Does a reply-conditioned, foil-specific forecast of a chess consequence add correct information beyond score and PV at equal compute and equal prediction budget?**

For each selected game fixed position, evaluate candidate two legal moves with native source-pinned Stockfish 16 under a **joint common search budget**, with consistent viewpoint and options. Do not select positions or root candidate sets posthoc for answer utility. Report candidate margin strata near (<20cp), intermediate (20-100cp), wide (>=100cp) only as descriptive/subgroup categories, and retain all cases (including no near ties). Near-equal remains primary target but a null yield is a valid diagnostic, not reason to retrospectively change the selected cohort.

Each proposed rival explanation produces exactly ONE claim/prediction per board-pair and must record abstention. Predeclare one verifier measurable from the board's **legal opponent reply universe**, not sourced exclusively from the explaining model's sampled PV. Equate forecast cardinality, chess API access, and **native engine node budget** for Stockfish+PV vs minimal foil-aware conditional JSON vs full C3X. Avoid giving C3X a larger per-reply oracle computation allowance under the guise of explanation. Use independent chess law to check legality and future material; deeper engine oracle, if used, must be segregated, engine-version/source-pinned and frozen, and is a finite-depth adjudicator not ground truth chess value.

Primary score: predeclared per-game paired Brier/logloss for falsifiable binary Q (with explicit abstention accounting); report factual legality, source budget and position-wise errors separately. Do not compare inclusion of 3 replies to an exact 1-reply baseline. If C3X does not add information beyond simple JSON and PV, mark fail and simplify.

## 3. Immediate one-step executability gate

Build **only** a reproducible engine-blind July-source provenance + deterministic eight-game freeze script, with pure parser tests and raw original SHA. Verify Lichess licensing and no game overlap with known archival 16 and 0.28 64 source as far as available. Persist original PGN raw and selected manifest to Drive BEFORE any Stockfish call. No 'prospective' claim merely because new source is a different month. Do not spend time on new neural instrumentation.

Native Stockfish/forecast comparison only after cohort has reproducible provenance and game-disjoint gate. Keep already proved P35-R7 actual NNUE route parity evidence, but it is supporting mechanistic work, not a new explanation advantage.

**Governance:** Notion scientific authority, Drive raw bytes, GitHub human-authored code only. Actions is read-only compute/artifacts; no github-actions[bot] commits/pushes/merges/tags/ref moves.
