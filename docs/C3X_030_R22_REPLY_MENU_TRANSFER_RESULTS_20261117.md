# R22 — Choosing defenses and valuing their continuations

[Initial protocol](C3X_030_R22_REPLY_MENU_TRANSFER_PROTOCOL_20261117.md) · [expanded protocol](C3X_030_R22_REPLY_MENU_EXPANSION_PROTOCOL_20261117.md) · [menu freeze](../receipts/C3X_030_R22_REPLY_MENU_FREEZE_20261117.json) · [forecast freeze](../receipts/C3X_030_R22_MENU_FORECAST_FREEZE_20261117.json).

The initial sample supplied one pair. The separate opening-disjoint expansion kept six after the preview was allowed to nominate moves whose scores carried bounds. The final 24k/48k admission criteria were unchanged. In total there were 255 shared Black replies, 510 conditioned boards and 1,020 evaluation runs per pass across the two Berserk depths. All references returned finite points and the second execution reproduced the first exactly. This is development evidence from one TCEC event.

| Three-reply menu | Mean omission regret cp, d12 / d14 | Actual worst reply included, d12 / d14 | Public prediction vs agreed full-reference rank |
| --- | ---: | ---: | ---: |
| Lead-PV | 6.07 / 7.86 | 7/14 / 9/14 | 6/6 |
| Opp-PV | 11.14 / 9.36 | 6/14 / 7/14 | 4/6 |
| Mixed | 11.64 / 10.14 | 4/14 / 9/14 | 5/6 |

The single original pilot gives 0/0 cp mean regret for Lead-PV and Mixed, and 0/1.5 for Opp-PV. The six-game expansion gives 7.08/9.17, 13.58/11.83 and 13.00/10.67 for Lead-PV, Mixed and Opp-PV respectively. Each candidate supplies one worst-reply value per game and those observations are paired. Two of seven cases had a forcing-difference reply selected by Mixed. Lead-PV was strongest on the measured coverage loss and public rank endpoints. When the same chosen replies are evaluated by Berserk, Mixed recovered the agreed full rank at both depths on 6/6 games and the alternatives on 5/6. Reply inclusion and source evaluation both matter, and this difference is retrospective and small-sample.

All seven first candidates had the narrow source lead by design. The agreed minimum-based reference favored the second candidate in four of the six agreed games. See the [Korean paired-move card](learner/C3X_R22_ROBUST_REPLY_EXAMPLE_KO.md) for Rac1/Rfe1, where the source's 9 cp lead is replaced by a 17 cp worst-reply reversal at reference depth 14.

## Fixed-menu valuation diagnostic

The [post-exposure diagnostic](C3X_030_R22_FIXED_MENU_BUDGET_PROTOCOL_20261117.md) kept all replies and compared 12k with 48k requested nodes per leaf. Exact repeat forecasts produced agreed-reference accuracies of 6/6 → 4/6 for Lead-PV, 4/6 → 2/6 for Opp-PV and 5/6 → 3/6 for Mixed. There were two lost answers and zero gained on the six reference-stable games for each policy. All three changed the pilot case to a tie. The other reversals were Lead-PV in 5.5 and the other two in 5.6. Additional search in this source regime therefore did not close the valuation gap on these fixed menus. The budget experiment was designed after the main outcomes were seen and measures this cohort, classical Stockfish evaluation, and the stated Berserk reference depths.
