# C3X 0.30/R37 — Independent Referee for the Previously Unjudged Third Winner Qd3

**Actual native experiment:** [GitHub Actions success #44866204367](https://github.com/WhoSia/C3X/actions/runs/44866204367), first protocol frozen separately [before any R37 scores](C3X_030_R37_THIRD_MOVE_REFEREE_PREREG_20261121.md). Actual new searches **540**, original independent engine **Berserk 14**, source `8ae895a6151695be4a50d4fb65b0c131659c513a`, network SHA256 `9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084`, built engine binary SHA256 `3e592d5d67a5cd5a0afefdcc25ac6d15f2bff8fb4c1ee0bcd58115ab88a7949e`. Python `chess==1.11.2`, Threads=1, Hash=16MiB. [Executable source](../harness/c3x_030_r37_third_move_referee.py), [seven protocol tests](../tests/test_c3x_030_r37_third_move_referee.py), read-only [native workflow](../.github/workflows/c3x-030-r37-third-move-referee.yml).

## Actual question

R30-017's local Stockfish TT move-hint intervention changed the final selected move from `e2f3` (**Qf3**) to `e2d3` (**Qd3**), but the original independent comparison only judged Qf3 and `a2a3` (**a3**). The treatment-selected Qd3 was a **third** move and therefore lacked independent strategic evidence. We now evaluate exactly those three legal moves without changing the frozen post-selected diagnostic target.

Original R30-017 board **FEN**, white to move: `5rk1/pp1bqppp/6r1/3pP3/3N4/2P1R3/PP2QRPP/6K1 w - - 25 36`. This experiment used the *board FEN only*, **not complete original repetition and game history**. One exposed position is not a new game-disjoint held-out cohort.

## Exact native results

All three candidates had **the same 45 legal immediate Black replies** after the forced White candidate. We enumerated all replies rather than source-ranking a top-k subset. Each candidate/reply leaf received independent Berserk searches to depth 10 and 12, repeated twice with a fresh UCI game identity: `3 × 45 × 2 × 2 = 540` actual searches. No leaf was dropped, and every leaf returned a completed finite centipawn evaluation. Across the original JSON, **every one of 270 paired replays was bytewise identical in parsed score, depth, actual node count and PV**. Total measured native search work: **14,596,738 nodes**.

For each root candidate, the value below is the **minimum** White-point-of-view referee centipawn evaluation over all legal Black replies. Higher is more favorable to White. It is **not** the original Stockfish root score.

| Candidate | Depth10 worst White cp | Depth10 worst Black reply | Depth12 worst White cp | Depth12 worst Black reply |
| --- | ---: | --- | ---: | --- |
| **Qf3** `e2f3` (original source selection) | **+74** | `h7h6` | **+72** | `d7e6` |
| **Qd3** `e2d3` (source intervention winner) | +62 | `f8e8` | +60 | `a7a6` (tied with `f8e8`) |
| **a3** `a2a3` (original referee rival) | +53 | `g6g5` | +49 | `g6g5` |

At both depths the finite worst-reply ranking is **Qf3 > Qd3 > a3**. Thus, for this board and this finite independent referee, the source intervention's changed recommendation **does not imply** that Qd3 surpasses Qf3 in minimum-reply value. The two independent referee depths agree on the ranking, but their numerical scores and worst-reply identities change.

## Matched-reply conditional preference, not a context-free ranking

Because all three candidates share the exact same 45 Black reply identifiers, we can compare each candidate under the **same Black response** instead of comparing only their separate minima. Below `first higher / tied / second higher` counts each of 45 legal reply moves once.

| Same Black reply | Depth 10 | Depth 12 |
| --- | --- | --- |
| Qf3 vs Qd3 | **33 / 1 / 11** | **34 / 1 / 10** |
| Qf3 vs a3 | **28 / 0 / 17** | **30 / 0 / 15** |
| Qd3 vs a3 | **18 / 1 / 26** | **22 / 2 / 21** |

This is a new useful discriminator: **the worst-reply ranking Qf3 > Qd3 is preserved at both depths, but strict Qf3 dominance over all legal replies is FALSE**. At depth 12, Qd3 scores higher than Qf3 for ten Black replies, and the two tie for one. A universal strategic claim like “Qf3 is better regardless of Black's response” is therefore rejected under these finite measurements.

Notice also that Qd3's **minimum** is stronger than a3's, while more depth-10 individual Black responses favor a3 over Qd3 (26 versus 18). Minimum robustness and the proportion of response identities showing an advantage are different estimands; the latter is **not** a frequency-weighted opponent policy or win probability.

## Evidence source and custody

- [R37 full original native ZIP, now preserved in C3X Drive 04_SEALED_RESULTS_COURTS](https://drive.google.com/file/d/1axG3y0LQnFNP9AQSutYfDcGhj4suviUa/view). Artifact ZIP SHA256 `5c3ed07315986fe2336f9ee4481c6a2de825285de343169a78d8a403d4eb61e6`. After Drive upload, direct downloaded readback had the **same SHA256** and both ZIP members passed CRC.
- Native 540-search JSON SHA256 `0fa5eadedbdff69b692f1d5d713a4a7649f90f57bfb480eb5f738eccb4bd4fcd`; original [GitHub Actions artifact #14691693392](https://github.com/WhoSia/C3X/actions/runs/44866204367/artifacts/14691693392).
- R30 original TWIC1664 experiment remains immutable in [Drive](https://drive.google.com/file/d/1BMSvffPHCzNQXpSjpQlxD9BihJwn8neM/view) (SHA256 `b42d19601f98fb00ff00e03fb7881bff3bd93114dc9c7b3bcd5876263727449e`). That prior full-history Stockfish intervention and this FEN-only independent referee are **different experimental worlds**.
- [R38 source replay audit](../harness/c3x_030_r38_reply_court.py) separately recomputes legal replies, all raw leaf values, candidate minima and same-reply conditional preference. Its read-only CI should be cited as an independent *derived data* validation only after a green run; not as additional native searches.

## Decision and limitations

**Observed:** a physically intervened final bestmove change in R30, independent 540-search FEN-only finite referee that retains Qf3 as the highest worst-reply candidate, and ten depth-12 legal replies where Qd3 has a higher response-conditioned value. **Not observed:** true exact source event → TT/history → root mediation, whole-history legal-reply value, independent-game generalization, or any human learner transfer.

These findings are incompatible with identifying “the search mechanism made the engine pick Qd3” with “Qd3 is independently strategically superior to Qf3.” They reinforce the need to represent source choice causality, conditional future chess value and learner meaning as separate evidence dimensions rather than collapse them into one score.

The next-version opening question is thus **whether an intervention-stable reduced decision state predicts source move contrasts and supports separately validated conditional chess plans**, not a claim that R37 established a winning plan.
