# C3X 0.31/P2-L2 — Previously Registered Macro-Family Exposure Reverses the Tiny M2 Brier Difference but Not the Falsification Gate

**Date:** 2026-11-21. **Scope:** *retrospective* historical exposure sensitivity of original P2, not new native search, randomization, prospective evaluation or change to P2's frozen training/sampling/intervention receipts. Independent real-byte [CI #44879488680](https://github.com/WhoSia/C3X/actions/runs/44879488680): **10 integrity tests PASS**.

## Why L1's exact family test was not enough

L1 found two P2 original Event header families that were previously sampled by R26 from the same source TWIC1670. However, a chess festival or tournament can have separate *Rapid*, *Blitz* and *Women* PGN headers. Crucially, C3X already had a **pre-declared** secondary family-grouping dictionary named `PREDECLARED_MACRO` in [the P2 independent native-data court](../harness/c3x_031_p2_independent_court.py). L2 reads that **unchanged original dictionary** by Python AST, requires it to match the original ten source-defined aliases, and asks what happens to the original 128 events when the R26 exposed games and P2 games are compared at the *same already-registered* macro-event family scale.

Two distinct levels must be kept separate:

1. **Originally registered P2 macro families:** exact original Rapid/Blitz or other map entries; the mapping **pre-exists this L2 audit**, but excluding overlaps here was not part of the original P2 primary experiment and is **still post-outcome**.
2. **New conservative possible umbrella name aliases:** e.g. original R26 `III ch-Sudamericano 2026` versus P2 `III ch-Sudamericano Blitz/Women`, and `7th ASEAN Plus Ind 2026` versus P2 `7th ASEAN Plus Ind Women`. These more expansive aliases are **not verified** to be the same formally organized championship and were **not registered before the P2 outcomes**. They are explicitly optional sensitivity assumptions, never factual claims of tournament identity.

## Three denominators, frozen original P2 prediction probabilities throughout

| Historical exposure exclusion applied *after results* | Exact Event header (L1) | Previously registered P2 macro names (L2) | Additional hypothetical umbrella aliases |
| --- | ---: | ---: | ---: |
| Removed P2 complete-game histories | 8 | **16** | 26 |
| Removed source-target events | 16 | **32** | 52 |
| Remaining complete-game histories | 56 | **48** | 38 |
| Remaining source-target events | **112** | **96** | **76** |
| Remaining source-header families | 15 | 13 | 10 |
| Remaining **macro** families | 15 (literal equivalence) | **10** | 8 |
| Remaining actual bestmove flips | **7** | **6** | **5** |
| Frozen M0 Brier ↓ | 0.0593038 | 0.0593038 | 0.0620068 |
| Frozen M1 Brier ↓ | 0.0589193 | 0.0564605 | 0.0561050 |
| Frozen M2 Brier ↓ | **0.0601507** | **0.0550385** | **0.0559102** |
| Gain `Brier(M1)−Brier(M2)` | **−0.0012314** | **+0.0014220** | +0.0001948 |
| Gain `Brier(M0)−Brier(M2)` | −0.0008469 | +0.0042654 | +0.0060966 |

The primary P2 64-game/128-event Brier and all seven original source flips were **not modified**. The above are **nested post-outcome sensitivity subsets** that answer different historical exposure definitions. None crosses the predeclared +0.01 improvement requirement.

For the pre-existing registered macro mapping on 96 events, whole-macro-family bootstrap (2,000 draws, original P2 secondary seed `310222`) gives:
- `M1−M2 = +0.0014220`, 95% interval **[−0.0047731,+0.0064239]**.
- `M0−M2 = +0.0042654`, interval **[−0.0085793,+0.0168109]**.

The additional *hypothetical* conservative alias scenario on 76 events (eight remaining macro groups, explicitly later seed `310223`) gives:
- `M1−M2 = +0.0001948`, interval **[−0.0076511,+0.0065648]**.
- `M0−M2 = +0.0060966`, interval **[−0.0107342,+0.0211522]**.

All intervals include **zero**. Thus **the numerical sign of the Brier difference is sensitive to historically exposed family granularity**, while **the prospectively frozen scientific gate consistently FAILS**. It would be incorrect either to say “M2 is proven harmful” or to say “M2 generalizes positively under the cleanest source families.” Absence of verified predictive gain remains the supported conclusion, rather than a stable effect direction.

## The scientific target choice changes: P2-028 is not *macro-family unseen*

Previously executed P2-D1 [equal-depth original-pair source audit](C3X_031_P2_D1_EQUAL_DEPTH_RESULTS_20261121.md) identified **P2-028-0** as the **only** one of seven originally flipped node-budget move pairs whose *exact same pair* was reproduced at the original fixed completed depth. It is an excellent **exploratory within-search mechanism target**.

However, P2-028 was drawn from **FIDE World Open U20 Blitz** while R26 had previously selected a game from **FIDE World Open U20 Rapid** in the **same** TWIC1670 issue. The original predeclared P2 macro taxonomy groups both under **FIDE World Open U20**. In L2, its `P2-028-0` event is therefore excluded under registered macro-family historical exposure, even though its whole-game moves are not R26-duplicate and its literal Event header differs.

Similarly, the later *non-verified alias scenario* excludes `P2-055-0` because R26 `III ch-Sudamericano 2026` could belong to a wider championship umbrella than P2 `III ch-Sudamericano Blitz`.

**Operational consequence:** Keep P2-028 as a powerful *source-mechanism development case* with exact original move-pair transport, but do **not** present work on it as a never-seen-family confirmation of that mechanism. A newly sealed tournament-family-disjoint P3 confirmation must come from a separate publisher cohort and genuinely untouched competitor family after original archives are checked.

## Provenance and limits

- Original publisher TWIC1670 ZIP SHA256 `6e6866cfe57ea0db7849f9b686fded1c1fe9d1fcab783359030b97ace377eccf`, [Drive publisher custody](https://drive.google.com/file/d/1aYTJF5WYCP-GkWndWrdot20xeA5eVf3H/view). Original R26 source [historical exact game receipt](../receipts/C3X_030_R26_TT_PREOUTCOME_20261117.json).
- All 64 P2 legal game histories and 128 physically signed interventions were restored from their **original GitHub Actions artifacts**, rehashed against SHA `2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4` and `69904f920c21844f2a2f278f6332b7c8fdc9857a821c33fdc0f29dfa56aaf09f` respectively. No original PGN or full private source history was added to Git.
- [L1 original exact source family correction](C3X_031_P2_L1_R26_SOURCE_FAMILY_EXPOSURE_RESULTS_20261121.md), [L2 source-based code](../harness/c3x_031_p2_l2_umbrella_exposure.py), [10 native-data/tamper tests](../tests/test_c3x_031_p2_l2_umbrella_exposure.py), [read-only CI workflow](../.github/workflows/c3x-031-p2-l2-macrofamilies.yml).
- [Actual successful GHA #44879488680](https://github.com/WhoSia/C3X/actions/runs/44879488680) issued derived JSON SHA256 `2c97e60ed677dd0936434abd9bfd64505e441a541118bfe9685ea68c56798192`, ZIP SHA256 `74024402cb3be34a92c1ecd534c56705f2bc15bb938599fa16c280675cf0983b`, original artifact ID `14697153926`; [Drive checked original L2 ZIP](https://drive.google.com/file/d/1TYzgiI4s1_c8Vfz7ZKtxM1BBApaIn9bJ/view) had exactly the same ZIP hash and valid CRC on readback.
- This audit ran **zero new Stockfish searches**, did **not** validate chess strategies under real replies, did **not** identify the causal TT/history/remaining-budget mediator, and did **not** produce learner transfer observations.

## Version-level decision

The P2 native total effects, original seven flips, first primary negative predictive generalization result and its chain of evidence remain. But the abstract's real contribution must be described as **historical family-exposure-aware transport testing**, not “new publisher archive from every earlier experiment” or “universally stable negative M2 improvement.”

**0.31/P3 next:** Source-level mechanistic state restore on a precisely defined, matched, physically contacted root-choice pair (P2-028 as *development*, never the new independent-groups claim), followed by an **actually unseen family** independent native replication on another source. Explicitly keep the repair or failed mediator rescue as the outcome, not merely another colored source log.
