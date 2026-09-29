# C3X 0.7.0-G9.5-P10 — Late-Opening Move-Ordering Causal Anatomy

## 1. P9 found the hotspot; P10 dissects it

P9 completed a fresh four-phase intervention map and found one operational developer hotspot: late opening. Nine of 288 late-opening exact-event replays changed the root move, and all nine positive interventions were MOVE_ORDER_SEED events.

P10 does not re-rank phases and does not treat those nine cases as fresh evidence.

It asks two narrower engineering questions.

1. On **new** late-opening positions, do ROOT_CHANGE MOVE_ORDER_SEED events share a prospectively defined search-lineage structure across engines, positions and monthly sources?
2. Can the seven P9 regression witnesses be replayed exactly on the original binaries so that they become a trustworthy baseline manifest for future patches?

## 2. Two lanes, two authorities

### Fresh anatomy lane
January–March 2026 Lichess broadcast worlds are fresh to P9. All causal claims in P10 come from this lane.

### P9 regression seed lane
The seven P9 cases are known positives. They may not vote in P10 fresh science. They are used only to prove that the regression harness can reproduce the exact baseline and counterfactual transitions that P9 sealed.

A future patch may later be compared against this manifest. P10 does not fabricate a future patch.

## 3. Fresh late-opening corpus

For each checksum-pinned January, February and March broadcast file, P10 inspects exactly the first 1,024 games.

Eligible positions are restricted to plies 14–21 and must be:
- standard legal chess;
- nonterminal;
- not currently in check;
- 18–48 legal moves;
- absolute material imbalance no greater than three pawns.

All recoverable P1–P9 FEN hashes are excluded before admission.

Three positions per source are selected by deterministic target-blind ordering, yielding nine positions and 27 engine×position worlds.

## 4. Focused event sampling

P10 does not sample all TT semantic classes.

Eligible events are baseline MOVE_ORDER_SEED uses at ply 0 or 1 with a nonzero TT move.

To ensure that recurrence is observable without selecting by outcome, the sampler prospectively allocates:
- 8 FIRST_KEY events;
- 12 REPEAT_KEY events;
- 4 remaining eligible events.

Ties are exact-address lexical order.

## 5. Primary lineage archetype A0

P10 intentionally avoids another large learned representation.

Every candidate event receives one fixed coarse A0 archetype from information available at or before that event:

- MAIN or QSEARCH;
- ply 0 or 1;
- depth band;
- TT bound category;
- whether this key appeared earlier in the baseline prefix;
- if repeated, whether the previous same-key use carried the same TT move.

Raw TT keys never leave the within-engine lineage computation.

Thus two engines can share an A0 archetype without pretending that their TT key identities are comparable.

## 6. Diagnostic lineage A1

A1 adds:
- same-key count;
- normalized previous same-key gap bucket;
- same-key depth direction;
- previous same-class gap;
- immediately previous semantic class/scope.

A1 is diagnostic only. It cannot rescue A0 if the prospectively frozen replication rule fails.

## 7. Counterfactual trace anatomy

For every fired exact intervention, P10 also compares baseline and counterfactual search traces with the existing C3X lineage engine.

This records:
- matched events;
- vanished events;
- emergent events;
- first trace divergence.

This is post-target anatomy. It may explain *how the search path reorganized* after blocking the event, but it may not redefine the pre-event A0 archetype.

## 8. Replication rule

Fresh support must first pass independently.

Then an A0 archetype is called a **replicated MOVE_ORDER lineage archetype** only if its ROOT_CHANGE events include:
- at least 4 positive exact events;
- at least 2 engines;
- at least 2 positions;
- at least 2 fresh monthly sources.

No ranking or threshold tuning follows the result.

## 9. Why same-position cross-engine replication matters

P9 already observed one late-opening position that was sensitive in multiple engines. P10 broadens the question on fresh positions.

Same-position cross-engine replication is especially useful to developers because it distinguishes:
- one implementation's idiosyncratic search path;
- a chess/search situation that repeatedly exposes move-order dependence across implementations.

It still does not establish a universal implementation-independent cause.

## 10. Baseline regression replay

P10 takes the seven P9 regression witnesses and their matched controls as a frozen engineering seed bank.

For each witness:
1. recover the P9 cell/FEN and exact event address;
2. run the original pinned engine baseline;
3. remove exactly the P9 positive event;
4. require the exact recorded root-move transition;
5. replay the matched control when available and require no root-move change.

The output is a manifest that a future patched binary can consume unchanged.

This establishes **harness reproducibility**, not patch persistence.

## 11. Developer-facing output

A P10 diagnostic should answer:

> In this fresh late-opening search, which move-order event changed the root decision, what prior same-key lineage did it belong to, how did the search trace diverge afterward, and have comparable structures appeared in other engines or positions?

For the P9 seed bank it should additionally answer:

> Does this engine build still reproduce the exact regression witness and its matched control?

## 12. Stop rule

P10 is deliberately finite.

- fresh support failure → close;
- fresh support pass but no A0 replication → close anatomy hold;
- A0 replication → publish the replicated lineage anatomy;
- baseline P9 seed replay is reported independently and cannot rescue fresh science.

P10 ends after anatomy + regression harness. No new representation family is authorized.
