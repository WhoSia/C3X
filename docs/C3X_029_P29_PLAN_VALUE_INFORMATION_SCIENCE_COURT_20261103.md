# C3X 0.29-P29 — From Plan Feasibility to Value-Bearing Information

Date: 2026-11-03 (researcher chronology). Status: formal finite semantics, local synthetic unit tests, source literature review. **No new native Stockfish or chess-pair performance experiment.**

## Scientific question
Does a preregistered prospective plan predicate Q add information about source-independent chess outcomes beyond equally budgeted static geometry, fixed engine scores, and conventional explanation baselines? If so, is the statement truthfully contrastive about two viable near-equal root candidates, rather than a post-hoc just-so story?

## Objects and distinctions
For root player and candidate a, R_a contains its own (potentially different from b) opponent legal replies. T_a(r) contains root player legal continuations. The target is the full original-state history, not a four-field FEN shortcut. U(a,r,t) is a single-root-perspective value evaluated under a frozen horizon. Q(a,r,t) is a predetermined measurable plan effect, not a model-generated after-the-fact description.

- Plan feasibility G_Q(a)=1 iff forall r in R_a exists t in T_a(r) with Q true.
- Unrestricted finite value V(a)=min_r max_t U(a,r,t).
- Q-constrained value V_Q(a)=min_r max_{t:Q} U(a,r,t), **only defined** when Q has at least one legal witness per reply.
- Plan opportunity cost C_Q(a)=V(a)-V_Q(a)>=0. A plan may be always possible yet costly. This is a finite minimax/constraint definition, not a novel general theorem.
- Under the strong separation condition V_Q(a)>V(b), V(a)>=V_Q(a)>V(b) **in the same finite utility model**. This is a stronger target than feasibility alone; it does not prove Stockfish actually based its internal selection on Q.

## Formal demonstration (synthetic; NOT chess-native)
A: r1 -> +0.1,Q true; r2 -> -0.3,Q true. B: u1 -> +0.15,Q false; u2 -> +0.05,Q false. Hence G_Q(A)=1, G_Q(B)=0 but V(A)=-0.3<V(B)=+0.05. Other synthetic case: each reply gives a non-Q safe action of value 3/2, Q-constrained actions values -1/0; then V=2,V_Q=-1,C_Q=3. Showing Q is possible does not prove it is wise.

## Information estimand
Choose an independently adjudicated heldout outcome Y and freeze BEFORE seeing it:
- p_plan(Y=1 | available source facts and planned consequences) from the plan system;
- p_static(Y=1 | same original source / engine budget) from strong static/baseline system.
With identical cases and source-game disjointness, game-macro paired Brier improvement is
  Delta_Brier = avg_game avg_case[(y-p_static)^2-(y-p_plan)^2].
Positive score favors plan forecasts **for this declared outcome**, not necessarily epistemic explanation accuracy or causal mediation. Report selective coverage, cases per game, confidence/uncertainty, calibration, factual claim rate, gold idea recall and cost separately. A model that abstains too often cannot win by looking only at covered easy cases. Strong baseline includes original score/PV, typed concept and machine-readable plan JSON; do not use a deliberately weak opponent.

## Attack matrix and stopping
1. Q globally possible in both candidates (real P28 20/20 vs 20/20 for immediate Nf3): correct but non-discriminating.
2. Q possible only for candidate a yet that candidate loses finite value or ranking (P26 mathematical counterexample): refutes raw availability -> utility.
3. Q-internal action selection has positive opportunity cost: feasibility may hurt play.
4. Shared labels but different consequence: discriminate only if verified out-of-sample and truly candidate-specific.
5. Rank reversals across root evaluation budget (0.2 historical): declare marginal direction unresolved and do not attribute it to a Q.
6. Identical UCI replies across candidate boards need not mean matching states; enumerate each R_a.
7. Human performance after explanation may degrade from persuasive-but-false certainty or increased overreliance; human transfer requires separate blinded outcome.

## Concrete P29 artifacts
- tools/c3x_029_p29_value_probe.py and test: finite action/Q/utility minimax cost.
- tools/c3x_029_p29_value_certificate.py and test: sufficient *finite* inequality separation.
- tools/c3x_029_p29_incremental_information.py and test: matched heldout game-macro Brier gain.
- 17 independent local Python unittest cases run with synthetic fixtures and pass in author's container before GitHub transport. Repository/CI execution separately requires monitoring; actual chess oracle never run in this unit.

## Literature court (connected Google Drive actual text selectively inspected)
1. Sutton, Precup & Singh (1999), *Between MDPs and Semi-MDPs*, Drive 1_AcKvt5GR8cYYAARM8GYdmQ8ekitJjd9: options combine initiation set, internal policy and termination; possibility of initiating an option is not its option-value. Transfer to two-player adversarial chess is OUR extension, not quoted theorem.
2. Sutton & Barto (2015 in-progress 2nd ed draft), Drive 1wufPP-uxpcqstgTkmUrctVS8feEhXj_D: decisions alter future options; long-term reward/return is distinct from action availability; the archived copy is an unfinished draft, not final 2018 edition.
3. Rao & Georgeff (1995), Drive 1sC-81Q948DnnIH_qjohZOw_zaofRJpFV: BDI separates option generation, deliberation, intention commitment and execution under bounded resources. Does not prove value of a specific chess plan.
4. Russell & Wefald (1991), Drive 1SAvlhQSvPEXTV4QxmsnrCZtzWk-x9ZWT: computations themselves can be selected by expected value net time/resource cost; C3X should evaluate search cost when gaining certainty on marginal pairs.
5. Woodward (2003), Drive 1kKd2k4oFoca7XzBEPz9S6gK1wIeZ-8lE: intervention and invariance as explanatory criteria; do not infer decision causation merely from a chess plan predicate.
6. Tal (2017), Drive 1P5guGX-EJBfjr0fKigoSyTOghk5q8Ff2: calibration requires modeling the process and handling uncertainty; engine centipawn is not a direct observed causal reason.
7. Kirsh & Maglio (1994), Drive 1G5fgEClza862ik1YuKMrc5DOhqv_Rd0S: epistemic versus pragmatic actions; the value of a move may include information for later judgment. Any specific chess application needs testing.
8. Nersessian (2008), Drive 168Yv277pBhy--iQrNjhMWbYcFhVx3_KR: scientific model-based reasoning and external representation; educational usefulness of explanatory certificates must be established empirically.
9. Buçinca, Malaya & Gajos (2021), Drive 1zhxm2rQiepYaI_p-Y6wc7AUD8OqarABQ: overreliance on AI and cognitive forcing in human decisions; fluent explanations can distort rather than improve human decision-making.
10. Geiger et al. (2025), Drive 1dkkczKfLgmHL8YPwKWrKunEdCbAel6hK: high- vs low-level causal abstraction needs faithful intervention correspondence; chess semantic predicates cannot be conflated with engine-source inner mechanism.
These were **targeted text reads of sections**, not comprehensive chapter-by-chapter audited interpretations.

## HOLD
Actual original complete-source legal histories, live identical-budget Stockfish candidate data, presealed Q, independently judged source-game-disjoint outcomes, real BinProp/CCC competitor implementations, blind human learning assessments. No improvement claim.
