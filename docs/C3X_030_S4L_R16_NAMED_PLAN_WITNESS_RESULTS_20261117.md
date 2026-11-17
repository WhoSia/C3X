# C3X 0.30 S4-L/R16 — Named-piece witnesses under equal menu slots

2026-11-17 KST. The [protocol](C3X_030_S4L_R16_NAMED_PLAN_WITNESS_PROTOCOL_20261117.md) fixed the named enemy piece, candidate pair, list of four common replies and short-horizon material objective. The [menu freeze](../receipts/C3X_030_S4L_R16_NAMED_PLAN_MENU_FREEZE_20261117.json) was committed before exact scoring. The source is the TCEC S29 Entrance League PGN with 240 games. The R10 even-ply eligibility rule gives White to move in all selected positions. R14 opening prefixes were excluded. Twenty-four near pairs were screened and eight admitted. The public continuation after the first candidate nominated a shared physical victim. Nomination did not inspect the legal-plan result.

## What the panels tested

Every leaf starts after the candidate and the same forced opponent reply. A first move proves the predicate if, for every legal Black defense, there is a legal second White move ending with that named piece captured and no decrease in material balance relative to the leaf. The target is tracked if it moves. Earlier legal termination is evaluated at that terminal position. A panel checks three first moves by the same exact continuation evaluator. Public uses immediate captures, then its UCI leaders and legal fill. Trace adds one candidate by replacing the final non-capture slot. Both menus come from the same pinned Stockfish process and do the same number of first-move checks. Their continuation enumeration effort can differ.

## R16 result

- 64 post-reply searches, 768,648 reported Stockfish nodes; 64 judged leaves and 32 complete same-reply contrasts. A source candidate replaces one public slot on 29 leaves.
- The exact three-ply oracle finds 28 positive leaves. The public panel recovers 27, augmented recovers 28. One net gain, zero losses.
- Ten common replies have unequal truth labels for the two root candidates. Public recovers both labels on nine of these ten, augmented on ten. Across all 32 common replies the complete-pair label count is 31 versus 32.
- Ten leaves begin with the victim relocated by the common reply; four have a plan witness. Among 18 candidate-side alternate tests where the nominal response allows a plan, four alternatives defeat it. There are 48 nominal versus alternate comparisons overall.

The one gain is round 1.3, Qb3 versus h3, after ...a6, targeting the a8 rook. The public menu for Qb3 is h3, Ra3, Bg5. Trace retrieves Qxb7 from an ordinary in-window PV-update event in iteration 7, and it is the sole three-ply first-move witness. After Qxb7 the exact short-horizon proof finds a rook capture following each of Black's 30 defenses. The h3 branch has no such witness. See [R17](C3X_030_S4L_R17_LAST_DEFENSE_RESULTS_20261117.md) for why the extra result is sensitive to the cutoff.

Questions and exact proof files reproduce byte-for-byte. Replayed Stockfish logs and menus match after only the UCI stdout time and NPS values are removed. [Raw and repeated receipts](https://drive.google.com/file/d/16wRXf7bKyISr-j3r8x55mqcE_34E2qSo/view), archive SHA-256 `409a8e6707ad770de15507e3247389c136a771b9f570d65597ba2d1702c0136b`.

## Reproduce

With python-chess and pinned R4 Stockfish 16, use `c3x_030_s4l_r16_plan_source.py nominate ENGINE PGN R14_QUESTIONS`, then `freeze ENGINE GOALS`, then `c3x_030_s4l_r16_plan_score.py GOALS MENUS MENUS_SHA256`. The same sealed inputs and the flag `--settle-final-defense` produce R17. Parent R14 questions are in its [archive](https://drive.google.com/file/d/1HFathAD2eGoPYRX5p9ciQm91uCMOao0R/view).
