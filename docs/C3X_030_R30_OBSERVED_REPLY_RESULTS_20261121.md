# C3X 0.30 R30 — More eligible reads and a public-display baseline

The 32 positions from TWIC 1664 were frozen before using either engine.
The discovery seal was committed before any masks were applied. Every
instrumented baseline agreed with original Stockfish. All masked probes
matched their frozen pre-treatment receipt and hit one requested gate;
their restored controls matched the untreated raw traces. Full discovery
and intervention campaigns were repeated byte for byte.

| Named source rule | Masks | First recorded reply changed | Child containing the read changed | Final pick changed |
| --- | ---: | ---: | ---: | ---: |
| Independent Berserk reply matching Stockfish hint | 21 | 10 | 13 | 1 |
| Stockfish's own first searched reply matching its hint | 8 | 6 | 6 | 0 |
| Value cutoff in the producing attempt | 3 | 3 | 0 | 0 |

The 32 masks cover 29 distinct cases. Among the 11 cases without an
independent-reply hint, the new fallback supplies 8. Six of these
eight are in the baseline's producing attempt. The two rule classes
are assigned to different cases and their intervention rates cannot
be interpreted as a causal comparison between rules. Berserk point
comparison classifies the sample into 15 close, 11 intermediate,
6 large and zero depth reversals. The two previously exposed R29
reversals are a separate follow-up, not new data.

R30-017 is the one final move change. A move-hint mask beneath
the alternative a3 changed the final choice from Qf3 to Qd3.
The reference's two candidate differences were +7 and −1cp.
The intervention changes the computation; this result does not
rank Qd3 against the other candidates in actual chess.

## What can the viewer see?

The Althöfer-inspired comparison uses paired public traces. The
final display includes best move, score, its bound and public
PV. The full iteration display additionally includes each public
depth and its score/bound/PV. Node counts, hash fullness, reporting
timing and selective depth are excluded from those projections.
Seven paired runs changed the final display, and the same seven
changed the full iteration display. Twenty-two changed only UCI
metadata excluded from both displays; three had no normalized
UCI stream change. In 13 of the 19 altered child returns, the full
public iteration projection was unchanged. This measures which
counterfactual differences are visible across a pair of engine runs.
It does not measure what a user learns from watching the untreated run.

## Verification

- Sealed discovery SHA-256
  `6de3270ae6769d5002ee22ac28db2c6cb2998ebd72a094274cce507756ca71be`.
- Intervention result SHA-256
  `e3e7ad66c86f50e75a6f783af68942914ebd7fb7c6f2011576701f36ebee2d26`.
- 30 tests passed across the new and reused research units.
- [Raw cohort logs](https://drive.google.com/file/d/1BMSvffPHCzNQXpSjpQlxD9BihJwn8neM/view).
- [Reversal and mechanism follow-up](C3X_030_R30_REVERSAL_MECHANISM_RESULTS_20261121.md).
