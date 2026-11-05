# C3X 0.29-P42/R2 — Cost, Chronology, Chess Legality & Independent Evidence Admissibility Court
Date: 2026-11-05 KST. **Adversarial synthetic structural research, not actual chess-value validation.**

## Question
Can a P41 case pass its structural preflight while failing a more demanding claim of fair, prospective, source-independent chess evidence? **Yes by construction**. The existing test fixture openly reuses e2e4 sixty times without legal replay; the original author explicitly disclaims chess-law certification. The original P41 implementation also caps individual actual costs, instead of establishing cost equivalence or estimating a cost-conditioned performance frontier; PRE_JUDGE is a self-supplied field rather than external time evidence.

## Original code and reproduction
- `tools/c3x_029_p41_r3_independent_plan_court_preflight.py` verifies source digest consistency, stated event/game exclusion, plan digest, stated PRE_JUDGE phase, candidate consistency, stated independent judge and per-method caps.
- The original `tools/test_c3x_029_p41_r3_independent_plan_court_preflight.py` deliberately uses fictitious non-legal move history and was never intended as a chess legality gate.
- If the PV method reports 1,000 native nodes and other methods 24,000, the original preflight can still return PASS_STRUCTURAL_PREFLIGHT_ONLY; equal *ceilings* do not imply equal *actual* resource use. A separate methodological comparison should either match actual resource vectors within preregistered tolerance or explicitly compare cost-conditioned / Pareto performance, not call unequal use equal-cost evidence.
- The original self-consistent phase/digest can be supplied after a reference judge has finished; a hash checks bytes, not the independent ordering of artifacts. Do not claim leakage occurred in prior experiments: the counterexample is a **design vulnerability**.

## New isolated P42/R2 implementation
`tools/c3x_029_p42_r2_cost_chronology_admission.py` operates beside and does **not mutate** P41. It requires reported dimensions native_nodes, legal_expansions, cpu_ms, engine_queries, model_tokens, model_calls for all four mandatory baselines; refuses missing, negative, or boolean-as-count fields; computes min/max and reports >10% observed imbalance (default). The check is intentionally strict and is not a normative proof that equal cost is the only valid scientific design. Efficiency experiments should explicitly use cost-conditioning rather than declaring an unmatched design matched.

An additional science admission gate demands separately trusted source custody, actual chess legality, independent temporal seal of prediction before judge, independently audited compute ledger, and independently verified judge provenance. Its injected trusted_* booleans are **interfaces for independent certification by the caller**; they are not verifiable evidence, and must never be copied from the case JSON. Even when all inputs are declared valid, the output is only READY_FOR_SEPARATE_VALUE_EVALUATION_NOT_CHESS_PASS, not a chess-value performance PASS.

Eight synthetic regression cases target mismatched nodes, fictitious chess history, bogus chronology, missing cost records, good declared ledger with external checks, zero-vs-one model calls, boolean count spoofing, and P41 global cap violation.

## Research interpretation
1. Root candidate preference and within-root plan regret are distinct (P42/R1 proof).
2. Prospective plan prediction needs an immutable external chronological seal; digest and PRE_JUDGE are insufficient.
3. Equal maximal resource ceilings are different from equal actual resource use, and neither alone proves equivalent exposure to evaluation information.
4. The 2026 Cui/Ling/Ng strategy tree is a mandatory strong baseline, not merely PV and one-reply JSON. Compare under true measured resources or preregistered cost-performance frontiers.
5. A verified source-independent value judge remains mandatory. Historic P38 Ethereal shallow 2–5 actual nodes are not qualified.
6. A G1/G2 chess-value result never establishes G3 NNUE→search ancestor→unrestricted root mediation without separate intervention evidence.

## Claim status, provenance, execution
- **New source**: `tools/c3x_029_p42_r2_cost_chronology_admission.py`
- **New regression tests (8 authored)**: `tools/test_c3x_029_p42_r2_cost_chronology_admission.py`
- **No native chess search or new GitHub Actions run** was performed by this unit. Code writing and authoring tests do not by themselves establish tests PASS.
- The older P41 R2/R3/R4 queue timestamps must not be implicitly upgraded to PASS from their written records.
- This does not establish a new chess explanation, outcome predictor, heldout cohort, or independent external referee.
- Git author/committer must be WhoSia; no github-actions[bot] pushes or commits. Notion meaning, Drive original bytes, GitHub reproducible code. Drive mirror remains a separately required byte custody check.

## Next research PI gate
Require one authentic independent-source challenging near-equal pair, verified immutable pre-J source and prediction seal, actual J source/binary/native node court, G1 root value and G2 plan value labels from heldout games, four honest competitor cost-performance accounting; only after any G1/G2 empirical success consider G3 NNUE mechanism experiment. Retain all negative results and abstentions.
