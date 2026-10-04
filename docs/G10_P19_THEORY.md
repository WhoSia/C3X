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

## Ordered-threshold rival

P19 elevates the P18 nesting from an empirical ordering into a falsifiable representation hypothesis.

Let d(x) be a scalar susceptibility difficulty attached to an intervention/world x, and let each engine have a fixed robustness threshold r_e. The one-dimensional ordered-threshold rival is

S_e(x) = 1[d(x) <= r_e],

with

r_stockfish19 <= r_berserk <= r_ethereal.

This representation necessarily implies the frozen nesting relation. The proof is immediate: if d(x) <= r_stockfish19 then d(x) <= r_berserk, and if d(x) <= r_berserk then d(x) <= r_ethereal.

Therefore an eligible Stockfish=1/Berserk=0 or Berserk=1/Ethereal=0 witness does more than perturb a rate ordering: it proves that no deterministic scalar difficulty plus globally ordered engine-threshold representation can reproduce the observed exact response tensor.

This is structurally analogous to deterministic Guttman-style nested binary response patterns and invariant ordering in nonparametric item-response theory. The analogy is methodological, not ontological: chess engines are not psychometric items, and P19 does not import psychometric latent-variable semantics.

Manski-style monotone-response reasoning is a second useful donor: monotonicity is treated as a substantive shape restriction whose empirical content comes from what it excludes, not as a smoothing preference. P19 is stricter because the primary law is exact finite-world inclusion.

### Rival outcomes

1. **Exact nesting survives.** A one-dimensional ordered susceptibility representation remains observationally admissible on the fresh ecology.
2. **Exact nesting fails sparsely.** The strict scalar representation is falsified. Violation mass may be reported descriptively but cannot rescue H1.
3. **Adjacent orders fail in different worlds.** This is evidence for engine×world interaction structure that cannot be compressed to one global robustness coordinate.
4. **Nesting is underpowered.** No representation conclusion is authorized.

A future P20 may then ask for a minimal multidimensional mediator basis rather than merely fitting a softer ranking.

## Frozen Ethereal candidate

The P18 candidate is carried forward without literal search:

grammar_complexity <= 1 AND phase != REDUCED.

P19 calls this an empirical sufficient candidate only. Replication requires the P18-style source-wise precision threshold and minimum support under fresh sources. It is not logical implication and not an engine-internal mechanistic explanation.

Under the ordered-threshold rival, H2 can be read only as a candidate low-difficulty region for Ethereal. It does not define d(x), and it cannot be used to refit H1.

## Fresh-event world lane

TWIC 1665/1666 remains a waiting replication lane, not a prerequisite for primary P19 closure.

P19 also freezes a completed-event lane using the official Lichess broadcast PGNs for:

- FIDE Candidates 2026;
- 46th FIDE Chess Olympiad Samarkand 2026.

Lichess is not a new provider for C3X, so this lane does **not** claim provider independence. Its freshness claim is narrower and auditable:

- event identities were repo-unseen before the source amendment;
- H1/H2 and all primary thresholds were frozen first;
- every recoverable historical C3X candidate/FEN hash is excluded;
- duplicate exact FENs across the two event arms are excluded;
- source selection is engine-outcome blind;
- only later engine-resolved counterfactual outcomes may vote.

The scientific transport axis is therefore event ecology / world composition under a shared provider, not provider transport.

## Mechanism interpretation

A confirmed order would establish an engine-relative susceptibility regularity: under the frozen intervention grammar, the set of worlds preserving preference in one engine is nested inside the next. It would still not identify why the nesting occurs internally.

The next mechanistic layer would require intervention on engine-internal search state (TT use, pruning/reduction decisions, aspiration/window trajectories, candidate ordering or equivalent provenance) and mediation analysis conditioned on the same chess-world perturbation.

If the scalar ordered-threshold rival is falsified, that next layer becomes sharper: search-state instrumentation must explain the inversion witnesses rather than an average survival-rate difference.

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

## Literature donors, not authority

- Manski, C. F. (1997), *Monotone Treatment Response*, Econometrica 65(6): 1311–1334. Used only as a donor for treating monotonicity as a falsifiable shape restriction.
- Mokken / Guttman scaling literature on invariant item ordering and nested binary-response patterns. Used only as a structural analogy for the ordered-threshold rival; no psychometric interpretation is transferred to chess engines.
