# C3X 0.7.0-G9.5-P8 — Scale-Normalized Chess Search-State Prototyping

## 1. Return to the engineering object

P7 answered a useful question early: an exact digest of the whole observed prefix is too identity-preserving to function as a reusable chess-search state. Across 480 fresh target-blind profiles, Q0–Q3 each behaved as one-record fingerprints.

P8 does **not** respond by adding a deeper graph refinement or another hand-made local bucket. It changes the engineering object.

The P8 object is a **retrieval substrate for causal chess-engine analogues**:

> Given one addressed TT semantic-use event in one fresh root search, can a target-blind scale-normalized descriptor retrieve previous exact-intervention situations that are similar in board/search provenance and informative about root-move change?

A useful result should help an engine developer answer questions such as:

- Have we seen this kind of TT/search situation before?
- In those analogous situations, did suppressing the addressed use change the root move?
- Did the analogue occur in another engine or another position?
- What root-move and legal-PV contrasts resulted?
- Is the present query outside the validated analogue region?

The terminal product is therefore a diagnostic index, not an ontology catalogue.

## 2. Harvest backflow

P8 imports four bounded donors.

1. **State as compression claim.** A state is useful only if it forgets history while retaining the distinction needed downstream. P7 was history laundering in the opposite direction: its state retained almost the entire episode identity.
2. **Predictive state.** State need not reconstruct the hidden world; it may be defined by the downstream responses it supports.
3. **Behavioral similarity / bisimulation metric.** Exact equality is stronger than engineering similarity. A task-relevant distance can support aggregation and nearest-neighbor use.
4. **Associative retrieval / local experts.** A prototype can be useful without being a universal law if it reliably routes a query toward relevant prior cases.

These are design donors only. C3X authority still comes from chess-engine intervention.

## 3. Estimand shift

P6/P7 sought state partitions that could support a deterministic ROOT_CHANGE law. P8 asks a weaker but more useful engineering question:

[
	ext{Does target-blind search similarity retrieve causally analogous root-move-change cases?}
]

The primary evaluation is therefore ranking/retrieval, not collision-free classification.

A P8 success is **not** “this prototype causes ROOT_CHANGE.” It is:

> queries that actually change root move under exact intervention receive systematically higher prototype risk and more positive cross-position/cross-engine analogues than queries that do not.

## 4. What P8 deliberately forgets

The descriptor excludes:

- exact prefix length as an identity;
- exact node/edge colour multiplicities;
- raw TT keys;
- engine identity;
- source identity;
- sampling stratum;
- P7 Q-state IDs;
- any counterfactual outcome.

It retains only coarse scale plus normalized chess/search provenance.

## 5. Frozen descriptor

Each event receives five blocks.

### Board block
Side to move, check, phase, legal-move bucket, material balance, castling and halfmove bucket.

### Current-event block
Search scope, TT semantic class, ply/depth buckets, TT bound, alpha-beta window relation, TT-move presence and payload bucket.

### Normalized provenance-rate block
Class shares, qsearch/current-scope share, current-class share, unique-key ratio, repeated-key-event share, current-key share, normalized same-key/same-class gaps, depth percentile and same-ply share.

Raw keys may be used only transiently to compute equality/recurrence statistics and are never emitted.

### Temporal-shape block
The prefix is divided by relative position into four equal segments. Each segment records only dominant semantic class family, dominant scope and repeated-key share bucket. Absolute segment lengths are discarded.

### Coarse-scale block
The only absolute episode-scale atom is a four-bin prefix-size bucket. Its total distance weight is only 0.05.

## 6. Distance

For each block, distance is the categorical mismatch fraction. The total is a frozen weighted sum:

- board 0.15
- current event 0.30
- normalized provenance 0.30
- temporal shape 0.20
- coarse scale 0.05.

No weights are fitted.

## 7. Prototype cover before labels

Train profiles are collected first with no ROOT_CHANGE access.

For radius (r), a deterministic farthest-first cover is constructed:

1. first prototype = lexicographically first stable profile;
2. repeatedly add the point whose nearest-prototype distance is largest;
3. stop when every profile is within (r);
4. assign each profile to its nearest prototype, lexical tie-break.

The radius ladder is frozen at 0.08, 0.12, 0.16, 0.20, 0.24, 0.28.

The **smallest** radius passing all target-blind compression/reuse gates is frozen. If none passes, P8 closes without opening train outcomes.

This is the P8 equivalent of refusing P7's episode fingerprints before causal labels can tempt a rescue.

## 8. Causal annotation after freeze

Only after a prototype index is frozen may train exact-event targets be joined.

For each prototype:

- labelled support;
- ROOT_CHANGE count;
- Laplace-smoothed ROOT_CHANGE frequency;
- positive and negative exemplar IDs;
- cross-position/cross-engine positive exemplars.

Mixed prototypes are allowed. They are not “impure states”; they are local retrieval neighborhoods.

## 9. Fresh selection

No descriptor, weight, radius, prototype, threshold or membership is refit.

Each fresh selection query receives:

- nearest frozen prototype and distance;
- coverage/abstention;
- prototype risk score;
- whether positive train analogues exist;
- whether positive analogues cross engine/position.

The retrieval gate requires coverage plus:

- AUROC ≥ 0.60;
- average-precision lift ≥ 2× base rate;
- positive-analogue hit rate ≥ 0.40;
- cross-engine positive-analogue hit rate ≥ 0.20;
- cross-position positive-analogue hit rate ≥ 0.30.

This makes “similar” pay rent in actual root-move-change retrieval.

## 10. Untouched transport

Transport targets remain unopened until:

1. train prototype is frozen target-blind;
2. train causal annotation exists;
3. fresh selection passes with no refit;
4. target-blind untouched transport scope has enough prototype coverage.

Transport then evaluates the same retrieval rule on unseen worlds.

## 11. Developer-grade diagnostic

A transport-validated P8 service may say:

- nearest search prototype;
- normalized provenance similarity;
- historical exact-intervention support;
- smoothed ROOT_CHANGE rate;
- positive analogues from another engine/position;
- example baseline→counterfactual root moves and legal PV divergences.

It may **not** say that ROOT_CHANGE is certified for the new event.

This is deliberately a debugging/explanation tool rather than a causal oracle.

## 12. Chess-first success criterion

P8 is successful only if a developer-facing query becomes more informative:

> “Show me prior TT/search situations like this one, including exact interventions that actually changed the chosen move.”

If the prototype geometry is elegant but does not retrieve fresh root-move-change cases, P8 fails.

## 13. Stop rule

P8 ends when one of these occurs:

- no target-blind radius passes reusable-prototype gates → engineering HOLD;
- train support insufficient → support HOLD;
- fresh selection retrieval fails → retrieval HOLD;
- untouched scope cannot support transport → scope HOLD without target opening;
- untouched retrieval validates → validated analogue retrieval.

No post-target distance learning, radius growth, new feature block or threshold relaxation is allowed.
