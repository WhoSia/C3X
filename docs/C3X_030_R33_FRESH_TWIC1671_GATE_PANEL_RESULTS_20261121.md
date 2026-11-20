# C3X 0.30 R33 — Fresh-game early-return interventions and hidden changes

The R32 depth-3 g5 mechanism motivated a broader test. The new source
was TWIC 1671 (16 November 2026), a publisher PGN archive listed as
7,379 games. The source ZIP SHA-256 is
`7540c3430a4124b513f46338a2d3a8f964ab22b774fb438da04921bc7385f03d`.
C3X sampled 64 distinct games and four-field board identities across
16 new event families. The frozen sampler excluded 78 prior event
families and previous game/board keys. Each new position supplied two
events according to a rule fixed before running any intervention.
These are 128 selected events in 64 games.

The native instrument was an overlay on the R31 Stockfish 16 source.
It observed actual non-PV children of a singular-verification search,
where the searcher excluded the TT move and another candidate
encountered the early child-futility condition. It nominated the
smallest nonnegative margin of futility floor over beta in each
null-eligibility stratum, with the earliest event as a tie breaker.
All 64 positions had one eligible target per stratum. The probe
kept history, TT, initial window and node budget of 32,000 fixed.
After the 64 source-only discovery runs, each of the 128 target calls
was rerun with futility suppressed, and with both futility and
null-move entry suppressed. Both treatments were repeated in fresh
engine processes.

## Results

| Outcome | Null-ineligible target, futility off (n=64) | Null-eligible target, futility off (n=64) | Null-eligible target, both off (n=64) |
| --- | ---: | ---: | ---: |
| Immediate event return changed | 54 | 53 | 61 |
| Original root-candidate value changed at the same window | 10/60 comparable | 2/55 comparable | 9/55 comparable |
| Public score, bound or PV iteration changed | 32 | 8 | 37 |
| Final bestmove changed | 4 | 3 | 7 |
| Final bestmove changed with same completed depth | 3 | 1 | 3 |
| Immediate event changed while public iteration stayed equal | 25 | 45 | 24 |
| Real moves examined inside the target | 80 total | 7 total | 71 total |

The 64 null-ineligible events were negative controls for the additional
null flag. In all 64, futility-only and both-gates-off yielded the
same selected event return, normalized UCI public stream, root candidate
and final move. Their stderr texts differed in the audit flag for
the null intervention. Wall time and nps were outside the equality
check.

In the null-eligible stratum, futility suppression still permitted
a null cutoff in 57/64 targets. Suppressing both gates removed those
returns and exposed additional actual chess moves. The final-move
difference increased from 3/64 to 7/64. Four positions gained a
final-move change that required the additional null intervention.
This is a within-stratum intervention comparison, with one
preselected event per position.

Across the two strata, 11 event interventions changed the final
recommendation in nine unique games. Six of the 11 final changes under
the combined intervention occurred with the same number of completed
iterative-deepening depths as the original. The other five also
changed the number of completed depths under the fixed node budget.
The latter require fixed-depth follow-up before describing a
within-iteration move preference difference.

The original nominated root-candidate's update flag was unchanged
in every comparable read. Several final move changes came from
later root candidates or from a different depth-completion boundary.
The source event therefore affected the outcome through subsequent
search, without necessarily changing the candidate that enclosed
the selected event. These results are diagnostic for the same-run
searcher and the frozen selection rule. They do not identify one
common downstream mediator across all cases.

## Examples with final move changes

Notation is SAN from the exact sampled history.

| New source fixture | Selected gate | Original bestmove | F or F+N treatment | Depth completion |
| --- | --- | --- | --- | --- |
| R33-003, Asian Nations Cup | Null-eligible | h3 | F+N gives Bc7 | 11 → 12 |
| R33-021, Polish Championship semifinal | Null-ineligible | h6 | F gives Nxe4 | 11 → 11 |
| R33-040, Tournament of Peace | Null-eligible | h3 | F+N gives Qxc7 | 12 → 12 |
| R33-042, European Youth U14 Open | Null-ineligible | Bc4 | F gives Bb3 | 10 → 10 |

R33-003 illustrates the depth boundary. Its targeted event occurred
in a non-PV probe inside the f3e5 candidate. The ordinary and
futility-only searches ended with completed depth 11 and h3.
With both early returns disabled, Stockfish completed depth 12 and
recommended Bc7. The evidence establishes a budget-conditioned
recommendation effect. It does not yet establish that the root would
prefer Bc7 to h3 if both arms were forced to finish depth 12.

R33-040 supplies a same-completed-depth example. The final
recommendation changed from h3 to Qxc7 with both early exits
disabled, while the public depth count remained 12. The selected
event was in a different root candidate. Its immediate return
and later search state require a root-to-root mediation trace.

## Reproducibility and validity

Every one of the 64 baseline positions passed old-binary versus
observer-disabled versus observer-enabled equivalence on normalized
UCI and native root receipts. The 128 frozen event signatures were
verified before each treatment. Exactly 256 intervention-arm pairs
were repeated, and their complete native stderr bytes matched.
This campaign executed 192 baseline/observation and 512
intervention searches, totaling 704 fresh Stockfish runs. The full
panel result SHA-256 is
`367f7bf4e3993312f41bdccaeb59caf77f97f28c0609d18144513d55e55cad9b`.
The signed summary SHA-256 is
`b5f03e9e773467d4ef8e46c9a637626e5a7b691f21116d7a115236eacf31bf67`.

The source issue contains additional games outside the 64 selected
positions. The 16 source event families are distinct from those
excluded, but the 64 selected games share event families and chess
motifs. The rates are descriptive over this deterministic selection,
with game-level clustering. The selected event is the first minimal
slack example per position and stratum, hence conditional on the
searcher having such a branch.

No independently judged move quality or human learning outcome was
measured here. A changed Stockfish bestmove under one finite search
budget can reflect search allocation or depth completion. The
learner trial in R31 is the current human protocol.

The original TWIC material is from Mark Crowther, The Week in Chess,
and is retained in the private reproduction archive. Publisher
[issue listing](https://theweekinchess.com/twic).
[Raw files, receipts, tests and byte manifests](https://drive.google.com/file/d/1C3RZRyibwCthOaoWOLYu4IZNzdGlPJg8/view).
The downloaded archive matched SHA-256
`e72ba91c0ffdbbb075642f044706d356fca84b4fa257a3ebcb7755db5837d8bd`.

## Next decisions

1. Re-run the 11 changed event targets to a fixed completed depth,
   separating within-iteration ranking from node-limit completion.
   Leave the original treatment events and clocks frozen.
2. Trace R33-040, the first same-depth null-eligible case where the
   combined intervention changes the final move. Identify the first
   later root-candidate return or update at a common alpha, then
   intervene on that intermediate state.
3. Convert several source-backed examples, including null outcomes,
   into learner cards after independently checking board-level
   strategic claims. The C−D difference in transfer accuracy,
   measured on unseen opponent replies, remains the human endpoint.
