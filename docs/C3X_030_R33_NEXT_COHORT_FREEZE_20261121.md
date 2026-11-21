# Post-R34 held-out cohort proposal — native explanation transport, not just TT sensitivity

**Status: proposal only; NOT the completed R34 protocol or an independent result.** The original R33 TWIC1671 native gate panel and its R34 equal-depth follow-up were completed separately. All R29/R30/R32, TWIC1671 R33 and R34 diagnosis positions are now development data. This note proposes a *future* held-out cohort beyond them.

## The falsifiable next-cohort question

Does a signed, causal Stockfish search-state explanation (native trace + interventions) identify failures and conditions of move recommendations in previously unseen PGNs better than the same-budget publicly visible depth/score/PV, *without increasing unjustified certainty about chess merit*? A separate controlled human comparison asks whether adding that evidence to a held-fixed board reply explanation improves responses to novel legal opponent moves.

## Selection protocol before any native mask outcomes

- Identify a new, public and properly licensed PGN source *not* from TWIC 1663/1664 or R32's already exposed R29-031, freeze the exact archive SHA and legal move histories; avoid matching transposed board keys and repeat games.
- Stratify by initial source score gap: close (5–25cp), medium (26–100cp), large (>100cp), depth reversal, and unclassified/bounded; **no forced case classification if source bounds prevent an exact comparison**. Sample every fifth eligible game up to 48 positions using the SHA-sealed seed; reserve positions with no eligible event in the denominator.
- Use Stockfish16 NNUE, Threads=1, fixed Hash and 32k nodes, same complete history. Instrumentation-disabled original and patched builds must agree on public output, and target read matching must be exact (full key, attempt, stack, window, depth, alpha/beta, candidate). Run sham, one-read mask, restore, and repeat; never merge TT fields from different executions into a supposedly simultaneous table.
- The primary mechanism intervention is one source-observed TT hint/value read in the original final-producer attempt. If none, nominate the latest earlier attempt on the actual alternative branch. Freeze root choice criteria, opponent reply, and score-bound gates before running a mask. If no target, record `not selected`, not `not affected`.

## Predetermined outcomes

1. Direct child returned and changed (with separate unobservable/cutoff state).
2. Root candidate update at **same alpha and depth**; if different, incomparable.
3. Final producing attempt and physical event id.
4. Final bestmove and complete score/bound/PV trajectory; metadata separately.
5. Native event mediation evidence: exact write-read and inherited state; if missing, `total effect only`.
6. Independent board outcome for **every actual root winner** including third candidates, across at least two referee depths and multiple legal replies. Independent judge must run after candidate set freezes.
7. Human outcome from separate protocol, not from synthetic responses; never derive human efficacy from deterministic engine replay.

## Gate to advance

Promote a causal search-to-strategy explanation only where the same history has: physical source event; sham-mask-restore with final choice or planned reply change; identifiable transport or explicitly bounded uncertainty; an independent legal reply/plan witness; and transfer beyond that very PGN. Otherwise retain a negative, partial or mechanistic-only label. No version bump without a held-out set and independent human-transfer evidence.
