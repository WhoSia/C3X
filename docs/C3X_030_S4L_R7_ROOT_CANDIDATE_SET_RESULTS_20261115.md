# C3X 0.30 S4-L/R7 — Root candidate eligibility changes shared-move preference

2026-11-15 KST. [Protocol](C3X_030_S4L_R7_ROOT_CANDIDATE_SET_PROTOCOL_20261115.md) · [Research lineage](C3X_030_S4L_R7_RESEARCH_LINEAGE_20261115.md). Development only. The R4 overlay rebuilt byte-identically at SHA-256 `3766b594a274e83bda1b2b1a8f67747b2f26724e6a64e388e659fb00c1fd12cb` from the pinned Stockfish 16 source. One thread, 16 MiB TT, classical evaluation. Recipients replayed the R4 sham first search before state transfer. All 27 unrestricted 12k end receipts and 108 depth-8 singleton receipts matched their archives. Per pass, 782 searches and 8,338,070 reported nodes in the primary grid and 274 searches and 2,740,120 reported nodes in the postselected London screen, including preparation. Both repeated in fresh processes with byte-identical normalized JSON. Depth and requested node budget are separate stopping rules. No holdout positions or independent judge searches.

## Shared-winner reversals

For nested menus S ⊂ T, record a reversal if the winner in T remains available in S and the smaller menu chooses another move. The selected large-menu winner was in the four-move menu in every cell reported below. With strict menu-invariant scores and a fixed global tie order, the T winner must also win S. Observed reversals reject that choice model for these cells. Menu-dependent tie resolution, changed ordering, bounds, search depth and branch work are possible sources of divergence.

| Development case | Four versus all, depth 8 | Four versus all, 12k requested nodes |
| --- | ---: | ---: |
| Italian ply10 | 5/9 | 6/9 |
| Italian ply8 | 4/9 | 3/9 |
| London ply8 | 3/9 | 2/9 |
| Total | 12/27 | 11/27 |

Cells share positions and donors. These are descriptive frequencies for exposed cases. A strict pairwise score model can still fit a fixed-menu donor grid while failing this nested-menu test.

## London ply8, second-only TT and second-only history

| Menu | Depth 8 | 12k requested nodes |
| --- | --- | --- |
| Nd2 and Ne5 | Ne5, +17 cp | Ne5, +14 cp upper bound at reported depth 9 |
| R6 four moves | Ne5, +13 cp | Ne5, +13 cp at reported depth 11 |
| All 36 legal moves | Nd2, +4 cp | Nd2, 0 cp upper bound at reported depth 9 |

Singletons at depth 8 give Ne5 +17 and Nd2 +4 cp. Pair plus c3 and pair plus Bxd6 each select Ne5 at both limits. In the all-menu depth-8 trace, the final aspiration attempt first scores Ne5 at 0 internal units with depth 5, then Nd2 at +14 after a reduced search and a PV re-search. In the four-move trace, Ne5 scores +44 at depth 6 and Nd2's reduced call returns +44 at depth 4, exactly alpha, so Nd2 does not replace it. The pair trace reaches Ne5 +59, then Nd2 +44 below alpha. These are within-run source observations with differing windows and adjusted depths across arms. They identify a candidate for surgical mediation testing.

A follow-up starts from each of two backgrounds: add each of the other 32 legal candidates individually to the R6 four, or delete each of 36 candidates individually from the full set. All 32 additions retain Ne5 at each stop. With Nd2 retained as eligible, deletions change the winner in 16/35 depth-8 arms and 19/35 node-budget arms. In particular, the four-move menu and the four-plus-a3 menu both choose Ne5. The full menu without a3 also chooses Ne5, while admitting a3 in this background switches the winner to Nd2. This is a contextual effect of eligibility under two stopping rules. It does not identify a unique third move or a chess plan. The legal list and all 136 screen PVs were independently replayed using python-chess 1.11.2 and the preserved full London move history.

## Reproduction and next test

Extract `dev.json` and `result1.json` from the R4 archive and `forced1.json` from R6. Rebuild as described in R4 and run the following from the repository root with fresh output directories.

```sh
python harness/c3x_030_s4l_r7_candidate_menus.py ENGINE dev.json result1.json forced1.json grid_logs > grid.json
python harness/c3x_030_s4l_r7_menu_summary.py grid.json > summary.json
python harness/c3x_030_s4l_r7_london_menu_screen.py ENGINE dev.json result1.json grid.json screen_logs > screen.json
```

Normalized grid SHA-256 `7c59bbe6e17a6bb6d2f163da6f720a4f860a65108288b998771eb51b0a139a34`. Screen SHA-256 `45590d3398aa1536daec1592b943a54dbb39be204822161253dccf9acaac1526`. Run the two existing root receipt test modules (13 tests passed). Inspect the full/full-minus-a3 traces, compare the first persistent divergence that can be manipulated without reordering the input menu again, and use a value or root-order restoration as a falsifier. A separate same-history reply evaluation can ask whether the computational reversal predicts a consequential difference for a legal opponent response.

[Raw UCI, source traces, build log, and replay capsule](https://drive.google.com/file/d/1T5yn7SvNLOT7evmUMp72Qr_3297_K6jq/view). ZIP SHA-256 `8fe3be12bea52a34a49c33e812fe4227faabe69b52c67dd91fa50b49b22e45fa`.
