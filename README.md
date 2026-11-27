# C3X — Counterfactual Contrastive Chess eXplanation

**Research version 0.31 · ACTIVE · scientific claims gated**  
Updated 2026-11-27. [Canonical Notion lab](https://app.notion.com/p/3c4ef561cf92817ab76bcab15e7d1faf) · [R36 GPT-6.2 × Claude collaboration](https://app.notion.com/p/425ef561cf928191be10d1f82d7e322a)

## Research question

Why is one legal move marginally preferred over a near-equal alternative beyond obvious tactical dominance? Can an explanation link actual search mechanisms to robust legal chess plans and remain useful to a human learner?

0.31 — *Intervention-Stable Decision-State Abstraction: Minimal Search-Memory Causality, Robust Chess-Plan Transport & Human Explanation Validity.* [Activation and gates](docs/C3X_031_FORMAL_ACTIVATION_AND_GATE_REGISTRY_20261121.md).

## Two tracks

| Track | Objective | Authority |
| --- | --- | --- |
| A — Science | Identify and falsify causal explanations of near-equal moves | Source contact, physical interventions, prospective transport, bounded claims |
| B — Explanation | PGN → evidence-aware practical chess commentary | Legal replay, factuality, contrast, provenance, calibration, learner utility |

[Two-Track Constitution](docs/C3X_TWO_TRACK_CONSTITUTION.md) · [Implementation and historical milestones](docs/EXPLANATION_IMPLEMENTATION_TRACK.md). Neither track certifies the other. Distinguish C3X_CAUSAL_CONTRAST from CONVENTIONAL_HEURISTIC_COMMENTARY.

## Current evidence and open frontier

| Finding | Evidence and scope |
| --- | --- |
| P2 predictor | [Negative prospective transport](docs/C3X_031_P2_TWIC1670_TRUE_NATIVE_TRANSPORT_RESULTS_20261121.md): 7/128 flips, M2 Brier .06217 vs M0 .05288. No exposed-cohort retuning as substitute for new evidence. |
| P3-A1 | [Root-only projection counterexample](docs/C3X_031_P3_A1_ROOT_ONLY_STATE_SUFFICIENCY_COUNTEREXAMPLE_20261121.md): same restricted root records, different future choices; node counts differ. |
| P3-X1 | [Physical factorial](docs/C3X_031_P3_X1_FULL_NATIVE_FACTORIAL_RESULTS_20261121.md): 0/128 null-only, 8/128 futility-only, 14/128 joint changes. |
| P3-X2 | [Depth and budget](docs/C3X_031_P3_X2_DEPTH_NODE_HORIZON_RESULTS_20261121.md): finite-horizon effects and reconvergence. |
| P3-X3 | [Read-only TT observation](docs/C3X_031_P3_X3_READONLY_TT_GATE_RESULTS_20261121.md): bounded passive parity; no restoration. |
| P3-X4 | [Third-winner falsifier](docs/C3X_031_P3_X4_TWO_HISTORIES_THIRD_WINNER_CAUSAL_SPILLOVER_20261121.md): one exposed source event, two dependent horizons. Isolated target-score-only model fails under fixed-rival assumptions. |
| P3-B | [Frozen checkpoint rescue preregistration](docs/C3X_031_P3_B_STATE_FAMILY_TRANSPLANT_PREREG_20261121.md): HOLD for named mediator sufficiency, independent transport, strategic advantage and human learning. |

Track B includes PGN replay, typed evidence, tactical/positional proxies and provenance checks. No claim of superior explanation quality or learner benefit. [R36 competitor benchmark](docs/C3X_031_R36_EXPLANATION_BENCHMARK_20261127.md) is a feature scan and proposed matched study, not a measured ranking.

## Active research

- [R36 operating loop and Claude handoff](docs/C3X_031_R36_RESEARCH_LOOP_AND_COLLABORATION_20261127.md)
- [Machine-readable priority ledger](docs/C3X_031_R36_PRIORITY_LEDGER_20261127.json)
- [P3-B field and exact checkpoint audit](docs/C3X_031_R36_P3B_FIELD_AND_CHECKPOINT_AUDIT_20261127.md)
- [Repository retirement and archive custody audit](docs/C3X_031_R36_REPOSITORY_RETIREMENT_AUDIT_20261127.md)
- P3-B: original SF16 field-specific writer/reader observation, noninterference and reciprocal restoration at the preregistered boundary.
- Track B: matched outputs against direct contrastive competitors; blinded correctness, robustness and pedagogical evaluation.
- Literature: [single missing-literature ledger](https://drive.google.com/open?id=1NtFbOpy9Mcv_f-f_iIr6adDuZQTyWoy1). Drive first; no parallel lists.

Default: Discover → learn → propose → score → select → execute → verify/falsify → rescore → integrate → iterate. Scores are ordinal judgments, not probabilities. Gates and Pareto comparison precede explicit bottleneck judgment; no weighted sum. Claude results count only after actual submission.

## Repository map

| Path | Role |
| --- | --- |
| c3x/, c3x_explain/, product/ | Research primitives, explanation and product surfaces |
| patches/stockfish16/, tools/, harness/ | Source overlays, experiment drivers and validation; some legacy dependencies |
| receipts/, evidence/, frozen/ | Bounded evidence and frozen records; preserve failures |
| docs/, paper/ | Scientific reports, protocols and manuscript lineage |
| .github/workflows/, tests/, crates/, compiler/, cmd/ | Executable reproducibility and tests; historical workflows are not automatically disposable |

[Governance](GOVERNANCE.md) · [Custody](docs/CUSTODY.md). Main is canonical; no bot-authored commits. Stockfish 16 pinned upstream: `68e1e9b3811e16cad014b590d7443b9063b3eb52`.

## Historical record

The full previous README (367,102 text characters; blob `e538b9868a5b57000f1226cb2151f3fc5d28d27c`) is preserved at [pre-reorganization main d7dcba4](https://github.com/WhoSia/C3X/blob/d7dcba4cf8ee7725b9af68007b5bddcfcf226208/README.md), where relative links resolve against the original revision. This replaces navigation, not evidence. [Older 0.16 snapshot](docs/archive/README_PRE_C3X016_CANONICAL_20261009.md).

Original bytes: [Drive data room](https://drive.google.com/drive/folders/1eWHPdlKM1Jlesec7Iu87LlHbuNER0b95) · [legacy archive](https://drive.google.com/drive/folders/1kmsG0DcGLV2qnQLEtVsKqzEcue-q3L1T). Remove code only after verified Drive custody and dependency/restore checks, not simply because it is old.
