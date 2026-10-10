# C3X 0.24 — Causal Search Explanations & Counterfactual Decision Transfer in Chess: Exact-Node Mechanism Certificates, TT–SEE Conditional Interactions, Branch-Survival Mediation Tests, Prospective Bestmove Prediction & Rights-Audited Cross-Ecology Falsification

**Formal version state: ACTIVE — USER-ACCEPTED 2026-10-11 (Asia/Seoul). P0 organizational research opening, not a claim that P0 prospective model gates have passed.**

## Authority / continuity

The user explicitly accepted this exact full title. **C3X 0.23 is closed as the active version but remains an immutable historical evidence chain; pending T5 / R4 obligations and negative gates are carried forward into 0.24-P0 / P1, not marked done.** Do not relabel any existing 0.23 CI artifact, repository path, SHA, date, negative result, or formerly precommitted scientific statement.

Prior validated **development-only** evidence:
- 0.23-T3: actual Stockfish16 source-pinned TT FIRST x single exact-site SEE return 2x2, native successes [#38070604820](https://github.com/WhoSia/C3X/actions/runs/38070604820), [#38070768528](https://github.com/WhoSia/C3X/actions/runs/38070768528). Two May2026 broadcast positions, not 8 independent chess games. May #2 joint TT+SEE creates new `b1b4`, neither singleton changes `e1g1`; May #11 TT-alone changes bestmove but added SEE does not.
- 0.23-T4 actual taken `continue` / SEE-guard-pass native witness **8/8 arm worlds**, 16 cold repetitions, original T3 full private SHA exact: [#38072795238](https://github.com/WhoSia/C3X/actions/runs/38072795238), [receipt](../receipts/c3x-023-P1-R2-T4-native-actual-prune-continue-branch-and-T3-observer-equivalence-20261011.json). Original T4 source-anchor run #38072709627 was TECHNICAL_FAIL; retained.
- **Unproven:** actual downstream `do_move` and child-search ancestor chain between chosen native SEE guard and terminal root bestmove; natural `TT→SEE` mediation; cross-ecology transfer of source mechanism; prospective per-position exact-UCI model improvement.
- Preserve historical scientific failures: 0.23 R1 M1 **111/124**, no-change M0 **117/124**; 0.22 TWIC1664 M2 **54/64** tied M0 **54/64**; earlier F19.5/K4/Jan/PAG negatives. No model renaming or denominator-inflation rescue.

## Central research question

For a particular frozen legal chess position and engine regime, **what minimal, independently checkable execution certificate suffices to attribute a counterfactual root-choice change to a specific native search branch, and does a forecast using such certificates beat frozen null and rival forecasts on an untouched source cohort?**

A source-operator effect is not evidence of chess understanding, an optimal move, a general law or natural mediation. The target is a falsifiable execution-graph account of Stockfish decision-making.

## Formal target / notation

Freeze before evidence review: board `x`, root order `o∈{O,F}` (F means archival played move artificially put first), regime `r=(Stockfish16 git 68e1e9b3811e16cad014b590d7443b9063b3eb52, Threads1, Hash16MB, NNUE OFF, depth12)`, TT treatment `t∈{0,1}`, SEE treatment `s∈{SHAM, FLIP}`, literal native source event signature `k` and observed root choice `Y(x,o,r,t,s;k)`.

For fixed `x,o,r,k`, define categorical controlled interaction when `Y(0,0)=Y(1,0)=Y(0,1)≠Y(1,1)`. This is *not* an assumption about a natural mediation path. For numeric search cost `N`, the factorial contrast is `I_N=N(1,1)-N(1,0)-N(0,1)+N(0,0)`; cannot perform arithmetic over UCI move IDs or infer saved descendant count from nodes.

## P0 — mandatory version-open governance and fresh-source-first court

- Version title / status / rights and epistemic boundary can be opened upon user acceptance **now**. The **prospective mechanism or M3 PASS** gate remains independent of administrative activation.
- **New source precommit**: use *Lichess official 2025-08 broadcast PGN* only (not June 2026, already used). Source URL `https://database.lichess.org/broadcast/lichess_db_broadcast_2025-08.pgn.zst`, archive page `https://database.lichess.org/broadcast/`, source category CC BY-SA 4.0. The reference had no exact archive string in the repository code search at precommit; this alone is not proof of zero prior position overlap.
- Before extracting source: deterministic, engine-free selector first 512 eligible Standard chess games scanned from first 20,000 PGNs; at least 70 plies, unique complete-game fingerprint SHA256(headers+mainline UCI) and legal board. Root `at = 30 + (int(first8hex,16) mod 15)`, legal played root move (not promotion), ≥3 legal root choices; sort 512 eligible by game SHA256 and choose **16 smallest distinct**. No outcome-based case replacement.
- Exclude every source-only accessible historical `fen4` from all available prior C3X archived cohorts (0.16, 0.18 Oct-Dec, 0.19 Feb, 0.20 Mar, 0.22 Apr/TWIC/puzzles, 0.23 May/puzzles). Require exact archived historical file SHA gates, log missing/exclusion as **HOLD**, not as 'disjoint verified'. Scan *all* 512 eligible records for old-position FEN collision before freezing.
- **Source phase FIRST**: only original archive source SHA, redacted 16 source positions, ordered hashes, chess-law sanity, and immutable selection receipt; absolutely NO SF16 baseline or TT-FIRST / SEE-FLIP in this phase. Official original PGN and player headers stay private; public aggregate and small BY-SA-derived research packets are rights-scanned, with licence link, credit and transformation notice.
- Next **untreated native Stage A** only after an immutable source-only artifact SHA and Git-literal registration; establish O/F root bestmove, node/score/depth and TT eligible physical writer→reader roles under identical native regime, with original SHAM cold control and no target mutation.
- Before **ANY** treated FIRST/SEE: Git-seal literal M0 (no-change), M1 (historical failed opposite-order), M2 (historical failed survivor if definable), M3 (predefined mechanism candidate) per eligible game/root order/role with a strict NO_PREDICTION/HOLD on unavailable source features. All source IDs, role masks, model source definitions, expected new exact UCI, and adjudication rule are sealed. An exact posttreatment string cannot be fabricated by selecting from posttreatment outcomes.
- Finally independent TT treatment source proofs/cold audit and strictly case-level scoring. A positive M3 claim requires *game-level* improvement over M0, not merely interaction count or technical CI SUCCESS; report 95% uncertainty where sample supports it, otherwise 'pilot'.

## P1 — causal certificate semantics (next design)

Certificate tiers:
- `C0`: rights/provenance+immutable board legality;
- `C1`: exact source TT writer/reader and SEE call `key64, parent, full ancestor key path, root candidate, depth, ply, alpha/beta, PV, qsearch, rule50, threshold, original value`;
- `C2`: source observer validates actual original `continue` or passes SEE guard, with sham and cold equivalence;
- `C3`: observer validates downstream `do_move`, child search entry, return, and root candidate survival path with exact source parent→child lineage, explicitly CENSORED/PATH_DIVERGED when not observed;
- `C4`: independent held-out prediction of literal UCI and direction of sensitivity, scoring against fixed M0/M1/M2.
Tier nesting is mandatory: `C2` does not imply `C3`; `C3` does not imply `C4`.

Future risk: conditioning analysis exclusively on posttreatment source contacts selects a collider. Preserve every `NO_CONTACT, PATH_DIVERGED, CENSORED, OBSERVER_PERTURBATION_HOLD, RIGHTS_HOLD` and total game denominator.

## P2–P4 roadmap

- P2: focused exact source operator parent and branching genealogy, rival explanation such as root reordering vs TT-induced alpha-window vs SEE guard vs later pruning; negative May #11 mandatory.
- P3: prospective new-source exact bestmove counterfactual transfer, group by independent source **game**, benchmark baselines, publish negative cases.
- P4: cross-engine / provider replication with actual source semantics differing per engine, meaningful legal recapture / king safety evidence, independent review and rights-audited minimum reproducer. No model cognition or universal chess claim.

## Governance

All research writes attributable to human `WhoSia`. GitHub Actions `permissions: contents: read` only, never self-commit or add `github-actions[bot]` to contributors/co-authors. Do not publish original third-party PGN / complete game strings, personal TWIC editor email, or patched Stockfish binary without GPLv3 obligations being discharged; technical scan PASS is not legal permission. README & Notion current version updated separately. An official title approval is **not** a scientific PASS.

**P0 status on creation: VERSION_ACTIVE / SOURCE_PRECOMMIT_SAVED / NEW_ARCHIVE_BYTES_NOT_YET_FROZEN / M3_NOT_PRECOMMITTED / P3_NOT_EVALUATED.**
