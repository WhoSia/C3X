# C3X Explanation Implementation Track — PGN → Evidence-Aware Commentary

## Status

This is **Track B: implementation**, not the C3X scientific novelty mainline.

The end product should accept a PGN and produce useful move-by-move or selectively triggered chess commentary. It may borrow established methods aggressively. Its engineering success does not promote a Track A scientific claim.

## Product contract

Input:
- PGN, optionally player level / commentary mode.

Output:
- selected moments worth commenting on;
- candidate alternatives and engine context;
- tactical and positional observations;
- contrastive explanation where supported;
- natural-language commentary;
- machine-readable provenance and confidence for every substantive explanation unit.

Two provenance classes are mandatory:

- `C3X_CAUSAL_CONTRAST` — backed by a specific C3X intervention certificate.
- `CONVENTIONAL_HEURISTIC_COMMENTARY` — useful standard chess explanation without a C3X causal certificate.

The UI may weave both into readable prose, but the underlying authority boundary must remain inspectable.

## Architecture

```text
PGN
 ↓
legal replay / position segmentation
 ↓
comment-worthy moment selector
 ↓
candidate-set + MultiPV analysis
 ↓
evidence router ───────────────────────────────┐
 │                                             │
 ├─ C3X certificate lookup / live causal probe │
 ├─ tactical motif and line verifier           │
 ├─ positional/concept analyzers               │
 ├─ retrieval from annotated commentary        │
 └─ conventional engine evidence               │
                                               ↓
                                  structured explanation graph
                                               ↓
                                  language realization / LLM
                                               ↓
                          legality + factuality + provenance firewall
                                               ↓
                               PGN commentary / interactive review
```

## Donor literature and engineering

### Move-commentary corpora and salience

Jhamtani et al., ACL 2018, **Learning to Generate Move-by-Move Commentary for Chess Games from Large-Scale Social Forum Data**:
- large move/commentary corpus;
- commentary aspect selection and pragmatic context;
- useful donor for data schema, salience, style diversity, and evaluation.
- https://aclanthology.org/P18-1154/

### Engine-grounded generation

Zang, Yu & Wan, ACL 2019, **Automated Chess Commentator Powered by Neural Chess Engine**:
- conditions generation on chess-engine representations;
- separates commentary categories such as description, comparison, and planning;
- useful donor for category routing and engine-grounded language generation.
- https://aclanthology.org/P19-1597/

### Concept-guided modern commentary

Kim et al., NAACL 2025, **Bridging the Gap between Expert and Language Models: Concept-guided Chess Commentary Generation and Evaluation**:
- explicit expert-model/LLM bridge;
- concept-guided generation plus dedicated commentary evaluation;
- useful donor for Track B concept adapters and evaluation.
- https://aclanthology.org/2025.naacl-long.481/

### Position-attribution XAI

Spinnato, 2025, **Towards Piece-by-Piece Explanations for Chess Positions with SHAP**:
- piece-level perturbation/attribution;
- useful as a heuristic explanation donor and rival baseline;
- must not be silently promoted to the stronger causal authority of C3X search-event certificates.
- https://arxiv.org/abs/2510.25775

### Faithfulness warning

Parfenova, 2026, **Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness**:
- fluent, coherent chess explanations need not reveal the cause of the decision;
- directly motivates the C3X authority firewall between useful narration and causal evidence.
- https://arxiv.org/abs/2609.22245

### Practical donor

ChessCoach demonstrates an end-to-end engineering lineage with PGN processing, chess play and natural-language commentary. It is a practical donor, not a novelty authority.
- https://github.com/chrisbutner/ChessCoach

## Implementation milestones

### I0 — PGN evidence spine — CLOSED/PASS
- deterministic PGN replay;
- per-ply FEN, SAN/UCI, clocks/metadata when available;
- MultiPV candidate packet;
- score/PV deltas;
- schema for provenance-bearing explanation atoms.

### I1 — Concept-proxy contrast, rating-band salience & renderer contract — CLOSED/PASS
Do not narrate every move equally.
Trigger on combinations of:
- evaluation or WDL change;
- top-candidate margin;
- tactical event;
- irreversible structural change;
- novelty/criticality heuristics;
- user-requested depth.

Evaluate precision/recall against annotated games and human preference, not only score swing.

I1 executable additions:
- exact board-derived proxy snapshots for center control/occupancy, home-square minor pieces, doubled/isolated/passed pawns, king-shield proxy and open files;
- played-vs-top-candidate proxy deltas, explicitly descriptive rather than causal;
- rating-band default salience thresholds: beginner 80cp, intermediate 50cp, advanced 25cp, expert 15cp;
- stable evidence atom IDs for renderer traceability;
- bounded renderer contract requiring provenance preservation and abstention.

### I2 — Verified tactical evidence, candidate contrast routing & graph quality — CLOSED/PASS
Implemented:
- exact board-verifiable capture/castling/promotion/check/checkmate facts;
- moved-piece multi-attack detection using explicit attacked-piece sets;
- newly created absolute-pin detection against the enemy king;
- played-vs-top-alternative tactical contrast packets;
- evidence-first commentary category routing across causal contrast / tactics / comparison / positional proxy / material context;
- graph-quality packet for provenance coverage, atom-ID traceability, firewall failures and category coverage.

I2 deliberately stops short of unverified labels such as tactical "threat", "overload" or "deflection" unless a future adapter can prove the corresponding relation. Conventional adapters remain `CONVENTIONAL_HEURISTIC_COMMENTARY` and cannot establish engine-decision causality.

### I3 — Retrieval, typed explanation graph & multi-axis evaluation — CLOSED/PASS
Implemented:
- license/source-bearing retrieval records with bounded excerpts;
- explicit rejection of inadmissible retrieval provenance;
- retrieval references remain conventional heuristic evidence;
- per-moment typed graph linking moves, evidence atoms and provenance objects;
- Structural / Motif / Tactic / Position-Judgment / Semantic / Contrastiveness / Provenance evaluation packet;
- human-utility fields deliberately unset until human adjudication.

### I4 — C3X bridge + verified planning evidence — CLOSED/PASS
Implemented:
- normalize existing C3X causal certificates into first-class `causal_certificate` graph objects with explicit authority ceilings and `authorizes_causal_scope` edges;
- legally replay bounded engine PVs and emit only verified line facts; strategic “threat/plan” labels remain abstained unless a later verifier proves their semantics;
- audit retrieval corpora for source URI, license state, tags and excerpt bounds before retrieval;
- preserve explicit abstention when strategic semantics outrun verified evidence.

### I5 — Bounded renderer + atomic factuality benchmark — CLOSED/PASS
Before free-form prose is trusted:
- every rendered claim maps back to atom IDs through `c3x-bounded-render-packet-v1`;
- ACT-Eval-style atomic factuality checks enforce atom traceability, provenance/authority presence and causal-scope discipline; legality/tactical/evaluation-direction checks remain delegated to verified atoms/firewalls;
- output a machine-readable atomic renderer benchmark while leaving human strategic completeness explicitly unset;
- never use an LLM as its own sole factuality judge.

### I6 — Claim-bounded language realization — CLOSED/PASS
The live implementation uses deterministic claim-bounded realization before any future free-form NLG:
- every sentence retains claim IDs and atom IDs;
- provenance and authority are copied, never inferred upward;
- I5 claim order is preserved;
- unsupported material is omitted/abstained rather than invented;
- free-form LLM prose is disabled at this authority level.

A future LLM/NLG adapter may improve style only after receiving this bounded packet; it remains a renderer, not an authority source.

### I7 — Adversarial surface verification firewall — CLOSED/PASS
The live verifier reverse-traces every sentence to bounded source claims and atoms. It rejects:
- missing atom/claim traces;
- provenance mismatch or authority upgrade;
- unsupported causal wording;
- surface-text tampering;
- causal wording without a first-class C3X certificate in the typed graph.

Canonical I6/I7 CI: run `36686880718`, head `4ab6fcf14ab8d61c0fd6251b94c58d665b460255`: 15/15 tests PASS; pinned Stockfish smoke `C3X_EXPLAIN_PINNED_STOCKFISH_PASS 3 10 12`; clean pass 1.0; adversarial rejection 1.0.

### I8 — Human-Utility World Contact, Rating-Band-Stratified Human Utility, Blind Baseline Preference, Explanation-Induced Move Understanding, Calibration/Trust & Authority-Separated Commentary Evaluation — CLOSED / HUMAN-UTILITY CLAIM HOLD
Terminal autonomous verdict:
- preference trials and move-understanding trials are separated before any human outcome was opened;
- blind preference uses paired randomized C3X-vs-baseline A/B exposure;
- explanation-induced understanding uses single-arm randomized C3X / baseline / no-commentary exposure;
- beginner / intermediate / advanced / expert strata are preserved;
- correctness, usefulness, pedagogical clarity, preference, understanding and trust are non-substitutable endpoints;
- trust calibration requires known valid/invalid controls rather than mean confidence alone;
- move-understanding reports expected/observed/missing denominators plus worst/best-case missingness bounds;
- participant packets are separated from adjudication keys;
- zero human rows yield `NO_HUMAN_UTILITY_CLAIM`;
- human judgments cannot promote causal authority or rescue I5-I7 failures.

Canonical terminal-design CI before roadmap seal: run `36691177181`, head `ab2e7390f4c598c681304e9bb9157b21c43c4e5a`: unit PASS + pinned Stockfish smoke PASS.

The I8 stage is **CLOSED** because all admissible autonomous work and the stopping boundary are exhausted. The empirical human-utility proposition is **HOLD / UNADJUDICATED**. Reopening requires genuine human-world-contact observations; synthetic preferences or model-judged pseudo-participants do not qualify.

See `docs/EXPLANATION_I8.md`.

## Non-goals

Track B does not need every component to be novel.
A strong product can be mostly excellent integration plus a small number of genuinely new C3X evidence primitives.

Conversely, Track A can publish a novel mechanism result even if the commentator UI remains immature.

## Reopening rule

Implementation development may proceed alongside later C3X science, but must never modify a frozen scientific constitution to improve commentary coverage.

The beyond-chess axis remains off until the chess science and this PGN pipeline each reach credible completion.
