# C3X 0.30 R25 — Why one Stockfish reply enters the principal variation

The R24 TCEC round 1.4 replay reported Qxe2 at depths 12 and 18 with the same White native value 292 and the same displayed +89cp. The first Black reply was Bh2+ at 12 and Be7 at 18. R25 joined each public reply to the original native child call, its last PV update, and the copy into the root producer that supplied the UCI report. Each of the six final conditions repeated twice with identical normalized UCI observations and joined evidence. The sham arms matched the archived R23 normalized UCI.

## The default search changed its first reply before depth 18

Black values in the following table use the child side to move's perspective. A return at a search-window boundary need not be an exact move value.

| Nominal iteration | Root attempt | Black call | Incoming window | Candidate returns of interest | PV copied to Qxe2 |
| --- | ---: | ---: | --- | --- | --- |
| 12 | 27 | 23 | [-300, -239] | Bh2+ first, -292, updated PV. Be7 fourth, -1760 at its searched window. | Bh2+, White +292 |
| 13 | 33 | 29 | [-446, -271] | Bh2+ first, -425, updated PV. Be7 fourth, -440. | Bh2+, White +425 |
| 14 | 34 | 30 | [-431, -391] | Bh2+ first, -435, below alpha. Be7 sixth, -391, reached beta with a PV update. | Be7, White +391 |
| 14 | 35 | 31 | [-411, -371] | The TT hint now names Be7. Be7 first, -370, above beta. | Be7, White +370 |
| 18 | 54 | 50 | [-316, -238] | Be7 first, -292, updated PV. Bh2+ second, -303, below the updated alpha. | Be7, White +292 |

The intermediate depth-14 copy is an actual root candidate update during the search. The final UCI rows at depths 12 and 18 have their own producer identifiers, 540 and 999. The change in the next call's TT hint is observed. Establishing which write supplied that hint requires tracing the TT writer.

## Reciprocal intervention at the child MovePicker

The intervention replaces the hint only for the ply-one PV MovePicker after Qxe2 at the targeted iteration. It leaves the root candidates and the value stored in the child's live TT entry intact at that site. The resulting search can change later state, candidate-specific effective depth, windows, node count and the rest of the PV. Each sham arm and its matching-hint control agree on full UCI report, node count and actual copy.

At depth 12, the Be7-first intervention examined Be7 first in the final call. Be7 returned -1750 below alpha, and Bh2+ returned -294 into [-299, -239], establishing the recorded PV. Displayed +89cp persisted. The raw value changed from 292 to 294. After the shared line through 15...Bxc1 the PV changed from 16.Rfxc1 to 16.Raxc1.

At depth 18, the first default call at that iteration gave Be7 -264 at alpha, with no child PV update. The root widened its aspiration window and retried three times. With Bh2+ first, it returned -268 below alpha, and Be7 went second and returned -241 inside [-264, -238]. The root accepted that result on its first attempt. The score became +73cp with raw value 241, and the PV still began with Be7. After 15.Nf3 it reported 15...a6 where the default run reported 15...Nf6.

The intervention establishes causal sensitivity of the measured search to the local ordering hint. In these reciprocal arms, the first reply at each depth persisted while later PV moves and values changed. The original cross-depth fork remains a fact about two complete search contexts. Which part of their different state or budget is necessary for that fork remains open.

- [Build manifest](../receipts/C3X_030_R25_BUILD_20261117.json)
- [Joined native replay](../receipts/C3X_030_R25_REPLY_REPLAY_20261117.json)
- [Board resource enumeration](../receipts/C3X_030_R25_B4_RESOURCE_20261117.json)
- [Rendered Korean explanation](C3X_030_R25_QXE2_EXPLANATION_20261117.md)
