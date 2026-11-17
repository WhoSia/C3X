# R20 learner pilot — Verified item and scoring

[Protocol](C3X_030_R20_LEARNER_PROTOCOL_20261117.md) · [comparison form](learner/C3X_R20_COMPARISON_KO.md) · [explanation form](learner/C3X_R20_EXPLANATION_KO.md) · [generator and scorer](../harness/c3x_030_r20_learner.py).

The transfer section reproduced byte-for-byte across forms, including the four FENs and the 8-minute instruction. Inside the worked example the only addition in the explanation form is the tracked rook, the legal Nd6+ witness, its three defenses, and the …b5 refutation of Qa4. The exact solver checked the terminal material guard. It also checked the transfer verdicts and every annotated entry. An independent synthetic response file exercised correct negative, false positive, abstention and valid positive submission. The key is generated separately from the participant forms.

Facilitator use: distribute only one form per participant. Collect answers with item codes T1–T4 and `answer` (`yes`, `no`, or `abstain`). Record any proposed move as `entry` in SAN. Run the script's `score --responses RESPONSES.json` mode with the frozen R17 goals. The score reports verdict and entry validity separately and treats a missing item as abstention.

The one-positive, three-negative item produces 75% raw accuracy for a participant who marks all four impossible. Report the positive item's correct verdict plus a valid first move, the negatives' specificity, and abstentions separately. A matched near-equal comparison of ordinary PV commentary and verified explanations requires a larger game-disjoint transfer set. This item is ready for a dry run with a board or a FEN reader. No participant observations were collected.
