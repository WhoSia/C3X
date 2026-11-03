# C3X 0.29-P30/R2 — Novelty and Risk Court After Reading Miller (2019)

2026-11-03. This is an intentionally adversarial pre-experimental review, not a paper novelty certification.

## Known: what is NOT new
1. A contrastive 'why P rather than Q' question and the need to specify a *foil*: extensively studied, cf. Miller 2019 Sections 1.2 and 2.3; earlier philosophers including Lipton. **Not C3X novelty.**
2. Selecting only a short subset of relevant reasons and adapting wording to a human: described in prior social explanation research; **not C3X novelty**.
3. Planning as an initiation set, contingent policy and termination condition: Sutton–Precup–Singh 1999; **not novel**.
4. A possible plan having less value than an alternative: finite minimax and RL return are standard conceptual tools, **not a novel theorem**.
5. Tool-grounded checking of chess factual statements: strong comparison needed with ACT-Eval and actual tool-based explanations; **not sufficient for novelty**.
6. Root order influences Stockfish output: original C3X 0.17 exposed development record 12 source roots and 2 changed bestmove, **not proof of transferable strategic causes**.

## Unproven but falsifiable incremental research hypothesis
A system can extract a **user-chosen foil-specific, opponent-response-robust, utility-aligned policy consequence** for near-equal but viable chess candidate moves and can predict source-independent heldout consequences with fewer factual errors and less abstention than strong static score/PV, executable concept, and ordinary plan-text explanations at matched compute. This is a conjunction of existing ideas with potential new verified empirical value, NOT established originality or superiority until independent holdout.

## Critical competing alternatives
A. **Raw engine+PV**: short direct bestmove/score and principal continuation; cheap.
B. **Static concept label**: standard mobility/king safety/pawn structure with factual chess audit.
C. **Engine+human/LLM generic explanation**: fluent, high-coverage.
D. **Simple rule-based plan JSON**: user foil supplied, fixed legal enumeration and value. This is the **most important ablation**: if it matches C3X, formal proof-carrying architecture has not earned its complexity.
E. **BinProp nearby-negative executable binary concept**: compare robustly on its applicable domain; published threshold >=75cp and paired C3X near-equal target are not naturally interchangeable.
F. **ACT-Eval backed atomic evaluation**: check factual explanation claims and gold atom coverage; comparison requires mutually aligned truth rubrics, not fabricated one-dimensional scores.

## Study design: reject five ways of gaming 'better'
1. Always abstaining: report coverage at fixed selective-risk and risk at fixed coverage.
2. Choosing easy foils: users or a precommitted deterministic selector specify foils before result inspection.
3. Using outcome to choose Q: hash Q/horizon/candidate triples, seal, then open labels; the boolean in P30 code is currently caller-declared and NOT cryptographic proof.
4. Comparing unlike domains: report near-equal and >=75cp strata separately, with complete source-game disjointness and independent reply worlds.
5. Scoring generated text by its own AI judge: independent chess law and value oracle, blind human response study separately.

## Human learning falsifier after Miller
Ask participants to predict a near-equal follow-up board or choose between two new candidates after seeing one of A-D explanations, under the same time. Outcome includes independent choice correctness, correct causal/generalizable rationale, calibrated confidence and error when the AI itself is wrong. Human preference or trust alone is not learning transfer. Explanations may harm by overpersuasion; include unsupported-claim checks.

## Exit criteria for P30
Source-backed archive audit and documented green CI achieved. **Stop adding metrology-only rubrics** until a NEW native/independent source cohort is opened; next unit should be actual chess game-history acquisition and first foil-specific rule/value witnesses. If source never arrives, publish HOLD and preserve tests, not re-label a mathematical example as discovery.

## Source references
Miller original Drive id 1b0Zqep9G93Mc-u-GFZ78gYXB6Oyhleke (now canonical 10_PAPERS); original 0.17 native receipt c3x/receipts/c3x-017-opening-12-independent-Lichess-root-order-72native-P4-legacy-id-20261009.json; P29 source review docs/C3X_029_P29_PLAN_VALUE_INFORMATION_SCIENCE_COURT_20261103.md. Every external paper's claims separated from OUR testable extrapolations.
