# R23 — Trace the result Stockfish actually emits

[Protocol](C3X_030_R23_EXPLAINABLE_STOCKFISH_PROTOCOL_20261117.md) · [engine and patch identity](../receipts/C3X_030_R23_NATIVE_BUILD_20261117.json).

Across two exposed game histories, ten configured scenarios match between clean upstream Stockfish 16, trace build with tracing disabled, and trace build with tracing enabled. There are four fresh runs per scenario, including a traced repeat. The comparisons retain all public depth, bound, score, PV, node, hash and bestmove fields after normalizing NPS and wall-clock time. Both exact and upper/lower reports were verified. Searches ran single-threaded with one PV and fixed depth or nodes. The results make no timing-control or multi-thread equivalence claim.

Instrumented runs contain **277 root attempts, 3,205 completed candidate returns and 108 public scores**, 104 from in-window candidate values and four with source bounds. All ten final moves map to a native producer in a completed root attempt. Six public records take their score from a different attempt than the output's latest attempt. Two records also differ in the displayed depth and the producer's nominal iteration.

| Case, 24k nodes | Full legal menu, default NNUE | Prior two-move menu, default NNUE | Full-menu source receipt |
| --- | --- | --- | --- |
| R21 1.2 | Bd2, +88 cp | h4 | Output depth 11, producing attempt 24 at iteration 10 |
| R22 2.3 | Rfe1, +35 cp upper bound | Rfe1 | Output depth 11, producer attempt 36 within iteration 11 |

At R21 attempt 24, a3 returns 280 below incoming alpha 284. Bd2 returns 289 inside [284, 323] and becomes the lead. In the same call Qd2 and h4 return 112 and 169 under current alpha 289 and neither updates the lead. Native candidate values can be searched with different effective depths and windows. In the R22 case attempt 36 retained Rfe1 with a raw return of 114. It published the alpha threshold 115 as +35 cp upper bound. The next attempt was cut off by the node budget in both cases.

[Read the verified Korean Bd2 and Rfe1 cards](../product/README.md). The observations that Nd1 attacks the rook and that …Rhe8 defends e5 are legally replayed chess statements. The root event trace does not prove that an individual board feature caused a particular neural evaluation.
