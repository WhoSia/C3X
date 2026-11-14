# C3X 0.30 S4-L/R6 — Native and Forced Root Gaps

2026-11-14 KST. R4 exposed development positions only. No holdout access. [Historical synthesis](C3X_HISTORY_AND_EXPLANATION_TRANSPORT_20261114.md).

## Native root receipts

Reanalyze both R4 trace copies. For each rectangle and candidate, require a unique strictly in-window value at the same root iteration, adjusted depth and candidate-specific window across four cells. Two candidates must be in the same root invocation within each cell. This matches observed context fields; root ordering and deeper state may still differ across cells. Both archive copies reproduce the same 75 contrasts. Italian ply10 provides zero admissible gaps. Italian ply8 provides three nonzero contrasts, 25, 44, 19 internal units, all for a3 versus d4 at iteration/depth 1. These are overlapping rectangles, not independent results. London ply8 has 9 zero contrasts. The five remaining cases have identical donor TT/history bytes, so their zero contrasts are controls without state separation.

## Fixed-depth forced-root experiment

Use R4's exact binary (3766b594a274e83bda1b2b1a8f67747b2f26724e6a64e388e659fb00c1fd12cb). Three exploratory cases selected because R4 donor blocks actually differed. Four candidates each fixed from prior native winners, the intervention target or a native witness. No whole-legal-root claim. Recreate the R4 donors and verify archived natural receipts, make fresh sham recipients, transplant both blocks, then issue go depth 8 searchmoves MOVE. The 108 forced results are all non-bound depth-8 cp reports. 234 searches including prep, 2006215 reported nodes per pass. The second pass reproduced all normalized results. Fixed depth, unequal node usage. A forced search removes normal root competition.

| Case | Nonzero gap rectangles / measured | Largest absolute contrast in cp | Sham-anchor top-set intersection on 4 interior cells |
| --- | ---: | ---: | ---: |
| Italian ply10 | 54/54 | 71 | 3/4 |
| Italian ply8 | 54/54 | 91 | 3/4 |
| London ply8 | 50/54 | 35 | 4/4 |

Each number is a contrast on candidate-pair score gaps, computed as g11 - g12 - g21 + g22. Rectangles and candidates overlap. Italian ply10 b4−h3 yields [-8, +8, +26, -29] for sham/second by sham/second, contrast -71 cp. Anchor prediction `Q(t,sham)+Q(sham,h)-Q(sham,sham)` has some top-set intersection in 10/12 cells, including ties. This is retrospective and selected. London second/second illustrates scope: forced top is Ne5 while joint R4 chooses Nd2. R5's additive representation of observed choice labels remains valid; measured forced gaps are a stronger, different observable.

Next link an interaction witness to a normal-root candidate at a deeper matched search site and precommit predictions on independently selected full game histories. Reuse PV, Cui-style reply trees and an independent evaluator before claiming strategic value.

[Native audit](../harness/c3x_030_s4l_r6_native_gap_audit.py) · [Forced runner](../harness/c3x_030_s4l_r6_forced_probe.py) · [Gap and forecast summary](../harness/c3x_030_s4l_r6_gap_summary.py) · [Raw UCI and replay](https://drive.google.com/file/d/1OrEUFKXHP_0PuhPm2ccKHQUs6Z5w53KC/view). ZIP SHA256 6cf04ba6e8b12c15cf920ad774de9551acaa00d31f9abbd9e669c6318dca710c. R4 development protocol and input results are linked from the [R4 report](C3X_030_S4L_R4_CROSSED_SEARCH_STATE_20261114.md).
