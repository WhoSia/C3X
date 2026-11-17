# C3X 0.30 S4-L/R17 — Extra defense removes the only trace gain

2026-11-17 KST. R17 repeats the named-piece objective on the same frozen R16 questions and menus. It requires a successful capture to survive every immediate final Black reply. [Sensitivity protocol](C3X_030_S4L_R17_LAST_DEFENSE_PROTOCOL_20261117.md) · [R16 and source design](C3X_030_S4L_R16_NAMED_PLAN_WITNESS_RESULTS_20261117.md).

| Endpoint | Positive leaves of 64 | Public / Trace recovery | Unequal same-reply pairs of 32 | Public / Trace recovery of both labels in unequal pairs |
| --- | ---: | ---: | ---: | ---: |
| End after White's second move (R16) | 28 | 27 / 28 | 10 | 9 / 10 |
| Include Black's immediate last defense (R17) | 16 | 16 / 16 | 8 | 8 / 8 |

R17 removes every witness in 12 of 28 formerly positive leaves. Invariants on all 64 leaves preserve menus and ensure every four-ply first-move witness is present at three plies. A separate literal move-replay verifier checks all 34 original first-move witnesses using legal move expansion instead of computing the final defender's material change without playing the move. Fifteen first moves are lost. The audit shares the named-piece identity tracker and the material evaluation, and verifies the final-defense search implementation.

## Two useful disagreements

- **Round 1.3, Qb3 ...a6:** R16's sole witness is the trace-proposed Qxb7. Black has the legal defense ...c5, then after Qxa8 replies ...Qxa8. White gained a pawn and rook but lost a queen, changing the post-reply material balance by -3. The literal replay confirms no alternative White finisher after ...c5 secures this named goal. The three-ply witness is valid at its declared cutoff. It fails with Black's final move restored.
- **Round 2.2, Rg1 versus Ke2, target h8 rook:** ...Rg8 moves the target and the goal survives after Rg1, witnessed by both Nd6 and Rxg8. It fails after Ke2 against the same ...Rg8. After Rg1, each of ...f5, ...h5 and ...Ra7 destroys the goal over the same bound. The selected candidate and the reply are both necessary to state the witness scope.

## Post-result diagnosis: the public menu is saturated

Every settled positive leaf has a successful immediate capture of the named target. A successful immediate capture was available in 27 of the 28 short-horizon positive leaves. Only Qxb7 requires a preparatory move in the three-ply run and that witness fails the final-defense test. The first public slot covers 14 of 16 settled positives and the first two cover all 16. These counts come from intersecting each exact witness list with the leaf's legal captures of the tracked target, and with the prefixes of its frozen public menu.

Both policies find all 16 settled positives in this sample. In a next sample, screen for a common reply after which the named target cannot be captured immediately. This admission decision can use legal moves without observing the delayed capture outcome. Continue to admit both plan successes and failures. That design measures whether the internal move nominates a successful preparation when a direct-capture shortcut is unavailable. Testing additional witness recovery requires room for a stronger policy to improve at the same public menu budget. The four-ply safeguard addresses immediate recapture and promotion, leaving longer compensation and other named strategic motifs as distinct outcomes. [Sealed raw and repeated evidence](https://drive.google.com/file/d/16wRXf7bKyISr-j3r8x55mqcE_34E2qSo/view).
