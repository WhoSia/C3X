# C3X 0.23-P1-R2-T1 — Search-State–Exact SEE Activation & Native TT Causal-Chain Identification

**Design freeze 2026-10-11; no T1 SEE actuator or T1 new heldout forecasts run.**

## Research finding that motivates a stronger identification gate

P1-R1 independently selected 32 licensed roots, 124/124 actually blocked first native TT reader targets, 2508 unique SEE matches on original chess path signature, 7/124 final UCI flips over four broadcast games, M1 111/124 accuracy versus M0 117/124. R1 match is a *search-path correspondence*, not a causal mediator.

P1-R2-T0 six deliberately post-hoc developmental cases show **21 unique common SEE events after original actual watched TT score use and after counterfactual physical TT block**, in four of six cases. **May game #2 control has 14 post-TT common SEE events yet no terminal bestmove flip**. Two cases (May #8 and #3) were censored and cannot be declared no-common-event. Source log-order was synchronized in single-thread native engine. [T0 receipt](../receipts/c3x-023-P1-R2-T0-chronological-native-TT-to-SEE-common-source-after-use-20261011.json).

## Exact computational SEE state definition

An event is eligible to be called **same computational node**, not merely same chess board and root, only with:

`(original root source, root candidate native move, original ancestry key-sequence, current full64 position key, chess rule50, native move, SEE site, threshold, optional occupied bitboard, source ply, source depth, alpha, beta, PV/nonPV, original SEE Boolean, unique source occurrence, TT origin and monotonic original event ordinal)`.

A 64-bit ancestry hash collision remains possible and should be augmented by exact ancestor key-vector bytes for positive certification, privacy/licensing reviewed. `position key` may omit search-level state; alpha/beta, qsearch versus search, and occupied bitboard must not be inferred from FEN alone. Compare original and TT-suppressed paths **after actual scored TT use/block**. Preserve PRE_TT, PATH_DIVERGED, SEARCH_WINDOW_DIFFERENT, OCCUPIED_DIFFERENT, MULTIPLE_OR_CENSORED statuses separately.

## What constitutes a possible mediator

For identical native `Position::see_ge` inputs, returned Boolean is deterministic. Therefore the **natural** TT-mediated pathway cannot be “TT changes the SEE output at an identical SEE invocation”. The relevant mechanism is alteration in SEE **call activation**, threshold, move/occupancy, pruning consumption, or which node is visited. Counterfactual Boolean flipping `do(SEE_return = ! original)` is a *controlled source intervention* on an operator, NOT the natural mediator under preserved arguments.

Strongest next falsifiable design:
1. Source-identity matched original/native TT first observer with actual score-use and cutoff labelled separately. Record native event serial and complete SEE source state (ply, depth, alpha/beta, PV, threshold, occupied). Require stable cold replicates.
2. Determine whether TT suppressing selected first physical reader changes SEE **activation/threshold/branch choice** after the original source, including cases with no final UCI flip. This is a test of necessity/response-contingent affordance transmission, not universal chess motif labels.
3. If **an exact computational node is visited in both arms**, preregister targeted *single* SEE source site, exact matching arguments and occurrence ordinal; run sham, TT-only, SEE-only and joint source operator control with no changes to chess legality or other SEE calls. If the identical source arguments yield a different observed original Boolean, stop for instrumentation fault investigation.
4. If TT changes the entire branch and no exact node survives, analyze event noncontact/activation as the mediator candidate. Do NOT relabel the first different node under the same rootcall as an aligned counterfactual.
5. Re-evaluate terminal root-leader divergence depths and actual search return/cutoffs, preserve per-game clustering and exact move forecasts. On these May and CC0 roots only *exploratory mechanisms* can now be developed after results viewed; a genuinely prospective M3 requires completely new eligible source stratum and git-committed per-move literal UCI before new native TT treatment.

## Mandatory negative and stop controls

- No TT physical source block → `HOLD`; no SEE real source contact → `NO_CONTACT`; censored source SEE prefix → `HOLD_CENSORED`; source position same but search state differs → `SAME_BOARD_DIFFERENT_SEARCH_STATE`.
- A common SEE source event *before* TT original score use or TT counterfactual block cannot mediate selected TT first-reader intervention.
- Compiled Stockfish GPLv3 source patch chain fully reproducible; user has separately sent TWIC rights inquiry through an outside account; this T1 development does not read/send email and uses only Lichess CC BY-SA broadcast or CC0 puzzle sources.
- The 14 positive chronology matches of May #2 with zero final UCI flip refute the sufficiency of “a post-TT common SEE event” alone.

**T1 current status: CONTRACT_FROZEN; SEARCH-STATE MEASUREMENT NOT YET PERFORMED.** No false mediation or M3 positive predictor is declared.
