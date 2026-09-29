# C3X 0.7.0-G9.5-P11 — Bound-Signed Repeat-Key Move-Ordering Mediation Anatomy

## 1. Question

P10 established a bounded late-opening regularity: two prospectively frozen A0 archetypes within one shared skeleton repeatedly changed the root move after exact MOVE_ORDER_SEED removal. P11 does not rediscover or refit that skeleton.

The P11 question is narrower:

> Once a frozen repeat-key/same-move move-order seed is removed, where does the downstream search first reorganize, which visitation/cutoff changes are merely correlated with that reorganization, which coarse downstream class can itself reproduce the root transition, and how do the same witnesses behave under an actual bound-signed search patch?

## 2. Authority

P11 is a conditional mechanism follow-up. The inherited P10 positives contribute no new independent confirmatory vote. The primary P11 universe is all and only the 17 P10 ROOT_CHANGE records belonging to the two replicated A0 archetypes.

No new A0 atom, subgroup threshold, source filter, or outcome-driven archetype is allowed.

## 3. Exact target recovery

P10 intentionally did not publish raw TT keys. P11 therefore re-catalogues each pinned P10 world and recomputes the exact event address hash internally. The inherited event is accepted only when its P10 event_id is recovered exactly.

A nearby event may never substitute for a missing target.

## 4. Node-visit and cutoff anatomy

Each TT semantic event occurs at a search invocation carrying full-key, ply, depth, bound, move and window state. P11 uses the private full key only within one replay to count and align search-event visitation.

Published diagnostics contain only aggregated quantities:

- unique private-key visits;
- ply-1 unique-key visits;
- visits by semantic class, ply and depth band;
- cutoff count and first cutoff divergence;
- first exact trace divergence ordinal;
- multi-window revisits of the same private key as a bounded re-search/PVS proxy;
- PV divergence and root move transition.

This is not a complete engine call graph and the multi-window statistic is not asserted to be exact PVS instrumentation.

## 5. Three intervention arms

For each inherited witness:

1. **T_ONLY** removes the exact inherited MOVE_ORDER_SEED target.
2. **M_ONLY** keeps the target but removes one prospectively selected downstream P34-Q3 mediator class.
3. **T_PLUS_M** removes both.

The mediator candidate rule is frozen before execution: choose the first divergent downstream CUTOFF event; if none exists, the first divergent MOVE_ORDER_SEED event; otherwise the first divergent TT semantic event. The event is then quotient-mapped with the existing P34 Q3 map.

M_ONLY is intentionally coarse. A positive M_ONLY result therefore supports a bounded *mediator-class causal alignment*, not a formal natural indirect effect.

## 6. Mediation status

- **OBSERVED_PATH_DIVERGENCE** — downstream anatomy changes, but M_ONLY does not independently reproduce the T_ONLY root move.
- **MEDIATOR_CLASS_CAUSAL_ALIGNMENT** — M_ONLY independently reaches the T_ONLY root move and T_PLUS_M does not contradict it.
- **MEDIATOR_CLASS_INTERACTION_REDIRECT** — the mediator intervention creates a third root move, reverses the transition, or changes T_ONLY into another outcome.
- **NO_POST_TARGET_MEDIATOR_CANDIDATE** — the frozen rule finds no downstream candidate.

Trace divergence alone is never called mediation.

## 7. Actual developer patch

P11 adds one bounded behavioral patch to the same pinned upstream sources used by P34.

During the measurement search only, the patch suppresses MOVE_ORDER_SEED when all of the following hold:

- MAIN search;
- ply 1;
- depth 5–8;
- the same full TT key appeared previously in the measurement trace;
- its most recent prior occurrence carried the same TT move;
- the TT bound is LOWER, UPPER, or either according to runtime mode.

The compiled binary exposes four modes: NONE, LOWER, UPPER and BOTH.

NONE must be behaviorally transparent. The other modes are developer experiments, not playing-strength recommendations.

## 8. Patch regression court

The sealed seven-case P9/P10 engineering witness bank is replayed without changing case membership.

For each patch mode P11 distinguishes:

- SURVIVES_EXACTLY;
- EFFECT_DISAPPEARS;
- EFFECT_REDIRECTS;
- EVENT_ADDRESS_DRIFTS;
- BASELINE_DRIFT;
- CONTROL_BREAKS;
- NONCOMPARABLE.

A baseline move change is never silently treated as witness survival.

## 9. Cross-engine meaning

Same-position replication across Stockfish, Berserk and Ethereal is useful because implementation-specific and repeatedly exposed search sensitivity can be separated.

P11 still does not infer one implementation-independent hidden mechanism merely because two engines produce the same root transition or the same coarse mediator class.

## 10. Terminal developer surface

The terminal P11 output should let an engine developer answer, per witness:

> Which exact seed caused the root decision change, how soon did the search visitation and cutoff structure diverge, did one downstream quotient class independently reproduce that transition, and did a bounded repeat-key patch preserve, erase, redirect or destabilize the witness?

Raw TT keys are excluded from the public diagnostic.
