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

### Wang et al. — NAACL 2025
**Explore the Reasoning Capability of LLMs in the Chess Testbed**
- Introduces MATE, a 1M-position dataset with strategy/tactic annotations for candidate moves.
- Donor: candidate-level tactic/strategy supervision, category-conditioned evaluation and theme coverage.
- DOI: 10.18653/v1/2025.naacl-short.52
- https://aclanthology.org/2025.naacl-short.52/

### Wen, Tang & Anderson — 2025
**ChessQA: Evaluating Large Language Models for Chess Understanding**
- Separates Structural, Motifs, Short Tactics, Position Judgment and Semantic understanding.
- Donor: multi-axis utility/competence evaluation; do not collapse commentary quality into one score.
- https://arxiv.org/abs/2510.23948

### Tang et al. — 2026
**Grounded Chess Reasoning in Language Models via Master Distillation**
- Distills expert-system reasoning into language and reports large gains in chess reasoning.
- Donor: expert-to-language training architecture and theme-balanced coverage.
- C3X difference: generated reasoning remains Track-B implementation evidence unless independently tied to a C3X causal certificate.
- https://arxiv.org/abs/2603.20510

### Dionisopoulos, Majamaki & Ammanabrolu — 2026
**Reasoning Through Chess: How Reasoning Evolves from Data Through Fine-Tuning and Reinforcement Learning**
- Reports that move quality and reasoning faithfulness can diverge, and that multi-move trajectory training can improve faithfulness relative to direct best-move training.
- Donor: separate move-quality, hallucination and reasoning-faithfulness evaluation axes.
- https://arxiv.org/abs/2604.05134

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


### Hebbar et al. — 2026
**Hallucinations on the Board: Tool-Augmented Evaluation of LLM Chess Commentary**
- Decomposes chess commentary into atomic claims and routes them to engine-supported tools / expert references for factuality and coverage evaluation.
- Reports that fluent LLM commentary still contains substantial factual sub-claim errors without tool grounding.
- Donor: atom-level factuality adjudication, tool routing, error taxonomy and coverage-vs-correctness separation.
- C3X use: strengthens Track-B evaluation/firewall design only; it does not supply Track-A causal authority.
- https://arxiv.org/abs/2608.04240


## 2026-09-30 — faithfulness and grounded-reasoning expansion

### Parfenova 2026 — explanation faithfulness warning
- Role: adversarial donor for the authority firewall.
- Product use: coherent or plausible chess language must not be treated as evidence that the stated reason caused the model decision.
- C3X response: I4 first-class causal certificates + I5 claim-level traceability keep narration downstream of evidence.

### Tang et al. 2026 — Grounded Chess Reasoning in Language Models via Master Distillation
- Role: donor for expert-system → natural-language transfer.
- Product use: suggests a future training path where verified engine/evidence packets supervise language realization.
- Authority boundary: distillation quality does not create C3X causal authority.

### Dionisopoulos et al. 2026 — How Reasoning Evolves from Post-Training Data
- Role: donor for reasoning-data design.
- Product use: multi-move trajectory supervision is relevant to future renderer/learning experiments because isolated best-move supervision can encourage unfaithful rationale generation.
- Authority boundary: this motivates data design, not a Track A claim.

### Hammersborg & Strümke 2024 — information-based chess XAI
- Role: donor/rival family for concept-level information-flow explanation.
- Product use: useful benchmark axis for concept evidence and information localization.
- Authority boundary: information attribution remains distinct from C3X intervention certificates.
