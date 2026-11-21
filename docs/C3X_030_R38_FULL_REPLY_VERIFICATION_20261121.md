# C3X 0.30/R38 — Frozen 540-Search Reply Court: Full-Leaf Legality, Replay Identity and Context-Conditioned Reversal

**Independent derivative audit of original R37 native search JSON, not a new engine run.**

- **Final successful read-only CI:** [GitHub Actions #44866755312](https://github.com/WhoSia/C3X/actions/runs/44866755312), Python 3.12, `chess==1.11.2`, **11 tests pass**, original JSON SHA verified before recomputation.
- Original R37 genuine experimental source: [native #44866204367](https://github.com/WhoSia/C3X/actions/runs/44866204367), 540 new Berserk 14 analyses (not repeated in R38).
- Frozen R37 native JSON SHA256 `0fa5eadedbdff69b692f1d5d713a4a7649f90f57bfb480eb5f738eccb4bd4fcd`; original GitHub Actions artifact ZIP `5c3ed07315986fe2336f9ee4481c6a2de825285de343169a78d8a403d4eb61e6`.
- R38 independently recomputed derived JSON SHA256 `2d22cbb1052154700c63e30533f4a197096f8ed4d3a29d2b5ed1991fca418d73`; derived artifact ZIP SHA256 `2172e8ea40ec184e6bbf18f94ab42960ff1cc8ecf4da628a659a360fbe61899f`.
- **Drive readback verified:** [original R37 ZIP](https://drive.google.com/file/d/1axG3y0LQnFNP9AQSutYfDcGhj4suviUa/view) and [derived R38 ZIP](https://drive.google.com/file/d/1gHq_AQ3SEJ_GJ7_7iBFwq8Z1KwOP3PfH/view), both with original exact ZIP SHA and CRC.

## Checks from raw R37 sample-level values

R38 did not merely trust R37's published minima. It verified the original FEN and three frozen root moves, enumerated all legal Black replies from the exact board under `python-chess`, revalidated **45 same reply UCI choices for each root**, checked every original leaf PV for move legality, independently compared **270 cold replay pairs**, recomputed all 540 search node counts (**14,596,738 nodes**), reconstructed two-depth worst-reply minima, and computed each shared-reply pairwise comparison from the original native leaf scores.

| Pair, same 45 legal Black replies | Depth 10 higher / tie / lower | Depth 12 higher / tie / lower |
| --- | --- | --- |
| Qf3 vs Qd3 | 33 / 1 / 11 | 34 / 1 / 10 |
| Qf3 vs a3 | 28 / 0 / 17 | 30 / 0 / 15 |
| Qd3 vs a3 | 18 / 1 / 26 | 22 / 2 / 21 |

At both depths the **minimum** evaluation of Qf3 exceeds that of Qd3 (74 vs 62 cp, 72 vs 60 cp), while a substantial finite set of concrete legal reply identities yields the opposite local ranking. Neither a single minimum nor a simple reply-majority by itself denotes a validated opponent policy.

The 11 test checks include **deliberately corrupted** R37 inputs: missing legal replies, fabricated cold replay, illegal reported PV, altered FEN, changed network SHA, changed repeat schedule, changed claimed full-history coverage, and post hoc root ranking. These synthetic test mutations do **not** count as real new chess outcomes.

## Engineering failure chronology (preserved)

- [R38 first CI #44866543424](https://github.com/WhoSia/C3X/actions/runs/44866543424) **FAILED**: a literal escaped newline introduced a Python syntax error. Source repaired without touching native R37 data.
- [Later CI #44866630375](https://github.com/WhoSia/C3X/actions/runs/44866630375) **FAILED** one negative fixture because `a2a3` happened to be legal in that tested White-to-move position; replaced with an actually illegal Black-pawn move `e7e5`, without touching scores, protocol, or R37 data.
- [Final CI #44866755312](https://github.com/WhoSia/C3X/actions/runs/44866755312) **SUCCESS**. Earlier failures remain visible as engineering errors, not scientific chess counterexamples.

## Scientific decision

R37+R38 close the narrow missing third-candidate *independent FEN-only referee* obligation **for exposed R30-017 at two depths**. They do not resolve original full-history repetition state, broader independent-game generalization, Stockfish's exact intermediate TT/history causal mediator, universal robust chess planning, or human learning effects.

R38 supports a strictly empirical conclusion: **at identical Black-reply identities, move preferences depend on which reply is realized, even though worst-reply ranks are stable across the two tested depths.** This is a substantive motivation to study a context-dependent conditional response plan in the proposed C3X 0.31 search-state abstraction framework.

Reproduction: [source verification code](../harness/c3x_030_r38_reply_court.py), [11 actual-data and negative tests](../tests/test_c3x_030_r38_reply_court.py), [read-only CI](../.github/workflows/c3x-030-r38-reply-court.yml).
