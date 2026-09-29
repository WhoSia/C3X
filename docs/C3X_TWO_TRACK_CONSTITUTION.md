# C3X Two-Track Constitution — Scientific Novelty vs PGN Explanation Implementation

## 1. Binding split

C3X deliberately maintains two different success functions inside one repository.

### Track A — Science / Novelty Mainline

Founding explanandum:

> Why is one legal move marginally preferred over a near-equal alternative beyond obvious tactical dominance?

Track A earns authority through prospective world contact: matched board interventions, exact search interventions, candidate-pair preference changes, fresh replication, transport tests, falsifiers, and explicit claim ceilings.

A finer mechanism catalogue is not progress by itself. A Track A stage is mainline only when it reduces uncertainty about the move-vs-move contrast.

### Track B — Explanation Implementation

Product target:

> Given a PGN, produce useful, high-quality chess commentary with inspectable provenance.

Track B may borrow aggressively from existing chess, XAI, NLP, retrieval, engine-analysis, and commentary-generation literature, including MultiPV, tactical motif detectors, positional concept recognizers, evaluation decomposition, annotated-game corpora, retrieval, calibration, and LLM verbalization.

Its success criteria are practical:
- chess correctness;
- contrastiveness;
- pedagogical usefulness;
- faithfulness/provenance;
- coverage and abstention;
- latency, reproducibility, and UX.

Borrowed implementation techniques do not become C3X scientific novelty merely because they are integrated.

## 2. Authority firewall

Every explanation-capable artifact must distinguish at least two provenance classes:

1. `C3X_CAUSAL_CONTRAST`
   - backed by an explicit C3X intervention/certificate;
   - may inherit only the claim authority stated by that certificate.

2. `CONVENTIONAL_HEURISTIC_COMMENTARY`
   - useful chess interpretation from standard engine analysis, literature, retrieval, motif/concept models, or language models;
   - may not be presented as a C3X causal discovery.

A user-facing explanation may combine both, but the provenance boundary must remain machine-readable and inspectable.

## 3. Repository policy

GitHub is the correct executable home for both tracks.

Track A authority-bearing surfaces include:
- `c3x/ontology/`
- `c3x/protocol/`
- `c3x/receipts/`
- prospective harnesses and Courts
- independent claim verifiers

Track B may add:
- PGN ingestion and segmentation
- candidate-pair extraction
- conventional engine-analysis adapters
- tactical/positional concept detectors
- retrieval and commentary corpora
- explanation composition and rendering
- product evaluation and calibration

Shared libraries are allowed when their role and authority are explicit.

A Track B CI PASS cannot promote a Track A scientific claim.
A Track A scientific PASS does not certify that generated commentary is useful or pedagogically good.

## 4. Origin lock

Before opening a scientific successor, ask:

> Did this stage make the answer to “why this move rather than that near-equal legal move?” more causally precise?

If not, classify the work as infrastructure, diagnostic support, or explanation implementation rather than mainline science.

## 5. Completion relation

The long-run chess objective requires both tracks:

- Track A: reliable contrastive causal evidence for meaningful classes of near-equal decisions.
- Track B: a PGN-to-explanation system that consumes C3X certificates where available and uses clearly labelled conventional methods elsewhere.

Neither completion condition substitutes for the other.

## 6. Beyond-chess hold

Transfer to Go, protein-structure systems, planning agents, or other decision systems remains dormant.

What may eventually transport is the explanation architecture and intervention discipline, not Stockfish-specific mechanisms.

Reopen only after both:
- the chess science mainline has reached a credible contrastive-explanation milestone; and
- the PGN explanation implementation can produce useful end-to-end commentary with provenance.
