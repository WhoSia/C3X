# C3X 0.31 — Formal Name Proposal and Successor Constitution (NOT YET ACTIVATED)

**Proposal date:** 2026-11-21. **Origin:** C3X 0.30 R7/R29–R37; C3X 1 founding question; 0.29 strategy and NNUE line. **Status:** PROPOSED_NAME_AND_PRIMITIVE_QUESTION; not a scientific PASS and not an issued 0.31 stage without an explicit successor decision.

## Proposed formal name

**C3X 0.31 — Intervention-Stable Decision-State Abstraction: Minimal Search-Memory Causality, Robust Chess-Plan Transport & Human Explanation Validity**

한국어: **C3X 0.31 — 개입에 안정적인 의사결정 상태의 추상화: 최소 탐색·기억 인과성, 체스 계획의 강건한 전이와 인간 설명의 타당성**

The essential change is not an extra NNUE detector or a larger Stockfish logger. The experimental object changes from **which source events were observed to change a bounded engine search?** (0.30) to **what smallest state-level explanation retains the relevant root-choice counterfactuals across admissible interventions and legal opponent-response worlds?** (0.31).

## Primitive scientific question

Given a fully legal history `h`, exact board `s`, source-engine/runtime `E`, candidate menu `A`, budget `B`, current search state `sigma` and a previously fixed intervention family `I`, can we construct an inspectable reduced representation `phi(sigma; s,h,E,A,B)` that is sufficient to predict:

1. the conditional *engine* preference between two near-equal legal moves, including when a third candidate emerges;
2. which physically executed source intervention changes that preference through which tested search-state mediator;
3. the independent *chess* counterfactual statements that remain supported after legal adversarial replies; and
4. the additional learner value of showing admitted causal evidence rather than a public PV-only alternative?

These four are distinct estimands, not an assumed single mechanism.

## First formal candidate — context-relative interventional state equivalence

Let `c=(s,h,E,A,B)` be a **fixed, provenance-complete context**. Let `Sigma(c)` be the admissible native runtime states reached by actual chess-legal histories and source-logged transition checkpoints. Let `J` be a frozen set of feasible state interventions (real TT gate masks, bounded TT-depth/value/bound restores, history/order controls, valid shams, and no-contact controls), rather than arbitrary modifications to unreachable board states.

For an observable vector `O_c(sigma,j)`, distinguish coordinates:
- `O_root`: final bestmove, bound-labeled scores, full root-candidate competition and actual completed work;
- `O_future`: pre-registered *independent* legal reply predicates/finite-depth referee values, with abstention where incomplete;
- `O_human`: participant-level transfer outcome, never derived from Stockfish alone.

A *tentative* equivalence relation `sigma ~_{c,J,epsilon} sigma'` is licensed only when for every pre-registered `j in J`, the relevant `O_root` choice contrast agrees and numerical comparisons meet the pre-stated tolerance/coverage rule, with all missing contacts coded unknown. If a state abstraction `phi` maps two snapshots to the same cell but a held-out admissible intervention yields different root choices, that abstraction is **falsified for this context class**.

This is a testable **finite, context-relative predictive relation**; do not call it a universal bisimulation or a complete Stockfish internal semantics. Eventual semantic transport to `O_future` and `O_human` requires distinct measured gates.

## Why 0.30 motivates this, and what it does *not* prove

- R7: eligible candidate menus changed *shared candidate winners*, so a move's fixed context-free score cannot generally stand in for the executed finite-budget decision.
- R31/R32: the same child PV return can coexist with a different final recommendation after depth, aspiration, futility/null and nested state effects. A scalar `return value` is not always a sufficient state.
- R33 source/public audit: 15 changed direct native child returns were hidden by identical public depth-score-bound-PV and final recommendation; two local leader update flips did not change final choice.
- R33/R34 fixed-depth new games: 11 node-capped changes selected post-outcome, 8 survived originally completed fixed-depth checks; a depth counter does not uniquely fix search work.
- R35: two **correlated arms in one game** reached the same h3 local update loss and Qxc7 retry from different upstream events, while TT/history/budget mediator remained unidentified.
- R37: the third-winner independent referee is **a post-selected FEN-only rescue** of one previously unjudged winner, not a whole-history causal or human result, regardless of numerical outcome.

These facts reject naive candidates for `phi`; they do not yet construct or validate a new minimal sufficient representation.

## Scientific designs and falsifiers

| Study | Competing explanations | Decisive measurement |
| --- | --- | --- |
| M1 — state mechanism rescue | TT value/depth/bound vs history/order vs remaining search-budget state | Same-prefix checkpoint + single-family restore vs orthogonal sham, identical legal history and actual contact; child-to-ancestor/root identity; crossover rescue and failures |
| M2 — intervention-stable compression | public score/PV; local event-only; TT-only; full trace; proposed reduced `phi` | Pre-chosen game-disjoint contexts and intervention family; held-out root-choice prediction accuracy, abstention/coverage, cost and counterexamples |
| M3 — adversarial chess semantics | PV-only; multi-reply plan; causal-state evidence + same independent reply evidence | Actual chosen pairs **and emerging third moves**, two depths, legal reply census, independent engine, equal evidence/compute accounting; never equate finite-depth bound with ground truth |
| M4 — human transfer | R31 A/B/C/D explanations matched on common content and panel extent | Randomized subject-level held-out new-reply threat+plan endpoint, blinded scoring, uncertainty, chess-skill strata and rights/consent |

**Stop/falsify:** If pre-specified local state transplants cannot rescue root contrasts even when the source event is physically contacted, reject that mediator family. If a public-only or simpler state baseline matches `phi` at equal cost and coverage, do not claim architectural improvement. If a legal opponent reply defeats the asserted plan, narrow or withdraw the claim. If the matched native panel does not improve transfer in a properly powered trial, report a null result; a successful source trace is not a learner benefit.

## Historical distinctions and novelty pressure

C3X already has a G9.5 context-indexed `c3x-field` classifier and 0.29 proof-carrying contingent explanation candidates. **Do not relabel those as newly invented in 0.31.** The proposed new test is an executed *source-state sufficiency and interventional transport* comparison with an explicit small-state compression objective, then independently verified legal opponent-response semantics and pedagogical value. Previously implemented SARFA, Cui-style trees, RAVEL, causal abstractions and concept evidence are method donors, not automatic novelty. Check each exact baseline and original paper before publishing a novelty claim.

The ambition is that the causal state of a deterministic search algorithm can be described through **small, falsifiable, human-interpretable contrasts** without reconstructing every visited node. The nearest counterexamples may be that no small state suffices or that the chess-usable plan has no detectable causal connection to that source state. Those are successful discriminating scientific outcomes, not excuses to create another version.

## Carry-forward from 0.30

- **Retain:** authentic source-gate intervention receipts, exact source identity, two-track provenance firewall, negative source/public witnesses, menu-dependence evidence, replay and finite-referee protocols, counterfactual explanation product.
- **HOLD:** exact intermediate TT/history mediation in R35 and related cases; generalizable strategy value of root flips; full-history third-candidate independent judging; NNUE representation→root causation; ethically and statistically adequate human-transfer outcomes.
- **Do not retroactively rename:** all original 0.30 R1–R37 stages and all earlier failed/negative experiments remain immutable.
- **Version boundary:** 0.30 scientific research phase can be closed with these open obligations transferred. This formal name is a proposal, not an automatic activation of C3X 0.31 or certification of its planned experiments.

**Founding constraint:** explain why this *real near-equal chess move*, rather than a nearby legitimate alternative, was selected — and whether that distinction teaches humans something true about possible future play. See [Two-Track Constitution](C3X_TWO_TRACK_CONSTITUTION.md) and [current Research OS original question audit](https://app.notion.com/p/41bef561cf928116a75cebbd4f735dd7).
