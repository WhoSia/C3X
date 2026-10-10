# C3X 0.23-P1-R2-T2 — Source-Exact Native SEE Prune-Return Interventions at Shared Post-TT Search States

**Preactuation protocol (2026-10-11 KST). No T2 site-specific SEE intervention has been executed on these T1 matched sites.** The six cases are retrospectively selected P1-R1 development cases, NOT independent heldout.

## Frozen empirical motivation and necessary conditions

- S0 32 independently selected licensed chess roots SHA `0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61`; untreated native Stage A SHA `fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442`; M0/M1 exact-UCI forecasts frozen pre-TT intervention.
- R1: 124/124 physically verified TT FIRST reader blocks, 2508 common path SEE witness episodes, 7/124 final move changes across May broadcast 4 games, zero puzzle changes; M0 117/124, M1 111/124 (M1 negative).
- T0: in six predeclared post-outcome development cells, 21 shared post-TT-operator SEE events in 4 cases, 2 capped/HOLD. One noflip control game #2 has 14 such events; event presence insufficient.
- **T1 verified** with native source four SEE sites augmented with source `ss->ply`, `depth`, `alpha`, `beta`, `pos.rule50_count()`, `occupied_given`, `occupied64`, plus P1 parent/path 64bit signature and original SEE bool: **21 shared post-source SEE events preserve all these recorded fields in 4/6 development cases; 0 observed differing-state events; PV/cutNode and full raw ancestry-vector remain uninstrumented.** No SEE return values altered during T1. T1 Actions #38068375315 source-patch and tests pass.

## Deterministic, outcome-independent T2 target selection rule

Retain *exactly* frozen `SELECTED=((1,O,STRICT),(8,O,BROAD),(11,F,STRICT),(12,F,STRICT),(2,O,STRICT),(3,O,STRICT))`, never replace #8 or #3 if their prefix censored.

Cold rerun same pinned Stockfish16, 1 Thread, Hash16MB, NNUE OFF, depth12, original source patch stack **plus read-only T1 window observer**. For each case:

1. Observe original TT source passively, using actual score use (`used`, `main_cutoff`, `qsearch_cutoff`) on exact physical full64 key/root_call, and separately verify first physical writer→reader block in V/FIRST TT arm (key64/slot/epoch/rootcall/root native candidate); cold duplicate and sham verify same sixfield UCI.
2. Match **source event identity** `(rootcall,root native candidate,position full64 key,parent full64 key,ordered ancestor-path64 hash,path length,SEE native move,one of quiet_prune/qsearch_prune,SEE native threshold)` uniquely in both original and TT FIRST, and reject duplicate source identity within first32 logs.
3. Require original SEE return == delivered in both arms, same native bool, and **exactly equal** `(ss->ply,depth,alpha,beta,rule50,occupied-present,occupied64)` in both. For strictly causal chronology original exact TT value-use source UCI log ordinal must precede original SEE event, and treated exact full64 physical TT reader-block UCI log ordinal must precede its SEE event. Any unavailable source use/TT contact/trace ambiguity/HOLD => no intervention.
4. Among *pruning* sites satisfying #1–#3, choose **first by original synchronized UCI line ordinal**, then lexical `(site,key64,move,threshold,path_hash)`; never use observed final UCI change to rank targets. If none, record `HOLD_CENSORED` or `NO_ELIGIBLE_COMMON_POST_SOURCE_QUIET_SEE` and execute **zero** SEE actuation in that case. Number of eligible cases unknown at commit and must not be inferred as four just because any SEE was shared.
5. Record the selected native event's exact signature **before invoking a SEE actuator**, including original full64 key, rootcall/root native move, parent/keypath, move/site/threshold, ply/depth/alpha/beta, rule50, occupied present/64. A 64bit path hash is an identity *fingerprint*; no claim full ancestor-vector byte identity until separately collected.

## New native first-site operator actuator

A separate C++ overlay **after** read-only T1 source observer adds strict opt-in `C3X023_T2_*` environment parameters for **every** identity field listed above. Only if *all* match the native wrapper's live source arguments and **only on the first exact matching occurrence per cold process** return `!Position::see_ge(...)`; otherwise return original Boolean. No chess move legality or input mutation. The code must make a source `kind=forced` record if the selected intervention would otherwise fall past first32 log cap, and must not expose individual source FEN/UCI in public Actions stdout. Require actual `altered=1` at exactly one source event with all identity parameters unchanged; zero/multiple = `NO_CONTACT/TECHNICAL_HOLD`, not evidence of no effect.

For each eligible case run **cold duplicates** and reproducibility controls:
- `T0/S0` unmodified passive OBS; `T1/S0` physical original TT FIRST suppression, passive SEE;
- `T0/S1` one exact native SEE bool forced at locked same-source event;
- `T1/S1` same source exact event force with original TT FIRST;
- sham `T0/SHAM`, `T1/SHAM` with impossible full64 SEE key, verify no SEE force and identical native baseline / TT-only.
- If SEE actuator changes upstream search such that original intended TT selected first-reader no longer physically blocked in a joint arm, label `TT_SOURCE_NO_CONTACT`, not a validated 2x2.
- Endpoint final UCI bestmove and depth leader/TT score-use vs cutoff; categorical operator policy interaction based on four actual paired arms; **not a natural mediation fraction**.

## Validation and limits

T2 has already observed R1/T1 outcomes and remains **exploratory six-case mechanistic experiment**. No M3 exact-UCI predictor can be scored as prospectively validated on this cohort. Same observed SEE original bool under matched full native arguments should be deterministic. Artificial return flipping is an operator sensitivity experiment, not the natural TT→SEE path; a genuine natural mediator concerns activation, threshold, path and consuming prune. `PV/cutNode` and exact full ancestry vector are not yet source-level compared; if absent, label `SOURCE_WINDOW_MATCH_NOT_FULL_COMPUTATIONAL_IDENTITY`. The target's causal effect must not be advertised as evidence of TT→SEE natural mediation unless additional exclusion and original activation witnesses hold.

## Rights

Only source-licence-verified Lichess CC BY-SA 4.0 broadcast/CC0 puzzles. Public artifact contains only aggregate counts, modified engine source manifest hashes, source URLs/licence notice; no raw original PGN, individual broadcast positions/moves, or compiled modified GPLv3 engine binary. TWIC inquiry sent from user's separate email but not a task dependency.

**Explicit scientific stop condition:** if no shared post-TT source event of site quiet_prune/qsearch_prune survives full T1 fields, do not execute any SEE flip and record mechanical non-identification. Do not replace with old 0.22 D2 rootcall-first surrogate.
