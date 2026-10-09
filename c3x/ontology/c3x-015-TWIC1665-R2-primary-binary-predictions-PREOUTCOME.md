# C3X 0.15 P1 Binary Prediction Preseal — TWIC R2, Before New Engine Outcomes

Scientific state: **PREDICTIONS FROZEN, TREATMENT UNOPENED**. This file is pre-outcome, not successful external validation.

Frozen TWIC R2 source-only PIN64 manifest SHA-256:
`1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534`

Historical training: S29 root-object SEE 40 games (13 flips); S28 root-object SEE 64 games (17 flips); exactly 103 unique FENs, with 29 positive changes after S28 duplicate suppression. Historical outcomes were revealed before 0.15 and are DEVELOPMENT/EXPLORATION training data only.

Outcome to predict: Stockfish16 CLASSICAL depth12 pristine OFF vs original-root-object-guarded SEE_UNMASK `bestmove` changes. 64 results ordered by the frozen R2 PIN world selection order, not sorted by model score.

- **B0 constant zero**: 64 all-zero predictions.
- **B1 law-only (Laplace smoothed five-feature law stratum)**: 
  `0000000000000100000100000000000000000000000000000000000000000000`
  — predicts 2/64 changes.
- **C1 law + source-only chess context logistic regression**:
  `1101011110110000001100010000100000100101110110101011101010111001`
  — predicts 31/64 changes. Uses exactly 13 categorical chess-law indicators and 11 pre-treatment normalized chess-board counts, ply and root legal move features, no FEN/event/game ID as model inputs.
  Solver scikit-learn 1.8.0 LogisticRegression lbfgs, `C=0.5`, `class_weight=balanced`, `max_iter=5000`, `tol=1e-8`, positive if uncalibrated sigmoid score >= 0.5. Do not interpret C1 score as a calibrated probability.

Frozen full binary model JSON SHA-256:
`70e626898d30d04fc1887d4b863c8c2f28d6af7d70cdc914873c1f6ae230481b`

Frozen full 64 world predictions JSON SHA-256:
`a4ebc45f8ab844e502aa507c64eb78f72371952c0512df676e4b33b0ccc4d172`

The complete files and exact training code are retained as independently downloadable conversation artifacts, pending durable byte custody. Binary predictions and their strict order are preserved here to prevent post-result relabeling. These predictions are **not** test results. Full historical Lichess dedup remains bounded HOLD; no TWIC Stockfish scores opened. See `c3x/ontology/c3x-015-P1-R2-repeated-law-context-fiber-prospective-contract.md`.
