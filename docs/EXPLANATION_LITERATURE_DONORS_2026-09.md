# C3X Explanation Implementation — Literature Donor Map (2026-09-30)

This page is **Track B engineering evidence**, not Track A novelty authority.

## Core commentary lineage

### Jhamtani et al. — ACL 2018
**Learning to Generate Move-by-Move Commentary for Chess Games from Large-Scale Social Forum Data**
- 298K+ move-commentary pairs across 11K games.
- Donor: move salience, pragmatic context, style diversity, human-evaluation design.
- DOI: 10.18653/v1/P18-1154
- https://aclanthology.org/P18-1154/

### Zang, Yu & Wan — ACL 2019
**Automated Chess Commentator Powered by Neural Chess Engine**
- Engine-grounded generation across commentary categories including description, comparison and planning.
- Donor: category routing and expert-model grounding.
- DOI: 10.18653/v1/P19-1597
- https://aclanthology.org/P19-1597/

### Kim et al. — NAACL 2025
**Bridging the Gap between Expert and Language Models: Concept-guided Chess Commentary Generation and Evaluation**
- Prioritized concept bridge from expert model to LLM; dedicated commentary evaluation.
- Donor: concept adapters, expert→language architecture, evaluation.
- DOI: 10.18653/v1/2025.naacl-long.481
- https://aclanthology.org/2025.naacl-long.481/

## Explainability / faithfulness

### Spinnato — 2025
**Towards Piece-by-Piece Explanations for Chess Positions with SHAP**
- Piece-level ablation/attribution.
- Donor: conventional XAI baseline and visual explanation surface.
- Not equivalent to C3X exact search-event causal authority.
- https://arxiv.org/abs/2510.25775

### Parfenova — 2026
**Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness**
- Fluent explanations can be coherent with an action without reliably exposing the decision process.
- Donor: faithfulness tests, masked-reasoning controls, strict separation between narration and causal authority.
- https://arxiv.org/abs/2609.22245

### Ciancarini & Pareschi — 2026
**What Counts as Strategic Reasoning? A Systematic Mapping of Chess Research on Humans, Engines, and Language Models**
- Maps 84 study families; identifies grounded/faithful explanation, planning, metacognition and human–AI complementarity as comparatively open areas.
- Donor: evaluation taxonomy and product/research gap map.
- https://arxiv.org/abs/2609.18286

## Practical architecture donor

### ChessCoach
- End-to-end chess engine plus natural-language commentary pipeline, PGN processing and commentary tooling.
- Donor: product architecture, not novelty authority.
- https://github.com/chrisbutner/ChessCoach

## C3X synthesis

The Track-B architecture therefore treats language as the final renderer, not the source of authority:

`PGN → engine/candidate evidence → verified chess facts/concepts → optional C3X causal certificate → typed explanation graph → language renderer → factuality/provenance firewall`.

The scientific novelty question remains separate: only prospective C3X intervention evidence can populate `C3X_CAUSAL_CONTRAST`.
