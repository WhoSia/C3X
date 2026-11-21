# C3X 0.30 R29 — Event coverage and effects on newly sampled games

32 histories frozen from [TWIC 1663](https://theweekinchess.com/html/twic1663.html)
before opening the engine results. Deterministic sampling used one game
per normalized event label. The games had no matching full-game
identity in the R26 and R28 manifests and excluded the normalized labels
listed in the R26–R28 experiment fixtures. Event sections may belong
to an overarching tournament. This pilot used a single issue and
reuses the engine pair. Each native control matched the original
executable. The full campaign was executed twice and its result JSON
was byte-identical (SHA-256
`e094e8706b90fc04dc2a1cec79e8baffd7c17ea330ad54952e29514b3e5b1828`).

| Prespecified reference stratum | Positions | Named-reply move read | Producing-attempt value cutoff |
| --- | ---: | ---: | ---: |
| Close | 13 | 11 | 0 |
| Stable, large absolute gap | 7 | 3 | 2 |
| Depth reversal | 2 | 0 | 0 |
| Intermediate | 9 | 7 | 1 |
| Point unavailable | 1 | 1 | 0 |
| Total | 32 | 22 | 3 |

The rules admitted 22 distinct positions and 25 interventions. Fourteen
of 22 move reads belonged to the producing attempt. A single move hint
changed the recorded first reply in five and the direct child return
in nine (two comparisons stopped before a trusted return). In one
trial the alternative replaced the active leader in the targeted
attempt. In two other trials the alternative became the final choice
even though the targeted event was earlier than the producer.

| Case | Berserk recommendation-minus-alternative, d13/d15 | What the mask changed |
| --- | --- | --- |
| R29-018 | +6/+10cp | In the producing attempt, the alternative Qd6 crossed the active-window comparison; Qe7 remained the final recommendation. |
| R29-029 | −5/+12cp | Early hint mask changed child 813→762, and the eventual pick changed from …axb4 to …Ne6. Final public depth changed 15→14. |
| R29-030 | +6/+16cp | Early hint mask changed child 160→165, and the final pick changed from Be2 to a3. The masked final −46cp is an upper bound. |

All three numerical masks removed the observed TT cutoff and induced a
reply search. Their direct child values and final choices remained
unchanged. Both depth-reversal cases had ply-one reads under the
named alternative. The independent replies were absent from eligible
stored move hints and their producing attempts had no recorded genuine
ply-one TT cutoff on the alternative. The frozen protocol abstains
on both. A separate observed-reply rule or deeper source trace can
improve coverage if tested on a new sample. These results are empirical
for the selected engine and finite budget, and do not imply that either
masked recommendation is objectively preferable or that every path
to the new choice was identified.

The four named cases and the missed cases point to two ways to improve:
measure whether a rule finds an auditable source event, and separately
measure how far any verified effect propagates. Sample the next
depth-reversal and large-gap cases across independent issues or engines.
