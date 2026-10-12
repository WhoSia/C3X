# C3X 0.25-P14-P1 — Actual Counterfactual Search-State Divergence and Root-Candidate Survival

**CLOSED: SOURCE-NATIVE DEVELOPMENT EXPERIMENT · 2026-10-12.** Parent original formal name is fixed as **Counterfactual Search-State Divergence & Root-Candidate Survival: Source-Matched TT Policy Interventions, Dynamic Quotient Falsification, Compensating Search Paths & Mechanism-Guided Engine Design**. This is a source-policy counterfactual over four *exposed development* positions, never an independent M5 cohort.

## Origin and precommitted source contract

The preceding P14-P0 native experiment physically suppressed one original qsearch TT score bound return and/or first original nonempty TT move hint, yet returned the same startpos UCI `b1c3` and 8,657 nodes across SHAM/SCORE/HINT/BOTH. The hypothesis that unchanged final action and node totals imply the same internal search trajectory was therefore untested.

[Pre-native source/code and registered four positions](https://github.com/WhoSia/C3X/commit/f83ae04ea8a8ad6c9fab53657dedc98548f5f60f) → [native CI #38189052448 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/38189052448) → [derived artifact, SHA256 e199cbf980a1295f88cc9a9d33798395b4905888f8b48ccaa39aafb955910f79](https://github.com/WhoSia/C3X/actions/runs/38189052448/artifacts/11721235542).

Original Stockfish16 git `68e1e9b3811e16cad014b590d7443b9063b3eb52`, exact original source SHA; seven-layer reversible source-only observers and independent original root endpoint. Threads1/Hash16MB/NNUE OFF/depth7. Each arm cold repeated twice, and original/observer SHAM/observer-off matched original UCI, nodes, root score and PV. qtrace is derived only from original qsearch executed child assignments and parent `bestValue=value` points. Final root contender fingerprint covers first move, score, UCI score, average score, PV length and score-bound flags. Both are **partial summaries**; their equality cannot certify identical full PV, TT table, entire execution path or counters. No hidden full64 TT keys, third-party PGN or modified binaries published.

## Native observed results

| Prespecified development cohort | Original root UCI | Original nodes | SCORE nodes | Root contender digest changed? | qsearch execution digest changed? |
| --- | --- | ---: | ---: | --- | --- |
| Public startpos | `b1c3` | 8657 | 8657 | No | No |
| Ruy Lopez 6-ply | `b5c6` | 1836 | 1836 | No | No |
| QGD 6-ply | `e2e3` | 7557 | 7557 | No | No |
| Sicilian 9-ply | `b8c6` | 3578 | **3579** | No | **Yes** |

All four arms' requested native qsearch score/hint contacts occurred. In Sicilian, both SCORE and BOTH add one search node and change qtrace digest, whereas HINT alone does not change registered qtrace, nodes, root contender digest or bestmove. The originally selected `b8c6`, UCI score cp:-26, and measured root contender fingerprint all remain stable. Each observed arm is deterministic on two cold executions.

This is **actual physical source-policy intervention–conditioned internal search divergence with stable observed root**, not merely a statement that some source code was instrumented. However it is not evidence of *natural* TT→SEE mediation; root contender fingerprint equality leaves internal PV structure and future TT-memory divergence unexamined. A single added node alone gives no chess-strength improvement or even efficiency gain. The other three positions' negative endpoints remain binding.

## Theory and rival accountability

An action-only observable quotient can report the same final UCI for two policy-indexed executions even when their search transition histories differ. This experiment does **not** claim to disprove fixed-policy `f=g∘π` since SCORE/BOTH and SHAM alter the policy itself. It does falsify the much weaker unwarranted inference that equality of `bestmove` and original total nodes (or final candidate fingerprint) forces equal internal source computation. More generally, distinguish:
- behavior-only observational equivalence (same bestmove);
- final bounded-summary equivalence (same UCI score, candidate digest);
- source execution equivalence (same true native qsearch event flow);
- natural mediator-specific causal effect (still unproven);
- prospective behavior prediction or engine superiority (not tested).

The precommitted H0 "registered qsource and root contenders identical under every contact" fails in Sicilian SCORE/BOTH. H1 "one or more qsearch path differences masked at root" is supported at the source-summary level; do not assume the exact compensation route without value-slice descendant alignment. H2 "root contender scores/viability visibly shift with same winner" lacks support in registered root digest. H3 "bestmove changes" not observed in this four-position development trial.

## Next P14-P2 / P15 research direction

Route to a *proximal and falsifiable* source event: pair baseline and intervention sibling execution, identify first native qreturn or bestValue branch divergence within the same program prefix, then measure root contender individual scores/PV, not only aggregate digest. Keep SHAM original-state parity and distinguish endogenous TT key/candidate rewrite from direct policy manipulation. Search mechanism-aware engine modifications only after observing reproducible root contender survival effects in legally suitable development positions. Engine-time/nodes and opening-paired color-swapped Elo/survival need separate independent cohort. A source-independent M5 requires all literal UCI predictions in human-authored Git before FIRST and historical September/July M3-v2/M4 negatives unchanged.

**Status:** P14-P1 NATIVE_PATH_DIVERGENCE_PASS_SICILIAN; ROOT_STABLE; TT_SEE_NATURAL_MEDIATION_HOLD; INDEPENDENT_GENERALIZATION_UNTESTED; P15_ENGINE_STRENGTH_UNMEASURED. All commit author+committer `WhoSia`, Actions read-only, bot contributor prohibited.
