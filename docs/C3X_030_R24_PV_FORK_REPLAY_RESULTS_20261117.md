# R24 — Which future move changed?

[Spanish freeze](../receipts/C3X_030_R24_SPANISH_PV_FORK_FREEZE_20261117.json) · [strict same-value freeze](../receipts/C3X_030_R24_EQUAL_NATIVE_FORK_FREEZE_20261117.json).

| Position | Same recommendation and score | First divergent ply | Earlier continuation | Later continuation |
| --- | --- | ---: | --- | --- |
| Spanish after 4…Nf6 | 5.O-O, +39 cp; raw 128 / 131 | 3 | …Nxe4 6.d4 | …Nxe4 6.Re1 |
| TCEC S28 League 2, round 1.4, 24 plies | 13.Qxe2, +89 cp; raw 292 / 292 | 2 | …Bh2+ | …Be7 |

The fresh fixed-depth searches (8/10 and 12/18) and fresh fixed-node searches (1532/15609 and 8170/257967 requested) reproduced the frozen recommendation, displayed and raw values, and divergent prefix for each case in all eight paired clean/traced comparisons. Nominal depth may advance once more when a node-limited attempt is interrupted; the receipts preserve the depth of the originating producer.

For the Spanish pair, d4 attacks the e5 pawn and Re1 attacks the knight on e4. The independent fixed-reply assessment at that same common board favored Re1 at depth 12 (+68 versus +56 cp for White) and d4 at depth 14 (+49 versus -12). In the strict pair, …Bh2+ imposes check and …Be7 does not. The two Black moves were judged after the same Qxe2. Berserk favored …Be7 at both depths, by 16 and 11 cp from Black's side. These comparisons apply at the exact branch point and do not identify the native cause of the later variation or a single preferred long-term plan.

[Spanish tutorial](learner/C3X_R24_SPANISH_PV_FORK_KO.md) · [same-native tutorial](learner/C3X_R24_SAME_NATIVE_PV_FORK_KO.md).
