# C3X 0.7.0-G9.5-P7 — Prospective Target-Blind Prefix-Graph Causal-State Construction

## Program identity

C3X is a chess-engine research program. P7 therefore treats causal-state methodology as infrastructure for a chess question:

> Can the observable search history of a chess engine be quotiented into reusable, engine-crossing search states that determine whether suppressing a specific TT semantic-use event changes the engine's chosen root move?

The object of study is not an abstract time series. It is a **Chess Search Episode Graph (CSEG)** built from an actual chess position and the engine's baseline search prefix.

## Data is not the bottleneck

PGN volume is not the scarce resource. Human and engine-testing chess distributions are abundant. The scarce resource is **intervention-labelled engine search behavior**.

P7 therefore separates:

1. **world supply** — PGN/EPD/legal-position sources that provide chess positions;
2. **search materialization** — Stockfish/Berserk/Ethereal produce baseline search prefixes;
3. **causal labeling** — exact-event removal replay produces ROOT_CHANGE / NO_ROOT_CHANGE.

No large learned model is required.

## Chess-world axes

P7 prospectively mixes five source roles.

- **PGN sequence lane** — preserves move-history-derived chess positions.
- **human-popular lane** — Lichess-derived popular positions.
- **engine-test lane** — UHO / 8mvs style positions used in engine testing.
- **endgame / pathological lane** — stalemate/endgame-oriented positions.
- **pioneer lane** — deterministically generated legal positions, included as a sparse frontier rather than as a replacement for natural chess.

The pioneer lane is deliberately small. It tests whether the state construction survives outside curated corpora without letting synthetic chess dominate the estimand.

## Target-blind state construction

P7 removes the P1-P6 `fiber_id` anchor from representation construction.

A P7 profile is built from **baseline information only**:

- root FEN;
- baseline parent trace up to and including the sampled event;
- the sampled event's target-blind identity;
- deterministic chess-position atoms.

Counterfactual traces, ROOT_CHANGE labels, P5/P6 target labels, and P6 near-miss diagnostics are unavailable to the state constructor.

## Chess Search Episode Graph (CSEG)

### Nodes

1. one **ROOT_POSITION** node;
2. one node for each baseline TT semantic-use event in the observed prefix.

### Root-position label

The root node records bounded chess semantics:

- side to move;
- in-check status;
- game phase from material;
- legal-move-count bucket;
- material-balance bucket;
- castling-rights class;
- halfmove-clock bucket.

These are chess-state descriptors, not causal labels.

### Event-node label

Each event node records engine-search semantics already present in C3X instrumentation:

- search scope;
- semantic-use class;
- ply bucket;
- depth bucket;
- TT bound;
- alpha/beta/window relation;
- TT-move presence;
- payload bucket;
- CURRENT_EVENT marker.

Raw TT keys are never emitted.

### Typed edges

- `NEXT`: temporal adjacency;
- `STACK_PARENT`: nearest preceding event at parent ply;
- `SAME_KEY_PREV`: previous use of the same TT key;
- `SAME_CLASS_PREV`: previous semantic-use event of the same class;
- `SAME_SCOPE_PREV`: previous event in the same search scope;
- `ROOT_EVENT`: root-position anchor to every event;
- `ROOT_CURRENT`: root-position anchor to the intervention event.

TT-key equality may create an edge; key identity itself is not part of the public graph.

## Frozen structural quotient ladder

P7 uses edge-labelled Weisfeiler-Lehman-style refinement only as a finite canonical state constructor.

- **Q0** — initial node labels + typed-edge census.
- **Q1** — one round of typed in/out neighbourhood refinement.
- **Q2** — two rounds.
- **Q3** — three rounds.

For each level, the state ID is a canonical digest of:

- root-node colour;
- current-event colour;
- multiset of node colours;
- multiset of typed coloured edges.

The ladder is frozen before outcomes. No new edge type, board atom, refinement rule or extra round may be introduced after P7 targets are opened.

## Why this is more chess-native than P6

P6 manually enumerated local features. P7 asks whether the **search episode itself** has a reusable structural state.

A state may therefore distinguish two otherwise similar TT events because they occupy different locations in:

- the alpha-beta search stack;
- TT recurrence topology;
- semantic-use sequence;
- chess-position context.

That is a chess-engine hypothesis, not a generic graph-learning objective.

## Fresh role sequestration

P7 uses disjoint fresh worlds after excluding every recoverable P1-P6 candidate hash.

- **STRUCTURAL_TRAIN**
- **STRUCTURAL_SELECTION**
- **UNTOUCHED_TRANSPORT**

The graph states for all three roles are computed before their role's targets are opened.

P6 labels and the two seven-collision P6 near-miss representations are development-only motivation and receive zero P7 confirmatory vote.

## Train court

For each Q-level:

1. compute target-blind state IDs first;
2. open only STRUCTURAL_TRAIN targets;
3. test whether each reused state is label-consistent;
4. require compression, cross-position reuse, cross-engine reuse and positive-state reuse.

The first prospectively ordered Q-level passing every train gate is frozen.

If Q0-Q3 all retain opposite-label state collisions, P7 closes `PREFIX_GRAPH_STATE_FAMILY_HOLD`. No Q4 may be invented.

## Fresh selection

The frozen Q-level and train state→label map query STRUCTURAL_SELECTION profiles before selection targets open.

Selection has its own independent positive-support gate. No refit or state splitting is allowed.

## Untouched transport

Only a selection-passing state map may query UNTOUCHED_TRANSPORT profiles. Transport targets open only after target-blind coverage gates pass.

## Chess phenotype lane

ROOT_CHANGE remains the authority target, but every positive counterfactual also receives a deterministic downstream chess phenotype:

- baseline root move;
- counterfactual root move;
- moved piece type;
- capture / check / promotion flags;
- legal PV prefix divergence;
- score/WDL direction when available.

These phenotypes improve chess explanation. They cannot expand field authority.

## Implementation roles

- **C/C++** — existing engine-native TT/search instrumentation and exact-event intervention.
- **Python** — PGN/EPD world materialization, UCI orchestration, board-state and root-move phenotype extraction.
- **Rust** — canonical CSEG construction/refinement and state-map court kernel.
- **Go** — independent graph-state digest verifier to detect implementation-specific canonicalization drift.
- **JavaScript** — final authority/explanation verifier.
- **Policy** — capability-first polyglot; language choice has no scientific authority.

## Claim ceiling

A P7 PASS would establish a bounded chess-search state quotient that survived fresh train, selection and untouched cross-engine transport under the exact P7 intervention regime.

It would not prove uniqueness, universal engine invariance, human cognitive validity, or that WL refinement is a general theory of chess search.
