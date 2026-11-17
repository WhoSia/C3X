# R24 — Same displayed score, same native value, different principal variation

[Initial protocol](C3X_030_R24_EQUAL_SCORE_PV_PROTOCOL_20261117.md) · [extension protocol](C3X_030_R24_PV_EXTENSION_PROTOCOL_20261117.md).

We compare qualified reports within a trajectory only if both have the same proposed first move and integer UCI centipawn score. A qualifying report traces to an in-window value from a completed native root attempt. Pair counts are combinatorial and dependent within a position. A strict prefix is a length change. A fork requires different legal moves at a ply present in both lines. Equal full FEN at a later equal ply is a rejoin observation with no claim about equal earlier repetition history.

| Scope | Positions | All same-root, same-cp report pairs | Identical PV | Prefix-only | Actual fork | Actual fork also same native value |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial screen | 4 | 10 | 8 | 1 | 1 | 0 |
| Precommitted S28 League 2 extension | 24 | 134 | 87 | 21 | 26 | 7 |

Fourteen extension positions have a displayed-score fork and five have a raw-value-equal fork. Two exact-value forks occur in the first four plies after the recommendation. One displayed-score fork returns to the same full FEN at plies 9, 10 and 11. The sample is a fixed same-season opening-disjoint development sequence. Its counts do not estimate a general frequency in matches, timing modes, versions or threading configurations.

The Spanish position follows 1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6. Stockfish depth 8 reports 5.O-O Nxe4 6.d4 with +39 cp and native 128. Depth 10 reports 5.O-O Nxe4 6.Re1 Nc5 7.Bxc6 dxc6 8.Nxe5 with +39 cp and native 131. The pinned UCI encoder truncates native value ×100/328, so both raw values display as 39. This is a real fork with equal displayed evaluation.

In the fixed-depth 16-to-64-MiB hash comparison, all twelve pairs keep the same final root, integer score, raw score and PV. The current report is a negative control for that setting and these depths. The original and tracing builds produced matching normalized public output in all runs, with duration and NPS removed.
