# C3X 0.30 R26 — TT effects across margins and a board-level move contrast

A broad native panel tested 88 legal histories from 32 games. The two read-channel
masks change root recommendations at fixed node budgets and at fixed depth.
For a named contrast, the independent opponent-reply calculation also supports
a board-level reason, with different references for what the engine did and why
the alternatives differ on the board. No source entry mediation is established.

## Experiment and results

The 40 TWIC and 48 TCEC positions were frozen before engine queries. The
source census parsed 8,391 TWIC 1670 records and 264 TCEC S29 League 2 records.
The latter event had appeared in earlier C3X work. This is an exploratory
sample with repeated checkpoints within games, distinct sampled 12-ply
prefixes, and no score threshold. Source/ply and missing-cell denominators are
in the archive. The upstream and patched-passive reports matched in all 264
control comparisons across the node and depth experiments.

| Read-channel intervention | 8k nodes | 32k nodes | Depth 13 |
| --- | ---: | ---: | ---: |
| TT hint withheld from non-root MovePicker | 27/88 | 24/88 | 28/88 |
| TT searched value withheld | 31/88 | 27/88 | 28/88 |
| Both | 29/88 | 30/88 | 28/88 |
| Changed under any of the three masks | 48/88 | 46/88 | 43/88 |
| 1 MiB hash with consumers enabled | 0/88 | 3/88 | — |

At 32k nodes, the joint mask induced a root switch in nine cases where
neither single mask did, and restored the default root in sixteen cases
where at least one single mask had changed it. For the same root with usable
displayed replies throughout the pair, the reply changed 18/45 under the
picker mask, 19/43 under the value mask, and 19/46 under the joint mask.
None of these 32k changes passed the exact-same-score gate. The fixed-depth
experiment found three such switches under single masks. Without any mask,
the 8k-to-32k stop changed the recommendation in 33/88 and the reply in
20/44 same-root comparisons with both replies observable.

Depth-13 MultiPV reference gaps were available for 86 positions. The root
switch counts for picker/value/joint were 24/18/20 of 43 at 0–14cp,
4/8/7 of 24 at 15–49cp, and 0/2/1 of 19 at 50+cp. These are reference
top-two gaps, at a comparable requested depth and a different root-search
configuration. They need not be the gap between the particular roots that
the intervention switched. The 120k-node reference had 46 unavailable
margins (last PV frame failed the common exact-depth gate), all retained
in the panel. In the depth control, median reported nodes were 39,664
baseline, 62,375 picker off, 25,637.5 value off and 44,724.5 both off.
Nominal iteration depth does not fix the work or selective reach.

## A named move contrast

TWIC 08, ply 61. 32k-node passive Stockfish chose `31...Nd7` and
the two masks together gave `31...a4`. In a 500k unrestricted run,
Stockfish chose Nd7 (−292cp, Black POV). Independent Berserk14 examined
all 44 legal White replies to Nd7 and all 45 to a4 at each depth.

| Berserk depth after White's reply | Nd7 minimum | a4 minimum | Gap | Gap excluding b4 only from the a4 reply scores |
| --- | ---: | ---: | ---: | ---: |
| 13 | −280 (Rxd7) | −363 (b4) | +83 | +54 |
| 15 | −316 (Rxd7) | −412 (b4) | +96 | +25 |

The Nd7 knight immediately attacks the c5 bishop. After a4, b4 supports
c5 before the knight attacks it. At depth 15 the critical lines begin
`...Nd7 Rxd7 Qxd7 fxe4` and `...a4 b4 exf3 Rxe6 Rxe6 Qxf3`.
Among 43 White replies legal in both branches, depth 15 favors Nd7
on 33 and a4 on 10. Removing b4 from the *already scored* a4 list
shows its contribution to the minimum; the remaining 25cp leaves
an intact preference. The geometry explains a concrete resource under
the checked replies. The global TT mask identifies a search intervention
that changes the root; the role of an individual TT entry and any
mediation by the c5/b4 motif remain open.

## A shared plan with a reply fork

TWIC 13, ply 96. At depth 13, both upstream and searched-value-off choose
`49.h5 +156cp`. Upstream gives `...f4 50.h6 ...Ne7`; the intervention
gives `...Nf6 50.h6 ...f4`. Both preserve the h-pawn advance and show
`Ne2+` next. In independent follow-ups, Berserk continues `50.Kh3` after
`...f4` at both depths, but chooses `50.h6` after `...Nf6` at both.
Forced h6 yields +128/+127cp (depth 13/15) after ...f4 and +118/+84cp
after ...Nf6. This supports h6 as a resource in both branches, with room
for different reply-contingent choices. Under ...f4, choosing ...Nf6
after h6 is legal and produces the same piece placement, side to move
and castling/en-passant flags as ...Nf6 h6 ...f4. The halfmove clocks
differ (1 versus 0).

The 500k follow-ups also preserve adverse evidence. In TWIC 03 at ply 61
the unrestricted 500k Stockfish chooses a5, despite the read-channel switch
to Rxf3 at 32k and Rxf3 leading the separate 120k MultiPV frame. Several
500k forced roots lacked a final point report, so they are retained as
bounds. The named successful TWIC 08 contrast is illustrative.

## Reproduction

All results use native engines. The 1,144 node-panel searches were replayed
byte-identically through a separate Python API capture path. The nonduplicate
evidence also includes 528 fixed-depth Stockfish searches, 18 deeper
Stockfish searches, and 186 independent Berserk searches. The 1,876
searches produced 87,150,518 UCI-reported nodes in the archived frames.
The panel has seven targeted regression tests. [Protocol](C3X_030_R26_TT_COMPONENT_PANEL_PROTOCOL_20261117.md) · [Follow-up protocol](C3X_030_R26_TT_FOLLOWUP_PROTOCOL_20261117.md) · [Digests](../receipts/C3X_030_R26_TT_PANEL_20261117.json) · [Byte-verified Drive archive](https://drive.google.com/file/d/1Y72FCNlQONIYj7RpnB3dAxOVGSKkvRBV/view) · [Research decisions and source inventory](C3X_030_R26_TT_RESEARCH_AND_LITERATURE_20261117.md).
