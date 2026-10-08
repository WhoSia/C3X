# C3X 0.13 P6-R2 — First Real-Game Birth-vs-No-Birth Same-Queen Pawn-Capture Pair

Status: NEW OUTCOME-BLIND ENGINE PRECOMMIT, developmental only.

P6-R1 fixed first passed-pawn birth per each of 16 original broadcast groups BEFORE any new engine score. Exactly ONE of nine birth-bearing source games had a strict matched legal alternative preserving moving piece, departure square, capture status, captured-piece type and promotion status. Do not replace the other eight HOLD sources.

Selected natural historical FEN:
1r3nk1/1pp1bqp1/6pp/p7/3PNQ2/2P4P/PP3PP1/4RRK1 w - - 0 27
Source first natural passed birth at ply53, White queen from f4:
- A f4c7: captures black pawn c7 and makes a white pawn passed;
- B f4h6: captures black pawn h6 and does not create a newly passed pawn.
Both are legal, same queen, one captured pawn. They also change OTHER strategic features, so no isolated causal treatment.

Propose two independent cold Stockfish16 runs at EACH completed depth 8/12/16, root pair frozen A/B, root side white score in cp only. Freeze exact binary SHA, source FEN and legal move check. Report mate exclusion, PV-root identities, same-depth comparability, repeat disagreement, move preference sign at every depth and whether |A-B|<=50cp in ALL three depth regimes. If not near-equal or if sign flips, HOLD. If all pass, still single-game DEVELOPMENT_ONLY, not concept causality or cross-engine validation. No post-outcome alternative adjustment; no human outcome.

Parent P6-R1 matched-source yield: 1/9 birth games, 8/no matched rival; 6/no passed birth games, 1/Chess960 source HOLD. This denominator is binding, not a false independent cohort of root examples.