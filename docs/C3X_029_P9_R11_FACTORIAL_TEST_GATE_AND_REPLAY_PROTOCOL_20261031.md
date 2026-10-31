# C3X 0.29-P9-R11 — Factorial Adjudicator, Testable Claims and Replay Stop Gates

2026-10-31. This is a NEW CODE ARTIFACT and static research protocol, NOT a fresh engine run.

## Actual code created as small commits
- tools/c3x_029_p9_r11_t3_public_factorial_adjudicator.py — fail-closed published T3 schema/2-game/4-arm validation; categorical outcome and indicator-level 2x2 interaction; explicit candidate-specific margin NOT_IDENTIFIED and out-of-budget robustness UNMEASURED.
- tools/test_c3x_029_p9_r11_t3_public_factorial_adjudicator.py — synthetic two-game cases, one positive interaction, one negative, invalid schema/incomplete arm/duplicate-game tests.
- tools/test_c3x_029_p9_r11_original_public_receipt.py — exact original GitHub receipt backed assertions for May game2 b1b4, game11 negative and 2 distinct chess games.

## Execute at repository root
`python -m unittest discover -s tools -p 'test_c3x_029_p9_r11*.py' -v`
`python tools/c3x_029_p9_r11_t3_public_factorial_adjudicator.py --receipt c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json --out /tmp/c3x_p9_r11_public_adjudication.json`

Run these locally or in a human-controlled CI environment. As of THIS commit, code creation and static inspection completed, not an executed Python verification receipt. GitHub access in this session does not permit starting a new Actions workflow without explicit provenance and user governance; no execution is claimed.

## Interpretation
Original T3 May game2 four-arm bestmoves (e1g1,e1g1,e1g1,b1b4) give binary indicator interaction +1 *in this particular postselected development board*. May game11 (c7d6,d8b8,c7d6,d8b8) gives 0 for the joint-world chosen candidate. Cannot compute any b1b4-vs-e1g1 *candidate-level margin* from terminal cp (-8,-8,+1,-4) across four different searches. Multiple configurations and depth-dependent moves are valid potential outcomes; original exact cold pairs do not certify depth/hash/NNUE/threads transport.

## Evidence gates and negative controls
G0: source/position/engine/pinned original cold replay parity including each arm bestmove+nodes+score and event contact.
G1: no reproduction, stop mechanistic promotion. Different depth or hardware implies distinct estimand, not technical parity.
G2: per-root-candidate, per-aspiration-attempt search start/completion and comparable exact/upper/lower scores, stored before/after. Child search return is not stored root score (0.15-P10-R2 already demonstrated this).
G3: heldout source-disjoint game-clustered repeat and chess legal-reply audit; avoid inventing universal bestmove.
Rights: no original PGN, player or private source key published.

## Researcher governance
Microcommits should correspond to independent testable logical units, not an arbitrary count. If any future test fails, write a new corrective commit preserving failed history.
