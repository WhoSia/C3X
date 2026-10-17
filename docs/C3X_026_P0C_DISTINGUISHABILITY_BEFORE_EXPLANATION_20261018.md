# C3X 0.26 — P0-C: Distinguishability Before Explanation

Status: theoretical proposal / development, **not** a certified strategic explanation.

## Core distinction
C3X 0.26's task is to find what legally actionable continuation property distinguishes rival chess choices, whether that property is causal for a particular search result, and whether it helps humans on unseen positions. These are *three different propositions*. A greater distance between board states is not chess superiority, and identical FEN6 positions cannot prove repetition-history identity.

## Candidate formalism
For a position s, root a, horizon H, response-policy family P, let R_H(s,a,P) denote legally attainable future state/action pairs. A proposed representation Phi should be defined by *observable, falsifiable chess predicates* (e.g. forcing check, legal pawn break, ability to restrain an opposing threat), with declared opponent assumptions and time horizon. Its contrast between a and b is not a value difference and has no unconditional ranking interpretation.

A reason r is discriminating only relative to a stated vocabulary V, opponent family P, horizon H and comparison cohort. It must differ between the response classes of a and b, survive declared negative controls, and have a legal intervention or hard counterexample that would make it fail. Minimality is *conditional*: deleting a component from a proposed explanation set should remove discriminatory power under a preregistered test.

## Rival accounts and falsifiers
- H_search: protocol-specific budget, root eligibility, move ordering or TT path accounts for ranking shifts even when chess-affordance contrast does not change.
- H_affordance: legal continuation constraints robust across engine configurations distinguish candidate choices, even if engine selection did not rely on them.
- H_mixed: both the search procedure and chess futures interact.
- H_null: candidate explanations add no generalizable decision/human utility beyond PV, score-only or unassisted baselines.

Do not force H_search and H_affordance to be mutually exclusive. Search-algorithm cause, game-theoretic chess justification and pedagogical usefulness require separate evidence.

## Actual source observations
P10 development selection had 53 strict FULL/LOCKED reported-cp margin reversals, 7 persistent same-rival pairs over depths 18 and 20. P11 source: 9 selected positions, 144 process runs, 72 cold-repeat pairs. P0 WSL python-chess legally replayed 144 recorded rows; source JSON SHA256 18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2. P0 within-two-reply board+turn/FEN4/FEN6 convergence counts 13/72, 13/72, 8/72; between-root 4/36 each. These are finite PV-sample comparisons, not equivalent strategies. The unaltered P11 data show opponent top-reply change across depths17→19 in 15/36 branch/evaluator combinations.

## Experiment gates
1. **P0-C1 (descriptive)** source hash, complete process and repeat denominators, side-to-move and FEN fields; do not call features 'affordances'.
2. **P0-C2 (actionable)** compute rule-complete legal tactical and mobility features under declared opponent policies, from python-chess; differentiate attacked squares from *safe* opportunities, define length/budget matched comparisons.
3. **P0-C3 (causal)** preregister rival accounts and legal counterfactuals on original positions; require both P10 negative controls 47 and 99. Consider interventions where a strategic predicate changes while other predeclared factors remain near-fixed; do not falsely assume such matched board interventions always exist.
4. **P0-C4 (generalization)** untouched event/game-disjoint cohorts and cross-engine protocols with no post-outcome re-fit; audit historic PGN lineage collisions.
5. **P0-C5 (human)** blinded transfer comparing causal-contrast explanations against score/PV-only baselines and no-explanation, with question-specific gains and abstentions.

## Decision
New version 0.26 is OPEN based on a changed central question; it is not a positive empirical verdict. P10/P11/P12 remain active and historical C3X 0.25 title/records remain unchanged. Preserve failures. GitHub commits WhoSia author+committer, Actions read-only, no new branch.
