# C3X 0.29-P40/R4 — Value-Bearing Plan Regret Under Diverse Legal Counter-Replies

2026-11-05 KST. PRE-OUTCOME THEORY/CONTRACT UNIT. No real C3X strategic predictor or independent chess referee has been validated here. This is the flagship hard question, NOT a conveniently substitutable new mobility or checkmate proxy.

## Fixed question and quantifiers

For exact legal original board s, candidate move m, and each legal opponent first response r, a plan P(s,m,r) is a SUBSET of our legal continuations after r, determined by a predeclared typed chess-semantic predicate BEFORE observing the adjudicator's result. Evaluate each own continuation u using a separately generated, source-pinned chess-value judge J at a preregistered horizon, giving interval-valued score V_J(s,m,r,u) from the original mover's POV. The unrestricted best action is max over all legal u. The best plan-constrained action is max over u belonging to P. Define per-response opportunity cost Regret_P(m,r) = max_legal u V_J(...) - max_plan u V_J(...). The plan's worst-case cost is max over legal opponent r of Regret_P(m,r). This is the target of an explanatory plan-invariance claim.

## Crucial anti-triviality and validity rules

Reject P=all legal u over all r: it yields tautological zero regret. Require at least one genuinely selective branch and publish selection fraction |P|/|Legal| for EACH r. P empty on a reply is a plan-availability failure, not zero cost. If evaluating a FIXED SUBSET of opponent responses for feasibility, label only SAMPLED regret, never a universal guarantee; a response set selected after outcome viewing invalidates inference.

If per-action scores are exact or bounded intervals, propagate lower and upper bounds: max of lower endpoints and max of upper endpoints separately for unrestricted and plan-restricted alternatives, then interval-subtract. A LOW-regret assertion is certified only if its entire upper bound is at or below the predeclared threshold. HIGH-regret only if its lower bound strictly exceeds threshold. Otherwise ABSTAIN/HOLD. Original P37 96k alpha-beta outputs had upper/lower flags; never silently point-impute.

Score J is not necessarily chess truth. In future experiments, use at least one genuinely independent engine-family judge after complete source/build/node-budget verification; a second judge and disagreement analysis is preferable. Historical P38 Ethereal v12.75 depth/node mismatch remains STOP, cannot revive its invalid results. Chess rules independently verify legality, terminal outcomes and typed plan predicates; a bounded engine still estimates positional quality rather than proving it.

## Concrete scientific test with fatal criteria

On fresh game/event-disjoint, source-hash-frozen near-equal candidate pairs with candidate-identity and near-margin stability across multiple budgets, let each rival output a plan predicate P plus response-conditioned predicted future value/regret intervals BEFORE opening J labels. Compare: strong Stockfish 24k score+PV with a same-budget response-aware extension, a foil-aware simple semantic plan JSON of matched selectivity, C3X source-grounded plan generator, and abstention/no-plan. Equalize engine nodes, legal continuations enumerated, CPU, number of plans and response claims. Preserve every heldout pair including no valid stable near ties and any judge disagreement.

**Claim ceilings:** this structural regret formula is not new by itself, nor a finished paper, and cannot imply NNUE feature-to-root mediation. One test is plan-output predictive validity, a separate test is specific NNUE/search causal path tracing under source-native interventions. If C3X does not beat strong PV and simple conditionals on independently scored response-conditional value after costs, FAIL the explanation-performance hypothesis rather than publishing a weakened proxy.

## This turn's executable gate

Implement only an interval-aware, subset-checked plan-regret certificate with synthetic proof cases and provenance flags. Report synthetic test PASS distinct from original chess-value evidence, which remains HOLD.