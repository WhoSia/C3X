# C3X 0.12 — Counterfactual Strategic Preference Explanation, Minimal Intervention-Sufficient Reasons, Rival Continuation Falsification & Cross-Engine Explanatory Transport Experiment

Status: OPEN — constitutional design / no empirical result.
Predecessor: C3X 0.11 CLOSED_TECHNICAL_HOLD. P23 FAIL; P24/P25 HOLD; Q0 DENIED.

## Explanandum
For legal near-equal moves a and b from the same chess position, can we determine a minimal, intervention-testable strategic reason why an engine prefers a to b? A coherent commentary, a high score or agreement with human concepts alone does not constitute such a reason.

## Prospective rivals
H1: board-feature mediated strategic preference.
H2: alternative legal continuation / search-mediator contingent preference.
H3: engine/context-specific preference not transported.
H0: no identifiable explanatory reason beyond observed ranking.

## Design obligations
1. Freeze move pairs and pair eligibility without consulting prospective explanatory outcomes.
2. Define an explicit estimand (preference sign and margin under engine, depth/runtime and legal intervention context).
3. Declare legality-preserving interventions and an independent control intervention.
4. Pre-register rival predictions and concrete falsifiers, including explanation abstention.
5. Audit engine evidence separately from language commentary and human strategic labels.
6. Separately test cross-engine and cross-ecology transport on source-disjoint held-out units. No automatic promotion from 0.11.
7. Keep historical-FEN exclusion as contamination control, NOT a discovery-of-new-position claim.

## Method and polyglot plan
Doctrine: https://app.notion.com/p/3e9ef561cf9281008219e330bcce1b55
Choose language by executable role, not popularity:
- C++ / native UCI engines: search and intervention execution.
- Rust (candidate): typed experiment event / validator and fail-closed durable ledger; only if a distinct correctness benefit emerges.
- SQL (candidate): provenance, pair joins and clustered outcome audits.
- Python: chess corpus preparation and exploratory prototyping only where it saves time.
- YAML / shell: hermetic orchestration; never author GitHub commits via Actions.
Do not implement all languages ceremonially. Define versioned IR and exactly one authoritative data owner.

## Literature/rival anchors
- ChessGPT: Feng et al. 2023, https://arxiv.org/abs/2306.09200, code https://github.com/waterhorse1/ChessGPT. Policy+language learning is not intervention-grounded causal explanation.
- Maia-2: Tang et al. 2024, https://arxiv.org/abs/2409.20553, code https://github.com/CSSLab/maia2. Human-move prediction is not reason-identifiability.
- Searchless Chess/ChessBench: Ruoss et al. 2024, https://arxiv.org/abs/2402.04494, code https://github.com/google-deepmind/searchless_chess. Distilled action values are not automatically strategic explanations.
- McGrath et al. 2022, https://arxiv.org/abs/2111.09259. Human concept probing of AlphaZero is not direct local counterfactual sufficiency.
Full-text and repository methodological audit pending; prior existence in Drive is not proof of complete re-reading.

## Authority
Constitution/design only. No 0.12 interventions executed, no success claim and no historical failure reversal. No Work Mode.
