# C3X 0.18 — Search-State Locality, TT Reader Event Rank & Implementation-Relative Mediation

**Status: ACTIVE / controlled source counterfactuals PASS, broad natural mediation HOLD.** Do not paper-freeze. This is a **research ontology update**, not a theorem that the engine possesses a chess concept.

## Primitive relations

For an engine source version `v`, position source history `h`, intervention `I` and fixed cold UCI contract `c`, distinguish:

1. **Physical value transport** `W→R`: a writer ticket with full 64-bit position key, TT physical slot, slot epoch and nonzero local serial is earlier than an actual TT consumer, whose raw entry `(value, eval, bound, depth, move)` equals the writer snapshot.
2. **Source eligibility** `E(I)`: the intervention's exact guard condition was reached with the expected value and key. An inactive/nonfiring intervention is not negative causal evidence.
3. **Local causal effect** `Δm_e(I)`: the return or state of a designated source search event `e` changes when `I` is applied, with exact root-call, candidate, ply and key matching *before* path divergence.
4. **Root categorical effect** `ΔY(I)`: the final UCI root bestmove changes.
5. **Reported search effect** `ΔU(I)`: any component of the six-field UCI core (bestmove, score kind/value/flag, nodes, PV) changes.
6. **Transport scope** `T(I,v,h,d)`: exact engine family/source role, position history and search depth are part of the causal intervention, not optional descriptive metadata.

**Observed counterexample to a naive inference:** a local source return difference **does not imply** a changed final root choice or final UCI core. One source-level branch can be locally necessary for a leaf return but globally screened off by root competition, search windows or later path compensation.

## Original game #1: positive, targeted, then blocked at exact source node

From independent October broadcast source (original history preserved), at depth1/root_call1/candidate native 2313, FEN6 without move stack returns child score **+68**. Actual historical game state returns **+1 in O**, **−1 in F**. The actual game state has a true `pos.has_game_cycle(ply=1)` with full64 position key **1393645049232160636**, rule50 16, `pos.has_repeated()==true`.

A subsequent **adaptive** micro-court (not a prospective independent test) blocked only that true `has_game_cycle` return, matching key64/rootcall/rootmove/ply. G mode had **one actual contact** and restored child return **+68** in both O and F. An immediate-draw-only D mode had **zero contacts**, leaving +1/−1; impossible-contact FEN6 arms were unchanged. However **the entire final UCI core did not change when G restored the local child score**.

Therefore the positive cycle branch is the witnessed **local source of the initial recorded child-score divergence**, **not** an identified explanation for all downstream node/PV differences. The distinction survives fully cold, source-matched, negative-control native execution. [Native G/D/GD receipt](../receipts/c3x-018-case1-cycle-root-call-targeted-native-20261010.json).

## Independent November twelve game histories: rank is not a proxy for cause

Selection source-only [workflow #37985213908](https://github.com/WhoSia/C3X/actions/runs/37985213908), source SHA `2971fe617f39fbba6d40fb0b09d8a18ce247d5865dc807fcdab9a594e3473402`. Prospective [pre-outcome reader-rank protocol](c3x-018-independent-nov2025-depth8-12-TT-reader-rank-preregistration.md), frozen ranks zero-index `0,7,23`; 12 new game histories, source-original six-field FEN clocks, depth8 and depth12. All **72 treatments actually fired and all claimed last-writer raw payload values matched**, no eligible ranks or cases silently omitted.

| TT V reader | Depth8 changed bestmove | Depth12 changed bestmove |
|---|---:|---:|
| First (index0) | 0/12 | 0/12 |
| Eighth (index7) | 1/12 | 0/12 |
| Twenty-fourth (index23) | 1/12 | 1/12 |

Case4's 24th-source-read intervention changes root bestmove at both depths, case6's 8th only at depth8. Prospective T1–T6 **all PASS**, but **rank is simply arrival order in a trace, not recursive ply, counterfactual distance or causal necessity**. Original October first-eligible V impact P1 failed 0/16 and **remains failed**; the November evidence cannot retroactively rescue it. [Full new-source source-native receipt](../receipts/c3x-018-nov2025-reader-rank-8-12-preregistered-native-20261010.json).

## Two Stockfish versions, then independently implemented Ethereal

Stockfish16 classical source vs Stockfish17 NNUE source use source roles both described as *TT score/bound improves position evaluation*. This is the **same semantic branch role**, not matched tree calls or matched TT entry layouts. A **global** two-site suppression (not a single targeted V reader) changed bestmove in **22/48** new-game×depth×version paired cells and created **10/24** source-game×depth binary-response disagreements between Stockfish versions. All source compile, cold runs and exact provenance passed. [Cross-version receipt](../receipts/c3x-018-sf16-sf17-bound-evaluation-transfer-20261010.json).

Independent **Ethereal** source does not contain an identical `ttValue`-as-better-static-eval source role. Instead it uses **cached static TT eval `ttEval`** at both main and quiescence searches. A separate global cache-bypass intervention physically reached a TT cached-eval consumer in every one of **24/24** new-game×depth cells; **0/24** changed bestmove, while 2/24 changed only nodes by 12 and 5 respectively. Prospective I3 **FAIL**, I1/I2/I4/I5 **PASS**. This is a **non-isomorphic role**, not a replication attempt of Stockfish V. [Independent-engine receipt](../receipts/c3x-018-ethereal-independent-TT-cache-evaluation-native-20261010.json).

## Remaining attacks

- **Search-history residual beyond one draw cycle:** case1 shows local repeat predicate drives the first child return, but the FEN6 vs actual original history final full core still differs. Need actual full search-tree stopping/alpha-pruning and repetition-state audit, not just one positive repetition witness.
- **Mechanistically defined reader selection:** infer source roles such as depth, write age, bound orientation, root candidate and trial *before* looking at treatment outcomes. Use a **third separate future-month** pre-outcome cohort to avoid mining November event index 24, and preserve all failed predictions.
- **Independent engine structural abstraction:** define a typed source role (stored TT **search value**, cached static **eval**, move hint, direct cutoff, replacement, path dependence) rather than forcing all engines' TT uses into Stockfish V.
- **Original game clock and history:** the October sixteen's categorical FEN/history differences were reproduced by authentic halfmove clocks, but case1's full search core residual requires search-state causal work; fullmove-only perturbations had no reported effects in that finite sample.

**Hard HOLD:** exclusive natural physical writer→reader→root mediation; general chess motif understanding; algorithm-independent invariant; statistical transfer beyond two Lichess months and these engine builds.
