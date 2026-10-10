# C3X 0.23-P1-R2 — Counterfactual SEE-Activation Mediation & Computational-Node Identity

**Design proposal recorded 2026-10-11 (KST), before interpretation of P1-R1 TT-FIRST outcomes. NOT an executed mediation claim.**

## Key structural correction

For a fixed native Stockfish16 `Position::see_ge` implementation and identical complete input tuple (position/bitboard, native move, optional occupied bitboard and threshold), output is **deterministic**. If TT suppression leaves these inputs exactly unchanged at the same event, SEE's native Boolean cannot naturally change solely because TT was suppressed. Therefore the natural TT→SEE→bestmove pathway can operate through:
- SEE **site activation** (event occurs versus does not occur),
- which descendant search nodes are visited,
- source move offered to SEE,
- SEE threshold and optional occupied bitboard passed by the caller,
- prune-or-search branch consuming the unchanged SEE result,
- alpha/beta/evaluation and downstream candidate survival.

Artificially toggling the native bool is a different operator `do(SEE_BOOL = ! SEE_BOOL)`, a **robustness/sufficiency perturbation** rather than evidence that TT naturally changes `see_ge` output at identical arguments. The 0.22 D2 case (joint-arm changes TT-alone result 3/6) is an experimental policy effect, not a natural mediator claim.

## Source-alignment causal graph

Let `T\in{0,1}` indicate exact physical first reader suppression and `S_t` search state at a native search call: `(root source, candidate, depth, ply, alpha, beta, TT raw entry and source history, ancestor chess position trajectory)`. Let `E_t` be the **event tuple** `(is_called, site, position key, move, optional occupied, threshold, SEE boolean, consuming branch)`. Let `Y` be final UCI bestmove. Need to identify causal edges `T→S_t→E_t→search descendants→Y` with actual timestamped source events, not mere correlation of `E_t` and `Y`.

**Important constraint:** a common `pos.key, parent key, path hash, rootcall, native move, site, threshold` in StageB R1 is a **weak node correspondence**; the search `depth, ply, alpha, beta, node type, rule50 count, occupied bitboard, TT bound` can still differ. Label `SOURCE_PATH_MATCH_ONLY`, not equivalent `COMPUTATIONAL_STATE_EQUAL`.

## Proposed P1-R2 experimental order (must remain separately registered before interventions)

1. **Close R1 only after verifying 124 original source-first roles** and 248 literal UCI strings pre-treatment. R1 executes *only TT FIRST* with passive SEE logger. Classify every role `TT_CONTACT+COMMON_SEE_PREFIX`, `TT_CONTACT+NO_COMMON_SEE_PREFIX`, `HOLD_CENSORED`, `NO_PHYSICAL_TT_CONTACT`. Audit candidate counts per *game*.
2. Extend source-level native instrumentation with **global monotonic native event serial** shared between TT first-consumer log and each SEE source call. Require actual `TT_reader_block.serial < SEE_call.serial`; otherwise the common event precedes the intervention and cannot mediate it. Compare TT original score use vs actual cutoff site separately (actual operator evidence, not probe hit).
3. Extend instrumentation with `ss->ply`, depth, alpha, beta, PV/nonPV, position rule50 count, the optional occupied bitboard, and **exact SEE-consuming pruning branch outcome**, in addition to originally measured `parent_key64`, `path_hash`, `path_length`, `pos.key64`, `native move`, `site`, `threshold`, `original Boolean`. If these differ, retain `SAME_CHESS_PATH_DIFFERENT_SEARCH_STATE`, **not identical computational node**.
4. Select from development-only original R1 outcomes a shared node only by an a priori deterministic rule (earliest chronologically eligible *after source TT reader*, unique within both arms, quiet or qsearch pruning sites, bounded parent/path identity). Register **its entire source signature** (key, parent hash, path hash, site, move, threshold, root-call, source candidate, native event serial constraints) *before* any SEE actuator test.
5. Two interventions to distinguish: (A) *targeted prune predicate* forced original/opposite at that **same native source identity** (mechanistic operator perturbation); (B) bounded **threshold-only** alteration at a source call with same board and native move, with recorded threshold, keeping legal move generation and Stockfish native SEE function intact. Never flip quiet/SEE Boolean by rootcall alone. Treat no common actual contact after TT path divergence as no identification, rather than force at a different descendant.
6. Propose a 2×2 source intervention with cold duplicate, sham, event serial, genuine physical TTL source writer→reader, source matched SEE contact, exact bestmove, root-depth leader, actual alpha/beta change and token counts. For categorical bestmove, report game-level patterns, not fabricated scalar “mediation proportion”. Any SEE-pruning effect must be assessed against a sham-at-same-site negative control.
7. **Distinct ecology and rights:** new May broadcast CC BY-SA 4.0 and nonmate CC0 puzzles already P1 frozen; THESE DATA BECOME DEVELOPMENT once TT outcomes opened. Any new *M3* exact-UCI generalization must be sealed with literal forecast and a later **not-yet-seen new dataset**, never retrospectively created on this heldout32 after actual TT effects are observed. Retain the previously sealed M0/M1 for prospective evaluation.

## Falsification and publication stop conditions
- If common node exists but is temporally **before TT first-use event**: label `NONMEDIATING_PRIOR_EVENT`.
- If `SEE Boolean` at identical board/move/occupied/threshold naturally differs: require source instrumentation/data-corruption investigation, not discovery of novel stochastic SEE physics.
- If path hashes match but search window/ply differs: preserve `SAME_BOARD_DIFFERENT_COMPUTATIONAL_NODE`.
- If common episode not observed within first32 capped trace: `HOLD_CENSORED`, no claim absent elsewhere.
- If target site does not actually fire in any 2×2 arm: `NO_CONTACT`; do not reassign intervention to a later/different SEE call.
- If TT order+SEE predicate change jointly affects bestmove with no preserved source identity or temporal ordering: record a **policy interaction only**, not natural TT→SEE mediation.
- If result is nonpositive: document failure and move on rather than relabeling motif, root order or speculative predictor post hoc.

## Rights

TWIC reuse-permission inquiry user reports sent from a different account; no automated email verification or Gmail read required. 0.23 source publication permissions are tied to individual origin sources, not email address. P1 test is restricted to Lichess broadcast BY-SA and CC0 puzzle records. Publish only rights-reviewed, reproducible metadata and source checksums; disclose modified GPLv3 Stockfish engine source/patch obligations if distributing engine binaries.

**P1-R2 status:** DESIGN PRECOMMIT, no SEE actuator run and no third-party data redistributed by this document.
