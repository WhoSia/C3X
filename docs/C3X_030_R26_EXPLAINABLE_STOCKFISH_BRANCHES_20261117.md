# C3X 0.30 R26 — Explainable Stockfish after the equal-score reply fork

Explain the engine's move against a credible alternative. A complete result lets a player follow which responses made the engine prefer the move, test which board-level resources are shared or reply-specific, and see which conclusions survive a change of search context. R25 connects the published reply to an actual native decision and demonstrates ordering sensitivity under local interventions. The contribution of the board resource to Qxe2's margin remains open.

| Research question | Minimal experiment | Result that changes the explanation |
| --- | --- | --- |
| Where did Be7 enter the default search? | Trace the exact TT read at call 31 back to a write of the same entry, retaining key, bounds, age and effective depth. Reproduce the read path with the R25 sham before any new mutation. | A matching write gives a testable transmission path. A different writer means the visible depth-14 PV update and later hint came through distinct events. |
| Does b4 help explain why Qxe2 beats a named alternative? | Choose a legal runner-up before intervention from the full root search. After each root, fix the contrast reply, then compare constrained and unconstrained searches at the relevant future White turn. Report within-root changes and their difference on matched budgets. Use a quiet legal control and track immediate versus forced-delay cases. | If removing b4 changes the root margin beyond the quiet control across several replies, report the scope. If the margin persists or changes sign across replies, describe b4 as a resource in the checked lines and report the residual. |
| How often do equal root reports support one shared plan? | Use the remaining exact-native R24 fork cases as a fixed exploratory cohort. For the first four unseen forks, label a board-verifiable claim before looking any deeper. Record whether divergent PVs share that claim, differ in timing, or present different resources. | Repeated moves with changing geometry call for narrower labels. Similar resources across different moves support comparing response-contingent plans rather than string prefixes. Reserve any prevalence estimate for an independent cohort. |

For the b4 experiment record the root, exact position and move history, reply, affected White turn, untouched legal alternatives, signed native returns, terminal bound and budget. A legal closer-to-root loss or gain from the constrained future action characterizes that restriction of the search. Describing an NNUE feature as an internal cause requires additional feature-level evidence.

Advance the three arms together until each has an outcome that can change the player-facing explanation. The next integrated example should answer both why the engine preferred one root move and how far the explanation carries across plausible replies.

## Cross-source R26 panel

The [component panel](C3X_030_R26_TT_COMPONENT_PANEL_RESULTS_20261117.md)
extends these branches across 88 positions and multiple score margins.
A fixed-depth h5 case connects an exact-score reply fork to an independently
checked shared resource. A separate Nd7/a4 case tests a named root contrast
against every legal first reply. Its global read masks provide a target
for a later local TT intervention, whose result would decide mediation.
