# C3X 0.30/R37 — Pre-registered Third-Winner Referee Rescue (Development Only)

**Frozen before R37 referee execution on 2026-11-21.** The R30-017 event and the previously unjudged third winner were discovered in earlier native experiments. This is an **explicitly post-selection diagnostic**, not a new blind cohort or prospective success probability.

## Fixed chess-world object

- Inherited R30-017 board FEN: `5rk1/pp1bqppp/6r1/3pP3/3N4/2P1R3/PP2QRPP/6K1 w - - 25 36`.
- Three **fixed legal White choices**, in this order: original native recommendation `e2f3` (Qf3), intervention winner `e2d3` (Qd3), originally referee-nominated alternative `a2a3` (a3). Never choose candidates based on new referee scores.
- The full original PGN history is not included in this experiment; **board-FEN-only referee** cannot represent prior threefold repetition or all history-sensitive dynamics. Not an exact full-history strategy result.
- All **legally available immediate Black replies after each White candidate** are enumerated. No top-k filtering. Legal replies are defined before scoring, not selected by the referee result.

## Fixed referee and search

- Independent engine family: Berserk 14, pinned source `8ae895a6151695be4a50d4fb65b0c131659c513a`, network `berserk-9b84c340af7e.nn` SHA256 `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`.
- Python chess version `chess==1.11.2`. Berserk `Threads=1`, `Hash=16`, a fresh UCI new-game boundary for each leaf search. Binary SHA is recorded.
- For each **candidate + legal immediate Black reply**, search the resulting board with two fixed depths **10 and 12**; measure score from original White's point of view, actual nodes, completed depth and final PV; perform **two identical cold-history repeats**. Count *every* requested and actually completed search.
- No unequal calculation budget equality claimed: identical depths may consume different nodes. The referee is independent from the original Stockfish search but not an error-free strategy oracle.

## Endpoints and stop rules (before new scores)

1. For each candidate and depth, record Black's *lowest scored legal reply*, its value, all available replies, score type (cp/mate) and whether all comparisons actually completed to the expected depth.
2. If a response is terminal, incomplete, illegal, the network SHA wrong, an engine crashes, or any required output is missing, record **HOLD**, not an invented result. Do not silently remove an unfavorable reply.
3. A **finite local ordering** may be reported separately at each judge depth only if every reply of every candidate is successfully scored in comparable centipawn form. Reversal across depths is an explicit negative robustness outcome.
4. Two repeats must match in score/type, completed depth, nodes and PV for a deterministic replay PASS; retain mismatches and withhold deterministic claims.
5. Even a stable depth-10/depth-12 ranking is **a bounded board-only independent referee observation**, not a causal explanation for Stockfish's own R30-017 choice, not evidence of human comprehension, and not a universal statement about chess strength.

## Evidence custody and rights

Original R30 intervention remains [R33 cross-cohort derived audit](../docs/C3X_030_R33_SOURCE_PUBLIC_GAP_20261121.md), derived receipt `receipts/C3X_030_R33_cross_cohort_summary_20261121.json`; its originally checked ZIP is in [Drive](https://drive.google.com/file/d/1BMSvffPHCzNQXpSjpQlxD9BihJwn8neM/view) with SHA `b42d19601f98fb00ff00e03fb7881bff3bd93114dc9c7b3bcd5876263727449e`. Do not rewrite that file.

R37 outputs must remain a separate immutable artifact with exact source/network/binary/checksum metadata and the entire denominator. GitHub workflow is **read-only**; no `github-actions[bot]` commit. If a workflow fails before native scoring, label it an instrument failure rather than a chess-negative result. Test before promoting any independent-referee claim.

## Why run this before 0.31?

C3X 0.30's central gap is not merely whether event suppression changes a root bestmove but what that changed move means under legal responses. The R30-017 third winner lacked even the same independent reference surface as the original pair. Resolving that precise *missing third-candidate judgment* is a higher-information task than increasing anonymous TT event counts. It still cannot close human learning or native state mediation.
