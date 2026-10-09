# C3X 0.15 — CSWP v0.6
## Choice–Value–Compute Fibers and Causal Contact Without Result Equivalence

**Status (2026-10-09): Proposed falsifiable research framework; not an established general chess theorem.** 0.15 OPEN, 0.16 NOT OPEN. Source interventions verified only on two outcome-exposed TWIC worlds (#2 and #29). Preserve failed prospective C1 accuracy 42/64 vs trivial B0 53/64.

### 1. New empirical discrepancy

The source-native P9-A1/A2 experiment factorizes a single P6S0-frozen physical TT return and its qsearch successor into distinct interventions:
- G: suppress one exact beta-break at CEFH #2, no contact at RISR #29.
- W: suppress exactly one target qsearch TT save.
- L: run qsearch completely, then force its return scalar to the original stored TT value.
- D129/D130/D131: at RISR #29's single original first child (native Move729, return -59, alpha130/beta131), substitute respectively 129, 130 or 131, without modifying chess legality. For CEFH #2 these are noncontact controls.

P9-A1 actual 48 native cold searches: G/W/L each source-exposed at their target except noncontact G in #29. Yet no G, W or L intervention changed the categorical root move compared with B. At RISR #29, W and L also preserved node count exactly under both SEE arms. No unique natural TT mediator has been isolated.

P9-A2 actual 24 native cold searches: in RISR world #29, all D129/D130/D131 have the SAME final root move f3e5 in both SEE conditions, despite:
- D129/D130: final engine cp +4, nodes OFF 50,516 and SEE-ON 60,899; first PV depth deviation 4.
- D131: final cp +22, nodes OFF 77,115 and SEE-ON 77,115; first PV depth deviation 5.
- P9-A2 CEFH #2 has zero contact for all six D-arm/SEE combinations, reproduces prior B moves, reported scores and nodes exactly.

### 2. Typed computational decision fiber

For a locked game history H, board P, source/build environment theta, operator-contact policy a and source SEE treatment s, define the observed (NOT necessarily structurally causal-complete) **choice–value–compute fiber**:

\[
\Xi(P,H,\theta;s,a)=
\big(Y_{s,a},\ V_{s,a},\ N_{s,a},\ D_{s,a},\ E_{s,a},\ W_{s,a}\big).
\]

Where:
- Y = final categorical root bestmove UCI (do not numerically average).
- V = completed-depth reported root score (cp/mate/bound tag, not game-theoretic truth).
- N = count of actual visited nodes (search cost), not wall-clock time.
- D = first reported completed iterative depth where root PV first move differs from the reference arm, or null.
- E = actual exact source-operator exposure and event trace (including P8 truncation).
- W = TT writer/reader/bound/alpha-beta window event provenance, possibly only partially observed.

The projection onto Y is non-injective for the actual RISR P9-A2 cases:
\[
Y_{129}=Y_{130}=Y_{131}=f3e5,\quad
V_{129}=V_{130}=4,\quad V_{131}=22,
\]
\[
(N_{\mathrm{OFF},129},N_{\mathrm{OFF},131})=(50{,}516,77{,}115).
\]
The difference in evaluation and node count under an artificial source intervention is **actual executable evidence**, not a new abstract mathematical theorem. The inference is limited to this engine version, policy, and selected original source world.

### 3. Mechanism terms must be distinguished

A **choice-invariant regime** is an experimentally specified set A for which Y(s,a)=constant at fixed world and policy; this says nothing about V, N or W. **Value-invariant** and **work-invariant** regimes are separate equalities. A search *mechanism* claim additionally needs a preselected event-specific intervention, no-fire sham, cold replay and an independently checked causal contrast.

The #29 source case is therefore better described by three separate observed properties:
1. Return-invariant source recomputation (P8/P9-B: local target TT value29 and recomputed qsearch value29).
2. Root choice-sensitive early-return bypass (P7/P9-A1 I vs B in SEE OFF).
3. Root choice-invariant but value/work-sensitive first-child qsearch threshold crossing (P9-A2 D129/130 versus D131).

These are three layers of the SAME historical game state, not three independent original game samples.

### 4. Prospective hypothesis requiring NEW data

Candidate H-CVC: the typed tuple \(\Xi\) and its motif/operator contacts can predict *which* outcome dimension will be sensitive (choice, score, nodes, first PV switch), conditioned on actual legal geometry and source context, more reliably than source contact frequency, binary SEE flip, TT bound alone or null never-change baselines, on source-disjoint held-out PGNs or STS-like strategically annotated positions.

Precommit before evaluating new games:
- Mechanism candidates: pins, skewers, interference, deflection, clearance, discovered attacks, zwischenzug; plus king safety/activity, pawn center/advancement, simplification, outposts and open files/diagonals.
- Legal geometry requires chess-law verification, tactical motifs require actual legal move sequences, strategic claims require plan/horizon stability and alternatives; labels alone are not proofs.
- Same 4-field FEN must not occur in both train/test even when STS section labels differ. STS source inspection: 1500 rows, 15 section numbers, 1497 unique four-field FEN, three cross-category duplicates; one of 15 sections has two literal word-order aliases. Source-only semantics, NOT checkmate solution or chess truth.
- Independently compare categorical choice prediction, numeric score calibration and computational work prediction using heldout data. Do not salvage an overall prediction accuracy failure using post hoc success on a minority class.
- Probe alternate depths, TT hash and evaluator regimes, plus a genuinely disjoint engine family. Failure to replicate falsifies generality, rather than being hidden by removing difficult categories.

### 5. Explanation-authority ceiling

ALLOW at current P9 level:
- An original SF16 software micro-intervention at frozen event changed reported value/nodes/PV while root move stayed stable (#29).
- A single TT shortcut can change root selection without changing the recomputed qsearch scalar (#29 P7/P8).
- One beta break, one target qsearch TT save, and one scalar-relay clamp each were insufficient to change final root bestmove under P9-A1, as tested (including exact no-contact controls).

ABSTAIN:
- Identifying which natural mediator or learned network feature caused the root choice.
- Claiming the engine "understood" skewers or a universal strategic concept.
- Treating the +4/+22 scores as certified optimal minimax values.
- Claiming independent source generalization from repeated outcomes of two P6-selected games.
- Treating cross-label duplicates in STS as independent validation trials.

This framework combines source-level program execution, search-window provenance, categorical potential outcomes and chess concept annotations under explicit abstention. Classical alpha-beta, quiescence, program debugging, potential outcomes and strategic test suites predate it; P9 does not claim invention of those fundamentals.

### 6. Immutable source evidence
- [P9-A1 SF16 48 native SUCCESS](https://github.com/WhoSia/C3X/actions/runs/37926784308)
- [P9-A1 actual source result receipt](https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-015-P9-A1-48native-CEFH-RISR-exact-event-causal-court-20261009.json)
- [P9-A2 SF16 24 native SUCCESS](https://github.com/WhoSia/C3X/actions/runs/37930348481)
- [P9-A2 actual source result receipt](https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-015-P9-A2-RISR-qsearch-score-boundary-24native-20261009.json)
- [STS source-only duplicate audit](https://github.com/WhoSia/C3X/blob/main/c3x/receipts/c3x-015-P9-STS-1500-1497-three-cross-category-duplicate-FEN-audit-20261009.json)
- The licensed original TWIC raw PGN is held privately on the C3X Drive, not redistributed on public GitHub.

**Court:** P9_A1_SOURCE_NATIVE_48_PASS / P9_A2_SOURCE_NATIVE_24_PASS / CVC_DIMENSIONAL_NON_EQUIVALENCE_DEMONSTRATED / FULL_TT_CAUSAL_MEDIATION_HOLD / MOTIF_AND_STRATEGY_TRANSFER_UNTESTED / C3X0.15_OPEN_NO_0.16.
