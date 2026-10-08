# C3X 0.14 — Transportable Search-Mechanism Evidence, Chess-Concept Mediation & Faithful Explanation Systems

**Status: FORMALLY OPEN — 2026-10-09.** Initiated after C3X 0.13 P8-EP11's scoped handoff. Scientific mechanism **OPEN/HOLD**, not a win declaration. This is the single active C3X research phase, not an additional Notion Lab per experiment.

## Why change phase
C3X 0.13 demonstrated actual UCI/C++ intervention and engine evidence to source-bounded PGN commentary, culminating in the reproducible Stockfish16 17.f4 Qc7 TT lower-bound cutoff event with complete position FEN and native 64-bit position Zobrist lookup key. The previous endpoint met *local source instrumentation and event-path attribution*. It did not meet independent-source transport, human chess-concept mediation or verified explanatory utility. Stretching 0.13 further to solve all three would mix discovery context with validation scope and invite post hoc selection. The open questions move forward with no retroactive promotion of failed P8 criteria.

## Four coordinated research axes

### A. Stable source-native mechanism extraction and nontrivial equivalence
Keep source version, engine binary hash, UCI options, thread scheduling, NNUE, software licenses and GPU/CPU specification in a signed reproducible event context. Distinguish 64-bit *lookup-board* Zobrist key from the 16-bit *stored TT-entry* discriminator; both fail to encode full repetition history. Collect full six-field FEN and search-stack path, native entry bound/depth, window alpha/beta, move ordered versus searched, TT hit versus bound cutoff, history/LMR and qsearch divergence. Hypothesis: a context-indexed family of structural search events predicts candidate-pair preference sensitivity better than mere prior move ordering or depth alone. Negative controls include legally matched null event, unreachable key, choice-order swap, hash size change, fixed node/elapsed budget, original NNUE and clean sham.

### B. Genuine prospective source-disjoint transport, and independent engine implementations
Before obtaining outcome labels, define source and game groups, legal root pair orientation, depth/nodes ranges and ranking thresholds. Neither two arms of the same chess game nor two cold reruns are independent games. Do not transfer an absolute TT key across positions or versions; test transport of **event-type predicates** and signed comparative root scores under a shared legal chess concept contract. Stockfish and Ethereal source-native measures are not interchangeable by cp unit; ensure chess legality, provenance, SAN, clock and rule50. At minimum require source-disjoint games; preferably independent provider/authorities (not only distinct Lichess events), plus a materially different chess engine implementation.

### C. Board-concept mediator discrimination
Specify at least two competing *chess-native* explanations in each candidate set: material/tactics, passed-pawn generation, king safety, piece coordination, tempo/candidate reply, etc. Freeze perturbations that preserve legal chess, opponent reply availability and relevant tactical danger. Define exposures E (chess structure), search mediator M (measured event), output Y (root pair preference), and rival paths R (move order, TT hit, LMR/history, NNUE score, opposing free tactical reply). A conditional TT-bound event may cause a finite engine output change without the chess concept being its cause. Need both context-specific perturbation and mediation witness; compare preservation-of-semantics with the Clark et al. (2023) causal-graph metamorphic test framework without claiming their graph is verified for Stockfish. No use of conceptual symmetry transforms that break pawn color or repetition invariants.

### D. Verifiable explanation software and reader-outcome evaluation
Build evidence ledger: `source -> node/line -> engine version -> intervention -> uncertainty -> human language`. A generated sentence can state only the certified granularity. Uncertified engine event statements remain `CONVENTIONAL_HEURISTIC_COMMENTARY`, not `C3X_CAUSAL_CONTRAST`. Tests: a source-byte tamper, wrong FEN, wrong score sign, mate/cp mismatch, multiple-source dependence, skipped detector, fabricated user-facing chess causation, inaccessible artifact. Measure human comprehension on a blinded before/after chess benchmark, including novice vs advanced segments, and an objective answer key that cannot merely reward agreement with engine cp. Human subjects/ethics review as appropriate.

## Baselines and novelty gate
- Méndez et al. (2023), *Metamorphic Testing of Chess Engines*, IST162 107263, original open-source 40k+-position metamorphic tests: http://doi.org/10.1016/j.infsof.2023.107263.
- Martin, Khelladi, Matricon & Acher (2025), *Re-evaluating Metamorphic Testing of Chess Engines*, IST181 107679: real-game search-depth/version sensitivity, source-native move-order explanation. Existing 10_PAPERS.
- Clark, Foster, Walkinshaw & Hierons (2023), *Metamorphic Testing with Causal Graphs*, ICST 153–164, DOI 10.1109/ICST57152.2023.00023: model-driven causal-graph metamorphic test generation; not direct proof of our hypotheses.
- Zhang & Nanda (2024), activation-patching metrics and intervention design sensitivity; Geiger et al. (2025), causal abstraction mathematical framework. Methodological analogues, not identical software components.
- Existing C3X G9.4 and G9.5 P13–P15 already include event-provenance and local pair flipping. No assertion that C3X 0.14 invented event-level TT intervention. A publishable novelty candidate is rigorous *transportable chess-structure-to-search-event-to-explanation* discrimination, including negative results and a real verified product.

## First active stage
**C3X 0.14 P1 — Prospective Source-Disjoint Search-Event Transport and Explanation-Boundary Court.**
Produce a frozen sampling and segmentation contract, independent candidate selection and strict source-root units, with a separate untouched heldout group. Freeze positive and negative predictions before running any outcome-specific local interventions. No trial may be counted as heldout if selected using P8 score/cutoff outcomes. Execute source-native telemetry and product integration on the same versioned evidence ledger. A pure Notion/protocol-only step does NOT count as P1 empirical PASS.

## Exit and failure
C3X 0.14 can be CLOSED as `SUPPORTED`, `PARTIAL`, or `FAILURE/HOLD` with explicit supported subclaims. No scoring overrides, no artificial positive results, no mechanistic or human strategy certificate without independent evidence. A good negative falsifier is publishable evidence when prior claim is honestly narrowed.

## Research OS / source custody
Use existing C3X Notion Lab root and continuous GitHub README; avoid P1, P2, etc. registering as duplicate independent Labs. Google Drive 00_INTAKE to 10_PAPERS canonical original PDF with duplicate/DOI audit; store experiment ZIP in existing C3X raw folder. Authenticated WhoSia human commits only. GitHub Actions: contents:read, no Actions-authored writes or contributor changes. No use of friends' servers unless explicitly reauthorized. Polyglot selectively: Stockfish/Ethereal native C++, Python-chess legality, Rust typed/provenance checks when correctness distinctly merits it, UI/TS only when actually exposing explanation product.

**Inheritance:** [C3X 0.13 EP11 handoff](../receipts/c3x-013-p8ep11-native-tt-fen-key-legal-ancestry-scoped-handoff-20261009.json). Do not relabel earlier experimental `C3X_014: UNOPENED` fields; those describe the time the older experiment was frozen.
