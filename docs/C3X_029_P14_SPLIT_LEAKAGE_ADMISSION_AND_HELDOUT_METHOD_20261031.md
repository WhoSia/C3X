# C3X 0.29-P14 — Source-Disjoint Benchmark Admission Before Performance

Date: 2026-10-31. Question: can an explanation robustness result survive new games, or is it continuation leakage from the same historical game?

## Blocker found
Existing P13 binary evaluator correctly computes the minimum of accuracies on positive, negative, nearby-negative inputs, but requires only a game_id string; source games could still occur in both support and heldout. Since a single chess game yields correlated positions and continuations, a heldout evaluation can become disguised within-game interpolation. Its distinct-game count does not prove train/heldout game disjointness.

## New method
`tools/c3x_029_p14_benchmark_source_split_gate.py` runs before P13 scoring and requires case identity, game, root, continuation, split, group and boolean verified-declaration fields. It rejects same game, root or continuation appearing across different partitions; incomplete heldout groups; no heldout; missing or false verification declarations. A pass is specifically `METADATA_ADMISSIBLE_NOT_BYTE_VERIFIED` because these fields are user/collector asserted; original PGNs, legal continuations and engine source must be independently audited before empirical authority.

Independent tests include cross-split same-game different-root, cross-split same continuation, unverified engine labels, incomplete heldout nearby negatives, and no heldout. CI workflow includes tests; green remote execution not confirmed.

## Rival experimental estimands
C3X hypothesis should be tested in near-equal root candidates, not only BinProp >=75cp position gap. Predeclare group selection and report original maximum root score variability under equal budgets. Use actual source histories, not only FEN if repetition/50move may affect output. Keep `root_id` stable across different branch outputs; keep `game_id` stable across all positions from one PGN. An outer game-level split must precede candidate-motif fitting, hyperparameter selection or negative construction, rather than apply after data leakage occurs.

## Competition design
- Same public input budget and legal action space, source-protected engine calculations disclosed by arms.
- Blind train/dev/test game partitions.
- Positive/negative/nearby-negative accuracy, ACT-Eval factual claim errors and expert idea recall, C3X quantified reply-domain proof and counterexamples, calibration/abstention, execution budget.
- Stratify true near-equal candidates versus >=75cp gap; don't compare binprop score directly to legal universal-policy proof as they measure different properties.
- Freeze negative-pair and motif selection before heldout score exposure, retain 0.27 P3 failures as development only.
- Report per-game uncertainty, not nominally independent 24/position continuation samples. At present all effects/advantage claims HOLD.

No fresh Stockfish run, no original 0.27 JSON used; this is a deliberately narrow methods artifact to enable later meaningful tests. The original P13 Notion record was successfully created and reread in this turn at https://app.notion.com/p/40aef561cf928132b740f96377444211.
