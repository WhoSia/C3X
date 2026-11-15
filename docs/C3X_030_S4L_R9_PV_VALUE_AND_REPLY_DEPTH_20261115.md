# C3X 0.30 S4-L/R9 — Post-PV value substitution and reply-depth sensitivity

2026-11-15 KST. London ply8 is the exposed development case inherited from [R8](C3X_030_S4L_R8_LONDON_PV_GATE_AND_REPLY_VALUE_20261115.md). No new games or sealed holdout positions were used.

## Source question — Does the PV value itself change the move?

Keep the target Nd2 PV re-search enabled in each menu. The full menu enters via its actual +6 null-window result. For the minus-a3 menu reuse the R8 0-to-6 gate substitution. Then change only the score consumed by the root after the PV child has run. The recorded child result, PV and descendant work precede substitution. Downstream search can adapt to the substituted score. Four identity controls match the exact normalized R8 records.

| Menu | PV score supplied to root | Depth 8 winner | 12k requested-node winner |
| --- | --- | --- | --- |
| All legal moves | 14, identity | Nd2 | Nd2 |
| All legal moves | 14 to 0 | Ne5 | Bxd6 |
| Without a3, PV gate enabled | 0, identity | Ne5 | Ne5 |
| Without a3, PV gate enabled | 0 to 14 | Bxd6 | Bxd6 |

The source log links the physical PV child and the root consumption site by invocation IDs within each execution. In the full menu, the substitution removes Nd2's first-window score update even though the PV child actually ran. In the minus-a3 hybrid, +14 exceeds beta=10 and promotes Nd2 in that attempt. On the first retry (window [-10,24]), Nd2 starts first and returns 0, then Ne5 returns +29 and forces another retry. Bxd6 ultimately wins. This is a three-candidate counterexample to explaining the final choice from one local head-to-head score. The substitution changes a local input and does not establish the entire causal path from a3 eligibility.

18 Stockfish searches and 185,804 reported nodes per pass including donor setup. Normalized replay and the selected root-consumption receipts match. Independently recheck them with the [trace auditor](../harness/c3x_030_s4l_r9_pv_trace.py). Exact R8 source hash accepted by the [R9 overlay](../harness/c3x_030_s4l_r9_london_pv_patch.py). Patched binary SHA-256 `32b6e15e9877a35f9d60eb4833f645890c52604162dc95e98a6d44464bbf76c1`. Existing tests 25/25.

## Chess question — Does the all-reply ranking hold at deeper budgets?

Reuse the pinned Berserk 14 and the complete London move history. For each depth, run fresh search state after each candidate, both with a free opponent response and after each legal opponent response (35 after Nd2, 32 after Ne5). Scores are White-perspective cp. The minimum over forced replies and the free-response search run at the same reported depth from different starting plies. Depth is matched within each design, and actual node counts vary.

| Depth | Free Nd2 | Free Ne5 | Worst forced reply Nd2 | Worst forced reply Ne5 |
| --- | ---: | ---: | ---: | ---: |
| 10 (R8) | +13 | +11 | 0 | +23 |
| 12 (R8) | +6 | +4 | +3 | +1 |
| 14 | +7 | +6 | +4 | -1 |
| 16 | +8 | +10 | +9 | -1 |

At depths 14 and 16 the minimizing reply is O-O for both candidates. At depth 16 the free search favors Ne5 by 2 cp, while the worst enumerated reply favors Nd2 by 10 cp. Across the 32 matched reply identities, Nd2 exceeds Ne5 in 14 at depth 14 and 17 at depth 16, with two and zero ties respectively. To match nominal distance from the original root, four further free-response searches at depths 15 and 17 used one ply more than the corresponding forced-response searches. All four selected O-O for Black. The free scores at depth 15 were +10/+14 (Nd2/Ne5), while at depth 17 they were +12/+6. This reverses the ranking between the two horizon-matched checks. The engine remains selective and nominal ply matching does not make the search trees or costs equal. The two new depth grids comprise 138 searches and 31,562,311 reported nodes per pass, with all scores unbounded cp at the specified depth. Repeating the full 138-search sweep in a fresh engine process produced byte-identical normalized JSON. Evidence remains one position and one independent engine family at finite depth. The all-reply advantage is a promising local observation, with no extrapolation to unseen games. A prospective next test should seal a development-disjoint set of histories, predeclare candidate selection and the score criterion, and contrast a single PV with a fixed-budget reply tree.

## Reproduce

Rebuild the R8 Stockfish source, apply the R9 overlay, then run the [native runner](../harness/c3x_030_s4l_r8_london_probe.py) with the archived protocol, R4 result, R7 grid and screen, adding `--post-pv R8_PROBE_JSON`. Run the [Berserk runner](../harness/c3x_030_s4l_r8_london_replies.py) with the R8 executable, network, and protocol plus `--fixed-depth --depth 14 --depth 16`. The [summary](../harness/c3x_030_s4l_r9_reply_summary.py) accepts that JSON or the archived R8 depth JSON. The four horizon-matched checks use the reply runner's evaluate function on the board directly after each root candidate with completed depths 15 and 17.

[Verified native and Berserk evidence capsule](https://drive.google.com/file/d/1_8mmkUmvE-JgNnLMIva1KfWlxatnU1XX/view). ZIP SHA-256 `c9ede2f11f2fa071d2eb54418fa30a5fb3692a94671c26f43a224f69008fa602`, verified by independent byte readback.
