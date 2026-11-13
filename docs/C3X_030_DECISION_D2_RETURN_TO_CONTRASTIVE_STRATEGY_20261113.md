# C3X 0.30 — Decision D2 · Return to Contrastive Strategy Explanation

2026-11-13 KST. Research-priority revision within 0.30.

## Founding question

Given a position with two credible, nearly tied candidate moves, what small, checkable difference in their future opportunities explains why a player should prefer one, and under which opponent replies or evaluation settings does that preference disappear? The [C3X 1 archive](https://drive.google.com/open?id=1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf) starts with what a learner can learn from a small engine preference in positions without a standout tactical move.

[D1](C3X_030_DECISION_D1_NATIVE_CAUSALITY_FIRST_20261111.md) made native search causality the main line and gated future strategy evaluation on it. This decision supersedes that work order. The contrastive chess explanation leads. Native tracing serves measurement stability and scoped claims about Stockfish's internal computation. A chess claim supported by legal continuations can be tested independently. The label “this event caused Stockfish's choice” requires its own same-world controlled intervention. Prospective 0.29 cohort (7/8) and S4-H2 remain sealed.

## Executed exploratory audit of archived candidate contrasts

Compute the difference between the worst evaluated reply for A and the worst evaluated reply for B under each matched regime in [R26](C3X_029_P42_R26_POLICY_STRESS_SOURCE_RANKING_MIXED_CAUSAL_STRATEGIC_EVIDENCE_20261109.md). The two minima can come from different replies. A positive number favors A. Sahel A/B = e5f4/e5c3. Cerrado A/B = d1c2/e5f6. Full means all legal first replies. Generic and stress denote R25 and R26 selections. Union takes the lower of the two selected minima **separately for each candidate**. These are finite-search replay values in centipawns, with two adaptively selected game histories. This audit executed arithmetic on the reported values, with zero new engine calls or raw per-reply replays. The union uses extra branches and source cost.

| Game | Berserk evaluation | Full | Generic k3 | Stress k3 | Union |
| --- | --- | ---: | ---: | ---: | ---: |
| Sahel | d12 fixed own action | -6 | -1 | -11 | -1 |
| Sahel | d16 fixed own action | 2 | 4 | 13 | 4 |
| Sahel | d16 unrestricted own action | 2 | 3 | 3 | 3 |
| Cerrado | d12 fixed own action | 40 | 51 | 40 | 40 |
| Cerrado | d16 fixed own action | 29 | 43 | 29 | 29 |
| Cerrado | d16 unrestricted own action | -17 | -9 | -17 | -17 |

Sahel's full fixed-action preference changes sign from −6 to +2 cp with depth. At d16, stress sampling inflates the full contrast from +2 to +13 cp. This is a useful abstention example even though the d16 rank agrees. Cerrado's full comparison changes from +29 to −17 cp when own continuation is unrestricted at d16. The 46 cp shift in contrast reflects unequal improvement in the worst-reply values for the two candidates (+0 and +46 cp respectively). The aggregate archive does not locate the witness replies or identify a plan. Replaying the reply/action pairs can distinguish within-reply recovery from a change of which reply attains the minimum.

## First empirical experiment on the restored main line

1. Freeze new complete game histories and a deterministic game-level split before tuning. Select non-forcing pairs with a fixed source screening budget, a declared near-tie band, and a minimum stability check across two search budgets. Keep screened unstable pairs and record why the explainer abstains. Use Sahel and Cerrado as historical examples of failure, not confirmation.
2. For each pair, freeze one short strategic claim with an executable success predicate and explicit failure conditions before independent review. First hypothesis: two distinct defenses can deny the same route after B while A can reach the same target using different legal continuations. Example predicates include occupancy and retention of a target square, or a pawn break that meets prespecified material and king-safety bounds. Confirm strategic equivalence by predeclared board predicates rather than requiring the same SAN sequence. Preserve reply, planned continuation, legal repair, node counts, and witness line per candidate.
3. Compare static position-difference, best-PV-only, generic reply top-k, and the short plan-plus-witness explanation at matched source search budget and explanation length. Cross-check claimed exceptions with independently budgeted replay. Probe full first-reply coverage on a bounded audit subset. Use equal length and same engine-visible information for comparisons that test presentation alone.
4. Judge whether each explanation correctly predicts which new opponent replies preserve or kill the plan, when a different own action rescues the position, and whether the engine ranking is stable. Report abstention coverage and errors by game. For candidate mechanisms, run a same-position legal action comparison with a matched alternative and placebo plan label. A later learner test can measure transfer to an unshown defense rather than agreement with the preferred move.
5. Stop promoting an explanation when a legal reply falsifies its claimed scope, an equally short static/PV baseline predicts the same failures, or near-tie preference is unstable. Repeat only with a declared revised claim and fresh evaluation cases. Native TT investigation is triggered for instability diagnosis or explicit engine-mechanism claims.

Two claims are independently testable: a chess-level explanation can forecast strategy failure in new replies, and a native search event can influence engine root preference. A same-world experiment may eventually join them.
