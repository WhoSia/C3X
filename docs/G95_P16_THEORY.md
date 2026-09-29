# C3X 0.7.0-G9.5-P16 — Minimal Distinguishing Chess Structure

## Origin

P15 earned replicated authority for a weaker but important link:

`pair-local board relation edit → exact-search susceptibility change`.

It did **not** replicate the complete:

`board structure → search mediator → near-equal pair preference`

chain. P16 spends exactly one authorized continuation budget on that gap.

## Scientific object

P16 does not search for a prettier chess concept. It searches for an **inclusion-minimal intervention-defined structural support** for a FULL_BRIDGE.

For a frozen unordered pair `{A,B}`, a quiet one-piece relocation induces changes in whether that piece attacks:
- A.from
- A.to
- B.from
- B.to

Every changed Boolean relation is encoded as a directed atom such as `A_TO_GAIN` or `B_FROM_LOSS`, then re-expressed per engine as `PREFERRED_*` or `DISPREFERRED_*`.

Square identity and the verbal meaning of the relation are deliberately downstream.

## Prospective chain

For the same moved piece and the same Chebyshev displacement distance, P16 freezes:

`TARGET → proper SUBSET → SHAM`

Two chain families are allowed:

- **COMPOSITE_DELETION_CHAIN** — TARGET has at least two relation atoms; SUBSET is a strict nonempty subset, preferring deletion of exactly one atom; SHAM has no changed pair-local atom.
- **ATOMIC_CHAIN** — TARGET has one atom and SHAM is its only proper subset.

At most one best composite and one best atomic chain are frozen per position.

This yields a bounded minimality claim: **minimal inside the declared chain family**, not globally minimal over all possible legal chess interventions.

## Outcome separation

Before edited-board native choices or exact-event removal outcomes are opened:

1. select 36 fresh P16 positions, 18 per July/August source, excluding every recoverable P1–P15 candidate/decoy hash;
2. freeze unordered near-equal pairs using the unchanged P15 qualification;
3. generate relation-atom chains mechanically;
4. require TARGET/SUBSET/SHAM to preserve legality and pair marginality under at least two active engines;
5. freeze up to two chains per position.

Only then does the search factorial run.

## Search mediator

P16 does not change the search hypothesis.

It inherits:
- MAIN `MOVE_ORDER_SEED`
- ply 1
- depth 5–8
- repeated full key
- same most-recent TT move
- LOWER / UPPER
- anchor = the original-board baseline-dispreferred candidate

Addresses are reconstructed privately and independently on every board. No cross-board or cross-engine native-address identity is assumed.

## FULL_BRIDGE

For a bound, TARGET earns FULL_BRIDGE only when:
1. original native and TARGET native choose opposite frozen pair members;
2. the eligible semantic event fires on both;
3. T_ONLY collapses original and TARGET to the same frozen pair member;
4. SHAM does not reproduce the bridge;
5. no defining cell escapes to a third move.

A FULL_BRIDGE is **MINIMAL_FULL_BRIDGE** only if the declared proper SUBSET also fails to reproduce the bridge.

## Structural equivalence

The primary signature is:

`MOVED_SIDE_ROLE | SORTED_ENGINE_RELATIVE_ATOM_SET | BOUND | MINIMAL_FULL_BRIDGE`.

It deliberately quotients:
- physical square names;
- physical edit ID;
- position ID;
- engine ID.

A structural-equivalence family replicates only with at least:
- 3 witnesses;
- 2 engines;
- 2 positions;
- both sources;
- 2 physically distinct edits.

A weaker FULL_BRIDGE replication can be recognized at the coarse preferred/dispreferred-dominance × bound level, but it does not earn minimal structural-equivalence authority.

## Causal explanation certificate

Every minimal bridge produces `c3x-causal-contrast-certificate-v1`.

The certificate stores:
- the actual candidate pair;
- original/TARGET/SUBSET/SHAM boards;
- physical board edits;
- normalized minimal atom signature;
- native and T_ONLY root decisions;
- subset and SHAM falsifiers;
- replication membership;
- authority ceiling.

The PGN implementation track may consume a replicated certificate as `C3X_CAUSAL_CONTRAST`.

The certificate has **no human strategic concept label** at P16. “Space”, “initiative”, “prophylaxis”, “piece activity” and similar semantic projections require a later prospective concept-as-partition test.

## Research OS projection

P16 follows the current Research OS lightweight runtime:
- Goal fidelity: the result must return to the original move-vs-move question.
- Frontier compression: relation atoms/minimal chains are useful only if they reduce the remaining mediation uncertainty.
- Authority separation: susceptibility, full mediation, structural equivalence and natural-language usefulness are separate authorities.
- Failure-preserving memory: local bridges and failed minimality remain explicit.
- World-contact minimality: fresh P16 worlds are acquired because P15 cannot establish the stronger authority from existing evidence without retrospective reuse.

No new Research OS operator is introduced. Research OS 2.4.4 remains frozen.

## Stop rule

One fresh run. If the frozen edit language cannot support or replicate FULL_BRIDGE, close the ceiling. Do not widen the intervention family, thresholds or search taxonomy after outcomes.
