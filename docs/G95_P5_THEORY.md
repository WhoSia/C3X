# C3X 0.7.0-G9.5-P5 — Outcome-Sequestered Causal Representation Discovery

## Why P5 exists

P4 solved the support problem without solving the representation problem. Fresh outcome-blind sampling produced 26 ROOT_CHANGE positives in 576 exact-event interventions across Stockfish 19, Berserk and Ethereal, but every P3-frozen context family still mixed opposite target labels.

P5 therefore changes the scientific object. It does not ask which hand-written context coordinate should be added. It asks whether a **bounded representation-discovery procedure** can learn a compact partition that is sufficient for the exact-event target, survive an independent schema-selection split without refitting, and then transport to untouched worlds.

## Temporal repair before representation learning

The P3/P4 topology extension itself was prefix-safe, but several inherited base coordinates were computed from the full parent search trace or terminal parent semantic summary. Those coordinates were target-blind, yet they were not strictly available at the candidate event.

P5 replaces the context surface with `c3x-context-v3`. Every candidate atom must be computable from:

- the board position before search;
- the candidate event;
- parent-trace events at or before that event;
- a frozen engine architecture descriptor kept outside the primary representation.

No future parent event, final parent depth/score/PV, raw engine identity, or counterfactual target may enter the primary grammar.

This repair does not alter P4's closure: P4 produced no certified field.

## Nested outcome sequestration

P5 uses three fresh, disjoint target roles.

1. **Representation train.** Targets are opened here to generate a shortlist from a frozen grammar.
2. **Schema selection.** Candidate representations are evaluated exactly as trained. No cell relabeling, coordinate addition, threshold change or refitting is allowed.
3. **Untouched transport.** Profiles are scoped first. Transport targets remain unopened unless one representation has already passed schema selection.

A representation that fails selection never reaches transport target opening.

## Frozen coordinate grammar

The primary field always includes the existing F0 `fiber_id` anchor. The learner may add at most four coordinates chosen from a frozen set of strict-prefix categorical atoms covering board state, event semantics, prefix counts, recurrence topology and local depth transitions.

The grammar explicitly excludes engine identity, architecture identity and sampling-stratum identity. Those variables may be audited diagnostically but cannot rescue the primary global representation.

The train search is exhaustive over all coordinate subsets of size 1–4.

## Minimal sufficiency and complexity

For coordinates C, records are partitioned by

```
cell(r; C) = fiber_id(r) × Π_{c in C} c(r).
```

A train candidate is admissible only when:

- every train cell is target-homogeneous;
- both target labels occur;
- compression is at least 0.15;
- enough records participate in cross-position and cross-engine cells.

Among admissible candidates, P5 records a two-part MDL proxy

```
L(C) = 8 |C| + number_of_distinct_train_cells.
```

The train shortlist is ranked by minimum L, then fewer coordinates, higher compression and lexical coordinate tuple. The exact constants are frozen before target opening; they are regularizers, not post-outcome significance thresholds.

## Selection without refitting

Every shortlisted train field is queried on schema-selection profiles. The field's train labels remain immutable.

A candidate may pass selection only with:

- zero covered contradictions;
- zero mixed observed labels inside a covered frozen cell;
- at least 20% global coverage;
- coverage on all three engines;
- at least 10% coverage inside each engine;
- at least four positions and two source regimes covered;
- at least one covered ROOT_CHANGE.

The selected representation is the passing candidate with minimum train MDL, then highest selection coverage, fewer coordinates and lexical id.

## Untouched transport

The frozen selected field is queried on transport profiles before target artifacts are downloaded. Scope requires at least 20% coverage, all three engines, four positions, two regimes and at least one predicted positive profile.

Only then may transport targets be opened. Public certification requires exact agreement for every covered profile and no mixed covered cell.

## Literature relation

P5 borrows three ideas without claiming equivalence to their formal settings:

- causal-state/minimal-sufficiency work motivates representing histories by the coarsest predictive equivalence that preserves the target;
- invariant prediction motivates requiring a representation/conditional law to survive environment changes rather than trusting in-sample fit;
- causal abstraction motivates separating a compact high-level representation from the lower-level intervention system and testing faithfulness under interventions.

Recent causal-representation work also shows why invariance alone is insufficient for identification. P5 therefore requires invariance jointly with collision freedom, complexity control, cross-position/cross-engine reuse and a final untouched transport court.

## Claim ceiling

A P5 PASS would establish a bounded, prospectively selected, cross-engine transportable representation for exact-event ROOT_CHANGE under this engine/replay regime. It would not establish that the coordinates are unique causal variables, that the same law holds in every engine, or that the representation describes human chess cognition.
