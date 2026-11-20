# C3X 0.30 R28 — When a Stockfish recommendation deserves a challenge

The [frozen protocol](C3X_030_R28_RELIANCE_PROTOCOL_20261121.md) used 32
TWIC 1671 games. The paired experiment made 85 Stockfish and 636 Berserk
searches. The fixed-depth PV checks added 384 Stockfish searches. The 32
history records and the paired-engine result reproduced byte for byte on
separate invocations. The producer audit added 12 searches, giving 1,117
searches in the first pass across the three components. The paired-engine
reproduction is separate.

## Why this move over the alternative?

Stockfish changed its actual recommendation between 8k and 32k nodes
in 11 of 32 positions. For the other 21, the alternative came from the
separate MultiPV run. At both reference depths, the two-child comparison
favored the 32k move by at least 25cp in 9 positions and the alternative by
at least 25cp in 2. The other 21 were unresolved. Eight of those switched
the sign of the Berserk comparison between depths 13 and 15.

| Case | Stockfish choice / alternative | Direct child margins | After all legal replies |
| --- | --- | ---: | ---: |
| R28-002 | …f6 / …Bh5 | +61 / +37 | +31 / +55 |
| R28-003 | …Nxd5 / …exf4 | −32 / −105 | −51 / −59 |
| R28-004 | h4 / Bd5 | +61 / +50 | +4 / +9 |
| R28-015 | Kg2 / Nc3 | −25 / −30 | −22 / −19 |

The table uses the root mover's perspective. For R28-003, after Black's
…Nxd5, White's exd5 minimizes Black's score at both leaf depths. After
…exf4, the minimizing white reply changes from gxf4 to Qxf4. The
disagreement held after examining all 40 and 47 responses at both nominal
horizons. This is a reference-backed challenge to a finite-budget
recommendation. The later trace found the emitting call in attempt 31,
which stopped at 32,053 UCI nodes. The logged returns for …Nxd5 and
…exf4 were both on the upper-bound side of their search windows. The
published +3cp had the upper-bound flag. The trace supports a description
of the finite search and its stop, with no exact point ranking between
those returns.

Four cases were reply-audited, comprising 508 leaf searches. Two of four
meet the original directional/margin rule in both readings. The four
are an ordered subset, so the demotion count does not estimate a
population rate. Default reliance scoring uses only matching directions
under both direct and enumerated search. In the synthetic smoke test,
four completed records entered the transition table, one qualified for
adoption of supported advice and one for retention of a better initial
choice. Two completed records had unresolved reference labels. No
human responses were collected.

## What changed after the same move and value?

In the paired node-budget reading, R28-029 reported …Ne4 and the number
+108 in both runs, with Ka1 versus h5 as the reply. The 8k number was a
point score and the 32k number an upper bound. This is evidence that an
interface showing only the formatted number could conceal a distinction.

The initial depth 10/12/14 grid yielded zero two-point equal-score forks.
The exploratory 8–16 grid yielded 10 pairs across 9 positions, each with
the same recommendation, identical unbounded UCI cp, and a different
immediate opponent reply. Two examples:

| Case | Score and recommendation | Depth pair and principal variations |
| --- | --- | --- |
| R28-023 | −28cp, …Kf8 | d9 …Kf8 Rf1 Kg7 Bd3; d10 …Kf8 Bd3 Kg7 Rf1 |
| R28-024 | −3cp, …cxd4 | d9 …cxd4 Nxd4 Rd7; d13 …cxd4 Rxd4 Rxd4 Nxd4 |

In R28-023 legal replay reaches the same full FEN at ply 4. The histories
differ, and the next displayed black move splits again (…d4 or …h4).
Subsequent repetition rights are outside the FEN comparison. In
R28-024 both white replies capture on d4. In the first line the recapturing
knight remains there through …Rd7. In the second line the recapturing rook
is traded off before the knight arrives, and replay does not reach the
same FEN at any matched ply in the available two lines. This distinction
supports board claims about resource use. The lines alone do not establish
a different strategic aim or prove why Stockfish picked the root move.

The R28-024 producer trace joined both −3cp reports to their actual
Stockfish root candidate calls. At depth 9, search attempt 16 and
candidate 379 returned the internal value −10. At depth 13, attempt 27
and candidate 621 returned −11. Both were inside their respective
aspiration windows. The public mapping displays both as −3cp. All
three traced settings gave identical normalized UCI output with the
original executable, instrumentation disabled, instrumentation enabled,
and an enabled repeat. The enabled traces also repeated exactly.
The event inside the tree that made the reply change remains open.

## Research decision

Use cases like R28-023 to test explanations that should survive a move
reordering. Use cases like R28-024 to test explanations about which piece
can carry out the plan and at what cost. For the latter, the next
mechanistic test should select a branch-specific search event before
intervention, replay under sham, removal and restoration, and measure
whether its parent scores, root ranking or only its public PV change.
Maintain coverage by sampling absolute gaps and response types across
several PGN sources. The present issue includes multiple sections of some
tournaments, and the expanded depth grid is exploratory.

For a participant experiment, compare the existing PV, board-response
and source-backed conditions on two independent outcomes. First, measure
unassisted transfer to a new position. Second, measure beneficial
adoption and justified retention when advice is revealed. If source
evidence helps prediction without improving transfer or reliance,
make it optional for learners and keep it as an audit interface.
An audit of successful reliance needs several new cases like R28-003
and a second reference regime before recruitment.

## Reproduction

Use the R26/R27 archived inputs and pinned engine binaries. Invoke the
R28 freeze harness with the TWIC 1671 ZIP, R26 frozen cohort, R27 items
and a fresh output path. Pass the resulting cohort and its SHA to the
paired harness with the original Stockfish 16, Berserk and its external
NNUE. Run the depth harness twice, once with the default grid and once
with `--depths 8 9 10 11 12 13 14 15 16`. Pass the expanded output and
the cohort to the fork replay. Run the scoring CLI with the paired
result and synthetic choices. The native follow-up uses the original
Stockfish, the R27 instrumented binary and the pinned Stockfish NNUE
with the original cohort. All writers require a fresh output path.
The five R28 tests plus the four R23 and five R27 regression tests passed.

| Bytes | SHA-256 |
| --- | --- |
| Frozen cohort | `1cfb47753f18ea060e6ac7de6752e5ac80c8fe3d7f0e69e97678fae623de96cd` |
| Paired engine comparison and reply audits | `57122631b88e49040432d2ca9ff5cfa8c27a445568988d738d35834ce05abd32` |
| Expanded PV grid | `38a5a700301c32bded03c13283ae8f14a4d0e2c3b9e79b617769e86c4aaf0033` |
| Native producer join | `0242061feff78dfb860611c13cb48dffa093e3dad30fb66d1b55a0ef17963843` |
| Legal board replay | `0001ee5a50cb15c7d0504494a3bfffdc8b46137681700af3c2188045afa51887` |

[Reconciled literature queue](C3X_030_R28_MISSING_LITERATURE_20261121.md).

[Paired comparison archive](https://drive.google.com/file/d/15NQNIt4xgkK5EaBOrsgbA76ZAFkyMd24/view) · [Native producer archive](https://drive.google.com/file/d/1C9GyUFtXkmxZ3b_bgPM6KBY-xQSSVeKn/view).
