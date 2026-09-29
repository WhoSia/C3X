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

### I0 — PGN evidence spine
- deterministic PGN replay;
- per-ply FEN, SAN/UCI, clocks/metadata when available;
- MultiPV candidate packet;
- score/PV deltas;
- schema for provenance-bearing explanation atoms.

### I1 — Moment selection
Do not narrate every move equally.
Trigger on combinations of:
- evaluation or WDL change;
- top-candidate margin;
- tactical event;
- irreversible structural change;
- novelty/criticality heuristics;
- user-requested depth.

Evaluate precision/recall against annotated games and human preference, not only score swing.

### I2 — Conventional explanation adapters
Implement clearly labelled adapters for:
- tactics: checks, captures, threats, pins, forks, skewers, discovered attacks, overload, deflection, trapped pieces, mating nets;
- material and exchange accounting;
- king safety;
- pawn structure;
- mobility / space proxies;
- open files, diagonals and outposts;
- development and piece activity;
- endgame-specific motifs.

These can be engineered from known techniques and do not require C3X novelty.

### I3 — Retrieval and commentary corpora
- retrieve similar annotated positions/motifs;
- use licensed/permission-compatible corpora;
- preserve source and licensing metadata;
- separate retrieved human phrasing from newly generated analysis.

### I4 — C3X bridge adapter
A P15+ Mechanism Bridge Card becomes an explanation atom:
- candidate pair;
- board difference;
- search mediator;
- counterfactual choice;
- authority ceiling.

The language layer may paraphrase it, but cannot broaden it.

### I5 — Explanation graph
Before prose, construct a typed graph:
- claim;
- candidate move(s);
- supporting evidence;
- counterfactual;
- tactical/positional concept;
- provenance class;
- confidence / abstention reason;
- source/certificate IDs.

### I6 — Language realization
LLM or other NLG is a **renderer**, not the authority source.
It receives only the structured graph plus bounded chess context and must preserve:
- move identities;
- side to move;
- evaluation direction;
- causal vs heuristic wording;
- uncertainty.

### I7 — Verification firewall
Automatically reject or downgrade commentary if:
- SAN/UCI is illegal or mismatched;
- claimed tactic has no verified line;
- evaluation direction contradicts evidence;
- a C3X causal phrase lacks a certificate;
- retrieval attribution is missing;
- causal scope is broadened beyond the certificate.

### I8 — Human utility
Evaluate separately:
- correctness;
- usefulness to different rating bands;
- contrastiveness;
- pedagogical clarity;
- calibration/trust;
- preference over baseline engine prose;
- whether explanation improves subsequent move understanding.

## Non-goals

Track B does not need every component to be novel.
A strong product can be mostly excellent integration plus a small number of genuinely new C3X evidence primitives.

Conversely, Track A can publish a novel mechanism result even if the commentator UI remains immature.

## Reopening rule

Implementation development may proceed alongside later C3X science, but must never modify a frozen scientific constitution to improve commentary coverage.

The beyond-chess axis remains off until the chess science and this PGN pipeline each reach credible completion.
