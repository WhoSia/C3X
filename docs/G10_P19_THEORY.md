# C3X G10-P19 — Engine-relative preference-stability law experiment

## Scientific object

P19 does not rank engine strength. It studies the binary support response of different search systems to the same frozen counterfactual preference intervention.

For a jointly-active chain row x and engine e, define S_e(x) in {0,1}. The frozen primary order candidate is:

S_stockfish19 ⊆ S_berserk ⊆ S_ethereal.

This is a set-inclusion claim over intervention survival, not an Elo ordering, quality ranking, or source-code homology claim.

## Falsification semantics

The adjacent relations are tested directly.

- Stockfish=1, Berserk=0 is an exact witness against Stockfish⊆Berserk.
- Berserk=1, Ethereal=0 is an exact witness against Berserk⊆Ethereal.

Any eligible witness kills the corresponding strict inclusion. A low violation rate may be reported afterward, but cannot rescue the strict law.

Nonvacuity gates require jointly-active support, antecedent-positive rows, and both-positive rows. Inactive engine cells are abstentions (NA), never failures.

## Frozen Ethereal candidate

The P18 candidate is carried forward without literal search:

grammar_complexity <= 1 AND phase != REDUCED.

P19 calls this an empirical sufficient candidate only. Replication requires the P18-style source-wise precision threshold and minimum support under fresh sources. It is not logical implication and not an engine-internal mechanistic explanation.

## Mechanism interpretation

A confirmed order would establish an engine-relative susceptibility regularity: under the frozen intervention grammar, the set of worlds preserving preference in one engine is nested inside the next. It would still not identify why the nesting occurs internally.

The next mechanistic layer would require intervention on engine-internal search state (TT use, pruning/reduction decisions, aspiration/window trajectories, candidate ordering or equivalent provenance) and mediation analysis conditioned on the same chess-world perturbation.

## Explanation track

Human-readable claims must compile from the evidence graph. Each sentence must point to:

1. the tested relation/rule,
2. fresh source identity,
3. positive witness rows,
4. exact counterexample rows,
5. authority level.

Free-form LLM prose cannot upgrade evidence.

## Publication boundary

A paper-level claim becomes defensible only after:

- prospective fresh-world confirmation or falsification,
- source-separated reporting,
- exact witness ledger,
- nonvacuity checks,
- engine/version identity freeze,
- reproducible tensor reconstruction,
- no post-outcome threshold/rule refit.

P18 is development discovery. P19 is confirmation. A later engine-internal mediation stage would be mechanism identification.
