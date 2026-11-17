# R20 D1 — One TT hit changes the early value of d4

[Protocol](C3X_030_R20_D1_PAIRED_MASK_PROTOCOL_20261117.md) · [frozen hit](../frozen/C3X_030_R20_D1_FIRST_HIT_20261117.json) · [raw runs](https://drive.google.com/file/d/1HlDio9F50PkZpRtd71tMt35hZpa6MVGD/view).

| Arm | First nominated probe | Child return | Immediate root edge at iteration 2, window [412, 454] | Last public report | Best move |
| --- | --- | --- | --- | --- | --- |
| Sham | hit | normal, −267 | +267, below alpha | depth 9, +27 cp | d4 |
| Mask one hit | miss | qsearch, −433 | +433, inside window | depth 8, upper bound +22 cp | d4 |

At the first actual hit, mask ordinal zero in epoch one logs 1 → 0. The focal call in each arm links through its own parent and child IDs to the PV edge and the root candidate update for native move 731 (d2d4). The sign reversal agrees exactly with both returned values. Source Step 10 enters qsearch at depth −1 in the mask run with no local TT move. The qsearch receipt's own TT-hit field is 1, consistent with a mask on one main-search signal. The root's internal values use Stockfish's native units. Their difference is distinct from the UCI score scale.

Last-score comparisons must preserve the bound. Even at a shared public depth, values can be transient. At depth 7 the completed UCI lines read +27 and +66 cp. Both fresh-process repetitions per arm give identical stderr and normalized search output. The 12,000-node requests ended at 12,004 and 12,011 nodes. The immediate value path is demonstrated within the two recorded runs. A change in the chosen move, transmission past this iteration, and transport to sealed games remain open.
