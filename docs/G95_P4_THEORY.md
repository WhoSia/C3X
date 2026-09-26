# C3X 0.7.0-G9.5-P4 — Rare-Event Causal-Support Constitution

## Explanandum lock

P3 failed before field authority could be earned: only 1 of 192 fresh exact-event removals produced ROOT_CHANGE. P4 therefore does not add another context feature. It asks whether the experimental design can obtain enough causal-positive support *without consulting the target* to make field formation and transport testing meaningful.

The target remains exactly the P1–P3 target:

```
Y(r) = 1{ bestmove(remove exact event r) != bestmove(parent) }.
```

The fiber remains F0 and context availability remains `EVENT_PREFIX_ONLY`.

## Design separation

P4 separates six objects that must not be collapsed.

1. **Known-positive instrument controls.** Three already-closed P32 exact-event witnesses are replayed with the inherited P34/P3 executable chain. They calibrate the intervention apparatus only and contribute zero records to fresh support.
2. **Outcome-blind event sampling.** Candidate events are selected from the unablated parent trace using only semantic class, near-root ply, TT-move presence, prefix key reuse, and a frozen deterministic tie-break.
3. **Fresh support/power gate.** Up to 576 discovery interventions are available: 12 fresh positions × 3 engines × 16 events. The field court requires at least 480 fired records, 6 ROOT_CHANGE positives, 240 negatives, at least one positive per engine, and positives in at least two source regimes.
4. **No feature expansion.** Field formation may choose only among the five schema families already frozen in P3. P4 cannot rescue support failure by inventing a new coordinate.
5. **Held-out target firewall.** Held-out profiles are materialized and scoped before target artifacts are downloaded.
6. **Public authority firewall.** A discovery field may be useful internally, but the public service may emit `CERTIFIED_*` only after zero-contradiction held-out transport. Otherwise it returns `ABSTAIN_UNCERTIFIED_FIELD`.

## Outcome-blind mechanism strata

The 16-event quota is:

- 4 near-root `CUTOFF` events;
- 4 near-root `MOVE_ORDER_SEED` events with a TT move;
- 4 near-root `EVAL_REUSE` / `TT_VALUE_AS_EVAL` events;
- 2 prefix same-key reuse events;
- 2 balanced near-root fallback events.

Events may satisfy multiple predicates, but exact-address duplicates are suppressed. Shortfalls are filled deterministically from the remaining eligible ply≤1 parent-trace events. Raw TT keys are used only transiently for equality and are never emitted by the sampler.

These strata are not learned from P3 labels. They are motivated by P32's independently closed exact-event witnesses, including near-root cutoff, move-order, evaluation-reuse, and same-key interaction cases.

## Fresh world constitution

Discovery uses four fixed source regimes from pinned `official-stockfish/books` commit `65815cc...`:

- `noob_3moves.epd`
- `noob_5moves.epd`
- `closedpos.epd`
- `UHO_4060_v1.epd`

Held-out transport uses four distinct regimes:

- `noob_4moves.epd`
- `Drawkiller_balanced_big.epd`
- `popularpos_lichess_v3.epd`
- `UHO_4060_v4.epd`

Every recoverable P1/P2/P3 candidate hash is excluded before engine execution. Positions are selected by SHA-256(FEN), not engine outcome.

## Power constitution

For actual fired discovery count (n), sensitivity prevalence (p_*=0.02), and required positives (k=6), P4 computes

```
Power(n) = P[Binomial(n, p*) >= k].
```

The minimum fired-record gate is (n=480), where the frozen calculation is approximately 0.9183. At the planned maximum (n=576), it is approximately 0.9737. Thus support failure after the gate is meaningfully different from P3's underpowered 192-record realization; the threshold is never lowered after target opening.

## Positive-control interpretation

A positive-control PASS says that the current executable chain can still reproduce three already-certified P32 root-changing interventions. It does **not** say that a fresh P4 world must contain ROOT_CHANGE, and its records never enter the P4 field. A control failure stops discovery because a null fresh result would then be instrumentally ambiguous.

## Field and transport

P4 reuses, unchanged, `P2_BASE`, `TT_LOCAL`, `TEMPORAL_LOCAL`, `KEY_REUSE_TOPOLOGY`, and `MINIMAL_HYBRID`. Discovery admissibility still requires zero mixed target cells plus compression and cross-position/cross-engine reuse. Held-out transport requires target-blind scope followed by exact agreement for every covered profile.

Unseen cells are abstentions. Covered disagreements are contradictions. Neither can be silently converted into the other.

## Public explanation service

The deterministic service has no LLM dependency. It exposes only certificate state, field identity, provenance, and a bounded limitation. An MCP, agent, or LLM may later wrap this service, but cannot promote an abstention, erase a contradiction, or create scientific authority.

## Claim ceiling

P4 can establish that a frozen outcome-blind design recovered enough exact-event support for a bounded field, and it can test that field on fresh held-out regimes. It cannot establish universal engine causation, human strategy, cognition, intent, or population prevalence.
