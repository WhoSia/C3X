# C3X 0.30 S4-L/R14 — Same-search root scores and the public-depth ceiling

2026-11-17 KST. The [protocol](C3X_030_S4L_R14_MATCHED_TRACE_PROTOCOL_20261117.md) was committed before selection. The [forecast freeze](../receipts/C3X_030_S4L_R14_R15_LEAGUE1_FORECAST_FREEZE_20261117.json) predates both independent searches. Eight questions were admitted from the 264-game TCEC S29 League 1 source after screening near pairs and excluding already used 12-ply opening prefixes in R10/R11. Exactly one common opponent reply was fixed per game.

## Observation

Each of the 16 forced Stockfish leaves used a 12,000-node request. Reported nodes sum to 192,177 across all leaves. The same executions yielded the public UCI baseline and 10,013 internal root score records in complete go epochs. In six leaves the maximum UCI score report's depth equals the maximum logged root iteration. In ten leaves the UCI depth is one higher. **Zero leaves** have a root score in an iteration deeper than the greatest reported UCI score depth. The depth condition therefore excludes every internal point before evaluating the in-window condition.

Stockfish16 emits a public PV report when it stops, and `UCI::pv` computes the depth label from rootDepth and an update flag. A reported UCI depth above the latest root event is compatible with that path. A public depth label is not a certificate of an additional completed root iteration. This pilot's rule obtains no rank incremental information even though the execution trace contains many more records.

| Projection | Correct at depth 16 | Correct at depth 18 |
| --- | ---: | ---: |
| Public last unbounded score | 6/8 | 6/8 |
| Public last score, permitting bound reports as predictions | 7/8 | 7/8 |
| Public unbounded score plus predeclared deeper trace rule | 6/8 | 6/8 |

Both reference depths label all eight questions, with the same signs. The trace rule replaces no value and changes no prediction. Five of eight labels favor the second candidate, so an always-second rule scores 5/8. The public-last heuristic changes one prediction, round 2.4. Following cxd4 or Ng5 with …Ng6, the unbounded public pair is 85 vs 112 cp and the public-last pair is 81 vs 78. The latter direction agrees with Berserk at depths 16 and 18 (126 vs 84 and 118 vs 89). This is an observed prediction comparison on one changed question. Window bounds remain bounds.

## Reproducibility and scope

Berserk did 16 forced searches per depth with 4,167,333 and 8,142,779 reported nodes, respectively. Independent reruns reproduce selection and both reference files byte-for-byte. The two source transcripts match after removing only UCI stdout `nps` and `time` fields, including all root trace records, final labels and public scores. [Raw and repeated evidence](https://drive.google.com/file/d/1HFathAD2eGoPYRX5p9ciQm91uCMOao0R/view) has archive SHA-256 `4e0355d13e2cb81e838d9af091a80dc9a71d446e86b7c3631ec8af4bc373a57f`.

Treat R14 as a scope limit for this depth-based source rule. Compare a branch witness that can alter a concrete prediction, keeping public tree inputs fixed, before revisiting incremental trace information. R14 concerns fixed-reply rank on one event sample. Named-plan survival, source interventions and human transfer retain their own tests.
