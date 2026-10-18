# C3X 0.26 P0-E — Theory-First Search–Strategy Discrimination

**Status:** preregistration draft / diagnostic data only; no new engine court. Existing C3X 0.26 formal title unchanged.

## Historical continuity
C3X 0.1 asked for a contrastive chess reason between near-equal legal moves; 0.2–0.2.4 investigated affordance, persistence, latent decision factors and transfer, with negative external results; 0.3 developed designed disagreements. Later metrology and 0.25 P10–P12 constrained the authority of engine protocol and PV observations. Preserve original names and negative cases.

## Theory refinement
Search ranking, a legally different continuation, a strategic differentiating reason, and the algorithm's causal reliance on it are four distinct claims. Define rival legal moves a,b, finite predicate vocabulary V, horizon H, response assumptions P, observation protocol O, and intervention set T before unsealing new search results. An inclusion-minimal discriminating reason R⊆V is *relative* to V/H/P/O/T; its existence and uniqueness are not presumed. For competing models h_i,h_j, discrimination requires at least one feasible intervention t with observably different predictions under fixed tolerance. If indistinguishable, report UNIDENTIFIED, not an invented strategy.

FEN4 convergence can hide halfmove or move-number differences; FEN6 equality does not capture repetitions. PV/MultiPV2 samples do not enumerate all opponent responses.

## P11/P0-D/P0-E descriptive audit
Original P11 SHA256 `18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2`; 144 process rows, 72 repeat pairs, 36 branch/evaluator conditions. Opponent top reply changed d17→d19 in 15/36; within those 9 retained identical reported top-two candidate set and 6 replaced one visible candidate. New *read-only* P0-E exposure audit reports descriptive ratio of sums of recorded two MultiPV node fields, nominal d19/d17: median 2.0685 for changed-top n15, 1.9917 for stable-top n21; fixed top-two set n20 median 2.0923, one-shared n16 median 1.9985. These **are not equal-budget searches**, independent position counts or a causal node mediation model. MultiPV field sums are *only a proxy* and may have engine-specific accounting.

## Competing preregistration hypotheses
H_search: root eligibility/order/TT/budget determines ranking shifts while chess predicate contrasts remain approximately invariant.
H_chess: independently verifiable legal opportunity or constraint differences persist across engine/protocol changes without assuming they caused search's choice.
H_mixed: both operate and interact (do not assert mediation without identification).
H_null: features do not generalize or beat score/PV-only control on unseen cases.

Development: 42 Classical Bf8/Bc5; 43 NNUE Re8/Qf5. Controls: 47 NNUE transient d18 reversal; 99 Classical d20 LOCKED tie. Development-only, P10-outcome-selected. No population/generalization verdict.

## Next decision: WSL not automatic
First freeze source-independent chess predicate vocabulary: legal checks, viable pawn advances, opponent forcing replies, defended/undefended targets, task-limited mobility at H=1/2 and declared P. Use `python-chess` to create read-only comparison table and explicit counterexample tests from P11; do **not** extract 'why' from mere metric differences. Only authorize a new WSL Stockfish experimental batch after a pre-outcome design yields different predictions for rival accounts and uses separate heldouts. Otherwise abstain and refine theory. Keep 0.25 research active and original GitHub bot-contribution-zero governance.