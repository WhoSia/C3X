# R23 — A short search can return a different move on the same board

[Pre-replay stopping freeze](../receipts/C3X_030_R23_STOP_BUDGET_FREEZE_20261117.json). On R21's full legal root, the first observed NNUE leader shift was Bd2 to Rf1. At root attempt 3, Bd2 had provisional native value 214 and Rf1 (candidate 15) returned 358, crossing beta 226. The retry used a wider window [202, 370]. Its Rf1 value 358 landed inside the window and was written to the published report. Bd2 did not retake the lead in that retry.

| Node request | Nodes searched | Final move | Exact score producer |
| --- | ---: | --- | --- |
| 77 | 77 | Bd2 | Attempt 2, native value 214, +65 cp |
| 139 | 139 | Rf1 | Attempt 4, native value 358, +109 cp |

Both arms return the predicted move with an untouched upstream Stockfish, the tracing build, and a fresh repeat of the latter. For each arm the stopped subsequent attempt leaves the prior completed score producer in place. This identifies the effect of continuing this engine search while holding the board, legal menu and evaluator fixed. It does not test the independent merits of the moves or an intervention on a specific NNUE feature. The long 24k run later returned to Bd2.
