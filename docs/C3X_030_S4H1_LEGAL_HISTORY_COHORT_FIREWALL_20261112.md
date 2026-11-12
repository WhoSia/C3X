# C3X 0.30 — S4-H1 Legal-History Cohort Firewall (C3X 33)

Date: 2026-11-12 KST. This continues C3X 32 without resetting the 0.30 research lineage.

## Why this gate exists

S4-H0 sealed 12 researcher-authored, deterministic and legal opening histories: four development game histories and eight untouched holdout histories. Two FEN snapshots (plies 8 and 10) share each game's lineage, so 24 FENs are NOT 24 independent games. These are not independently sampled human games and are not the older 0.29 prospective 7/8 cohort.

S4-H1 protects identity, history and outcome-blindness **before** any comparative claim.

## Added files

- `harness/c3x_030_s4h1_cohort_firewall.py`: strict row key set, positive/negative data-leak firewall, legal chess replay, reconstructed FEN equality, within-game prefix consistency, exact 4/8 game split and game-disjoint separation.
- `harness/test_c3x_030_s4h1_cohort_firewall.py`: eight checks covering valid pilot, forged FEN, illegal move, altered history, outcome leak, game identity collision, missing snapshots and false random-sampling assertion.
- `.github/workflows/c3x-030-s4h1-cohort-firewall.yml`: read-only CI, pinned chess validator, test and identity artifact upload. The workflow does not make commits.

## Evidence boundaries

- SOURCE: existing frozen S4-H0 author-coded game histories. The S4-H1 workflow re-generates from checked-out source and compares the digest of **that generated file** with itself passed as an argument. This does **not** independently certify the previously archived historical original SHA or prospective chronology. To certify that, independently compare with the first S4-H0 pre-outcome artifact preserved outside the evaluator and record its immutable SHA before any outcomes.
- No Stockfish search or new causal computation is performed by this audit.
- Any CI PASS establishes contract execution, not scientific superiority.
- No independent method labels are supplied or fabricated.
- Existing S4-G/R1 physical-masking evidence and 0.29 prospective 7/8 HOLD remain unchanged.

## Next gates

1. Confirm S4-H1 CI and inspect actual regression logs; correct failures instead of claiming success.
2. Retrieve and cross-check first pre-outcome S4-H0 artifact bytes against the S4-H1 data identity.
3. Lock an outcome-independent S4-H2 execution protocol: paired masked/sham invocation and root-value anchor integrity; isolate within-game dependence.
4. Conduct independent empirical F3 SARFA/response/native/fusion risk-coverage comparison only after externally grounded independent labels exist.

## Status

IMPLEMENTED in GitHub; CI runtime result NOT YET CONFIRMED. No new engine searches. Method superiority HOLD.
