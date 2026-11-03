# C3X 0.29-P29 — Prospective Rival Forecast Court (Frozen Design Draft)

Date 2026-11-03. No actual test outcome inspected. This design is NOT yet an independently timestamp-sealed preregistration; freeze it before generating/selecting any new results.

## Hypothesis and alternative
H0: conditional plan information Q does not improve independently measured game-cluster paired forecast quality over the strongest matched static or engine-baseline forecaster at identical engine/token budget.
H1: Q adds positive out-of-sample game-macro Brier gain without violating source-correctness and at matched decision coverage. Distinguish this empirical claim from stronger engine-causal mediation and human learning, which require separate tests.

## Experimental units, splits, and eligibility
- All original complete source games and rights/history, legal continuations, independent provenance checksum. Source game is the unit of split and uncertainty.
- Frozen candidate set of two viable near-equal moves, with repeated fixed score/nodes/time budgets and root-side utility perspective. If rank direction flips, HOLD stable preference attribution even if structural differences remain.
- In a separate control stratum choose gap >=75cp, with matched input to BinProp motif methods; never pool its effects with near-equal stratum.
- Development includes historical 0.16's twelve and 0.27's game14, NEVER counted as new prospective heldout.
- External new dataset reserved by complete game ID prior to generating Q, selecting H, fitting thresholds, or opening oracle outcomes.

## Prospective target and leakage control
Construct a binary Y by an independently selected evaluation protocol; a candidate example is whether the plan-relevant verified board consequence survives a separately heldout opponent response family at horizon H. A stronger engine value at a NEW fixed budget is supplementary, not automatically an independent factual oracle. Freeze the exact target definition and response sampling before any score observation.
- No plan features derived from target-generation engine private PV if baseline does not also get that information.
- Do not train against same Y with results opened from matching games.
- Compare plan forecast vs (1) raw root value/PV, (2) a static board concept, (3) machine-readable plan facts, (4) BinProp/CCC-style executable benchmark if accessible. Compare both forecast quality and coverage.
- Explanations may be wrong even when Y forecast improves; measure factual truth and legal rebuttal examples separately.

## Report precommit outcomes
Primary: game-macro paired Brier gain at matched heldout predictions. Secondary: per-case paired Brier, worst-group robustness, factual claim error, gold idea recall, opportunity cost, measured explanation coverage, runtime budget, human blind transfer. Report confidence intervals by independent source game, not by correlated branch or one game's many examples.
- Before opening heldout commit exact scripts, Q, H, cohort and manifest checksums, model versions/prompts/seeds and run limits.
- Do not retrofit failed labels, drop difficult opponent replies, or change comparison baselines after outcome.
- Admit zero/negative game-macro advantage as real failure; Q-only value gain with no truth/coverage is not explanatory success.

## Ready vs blocked
Ready: algebra, three evaluation tools and synthetic regression tests in tools/c3x_029_p29_*.py; original Go chess code previously independently source hashed and unit tested in P22.
Blocked: new complete game source, matching native engine, independent labels, actual competing model output, preregistered prospective seal and human transfer. Current work is an experiment plan, not a performance result.
