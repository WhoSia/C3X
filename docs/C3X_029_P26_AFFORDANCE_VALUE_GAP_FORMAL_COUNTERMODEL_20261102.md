# C3X 0.29-P26 — The Affordance–Value Gap: Formal Countermodel and Research Questions

Date: 2026-11-02. Status: MATHEMATICAL COUNTERMODEL, not chess-native empirical finding.

## 1. Separate predicates
For legal root action x, legal opponent replies R_x, own legal responses T_x(r), predefined binary plan predicate Q(x,r,t):
G_Q(x) = 1 iff for every r in R_x there exists t in T_x(r) with Q(x,r,t).
For a two-ply finite value model (same root-side utility scale):
V(x) = min over r in R_x of max over t in T_x(r) of U(x,r,t).
G_Q is a witness-existence statement. The result-value ordering V is a different statement. Without a *predeclared validated link* between Q and U, G_Q(a)=1, G_Q(b)=0 does not imply V(a)>V(b). Even a validated positive association is weaker than a universal implication.

## 2. Explicit finite countermodel
A has two opponent replies r1,r2, each exactly one player response t:
U(a,r1,t)=+0.10, Q(a,r1,t)=True;
U(a,r2,t)=-0.30, Q(a,r2,t)=True.
Thus G_Q(a)=1 and V(a)=-0.30.
B has two replies u1,u2, one response each:
U(b,u1,t)=+0.15, Q(b,u1,t)=False;
U(b,u2,t)=+0.05, Q(b,u2,t)=False.
Thus G_Q(b)=0 and V(b)=+0.05. Therefore a has a universally realizable declared plan but strictly worse minimax value. These are *invented abstract payoffs* witnessing formal non-implication, not real chess positions, evaluations or Stockfish outputs.

## 3. Stronger unresolved questions
- Construct validity: is Q a preselected strategic effect or a hindsight correlator of engine evaluations? What source of ground truth exists independently of Stockfish's root preference?
- Utility alignment: is plan achievement necessary, sufficient, or only contextually helpful for root value? Record each separately.
- Policy robustness: does the same own policy generalize across replies or does the existential witness permit different actions per opponent reply (legitimate contingent strategy)? What observation does the policy use?
- Counterfactual alignment: reply sets differ between a and b. Compare on each candidate's own legal reply domain, or preregister a valid opponent intention equivalence; never match bare UCI labels as if the resulting boards were identical.
- Finite-horizon risk: how does G_Q change with horizon H, reply sampling, and Stockfish depth? Universal coverage on an enumerated sampled reply set is NOT universal across all legal replies.
- Decision interpretation: a static Q-label may be shared by both candidates, while only one preserves a favorable *consequence* under intervention; conversely both preserve plan yet value differs. Explicitly abstain rather than posthoc search.
- Near-equal instability: if repeated calibrated utility differences change sign, can report verifiable planning geometry but not a stable preference explanation.
- Pragmatics: explanation performance should include claim truth, contrastiveness, novelty of plan content, game-disjoint transfer, abstention/coverage, compute cost and blind human decision-transfer; no metric weights fitted on heldout.

## 4. Pre-registered falsifier family
F1: affordance exists for A but better minimax consequence for B.
F2: affordance exists for both, stable preference for A — Q non-discriminative.
F3: affordance only for A but nearby opponent reply invalidates the planning claim in real legal game.
F4: preference changes sign across independently replicated search budgets — explanatory target unresolved.
F5: model abstains too frequently to match competitor coverage.
F6: compressed prose drops critical contingency versus machine-readable strategy; compare JSON plus text.

## 5. Next actual chess experiment
Reconstruct original complete game histories or recruit genuinely new source games, independently verify rule legality, seal two candidate sets (near-equal and >=75cp comparison), preregister Q and legal horizon, enumerate or explicitly bound response fans. Compare forecasted consequence truth with robust static concept and BinProp-style learned motifs on identical game-disjoint instances. No superiority claim until external replicated results.
