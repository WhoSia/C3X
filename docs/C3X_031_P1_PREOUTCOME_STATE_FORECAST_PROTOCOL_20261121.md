# C3X 0.31/P1 — First Active Scientific Unit: Frozen Search-State Sensitivity Benchmark

**Formal stage:** C3X 0.31; **approved version name**: *Intervention-Stable Decision-State Abstraction: Minimal Search-Memory Causality, Robust Chess-Plan Transport & Human Explanation Validity* (the user explicitly requested to proceed under this name, 2026-11-21). **Unit:** P1 = *Can pre-treatment native search-state information predict whether a source intervention changes the eventual recommended move beyond ordinary public search observations?* The comparison is motivated by 0.30 R33–R35, but no general mediation is assumed.

**Evidence class:** historical source-exposed **RETROSPECTIVE DEVELOPMENT AND PROTOCOL IMPLEMENTATION**, not independent prospective testing. The R33 TWIC1671 outcomes were published before P1 was designed. P1 must never claim blinded novelty, newly executed Stockfish searches, or intervention-stable sufficiency merely because an estimator fits these data.

## Origin, denominator and exclusion

- Entire original [R33 TWIC1671 native archive, 64 game histories, 128 selected physical events](https://drive.google.com/file/d/1C3RZRyibwCthOaoWOLYu4IZNzdGlPJg8/view); ZIP SHA256 `e72ba91c0ffdbbb075642f044706d356fca84b4fa257a3ebcb7755db5837d8bd`, SHA manifest **1,414** entries.
- Derive precisely **128** records: one preselected null-ineligible and one null-eligible target from each of 64 complete unique game histories. Main intervention is `both_off` (suppress both futility and, when eligible, null return) versus the natural unmasked reference. The null-ineligible extra null toggle was previously confirmed as a no-op; **do not count `futility_off` as independent data for that stratum**.
- Frozen target's `C3X_R33_OPEN` fields and unchanged engine `discovery/{case}/observed/stdout.txt` are collected *before interpreting the treatment-arm result*. Refusal rules cover broken SHA, duplicated games/events, absent physical treatment contact, changed event identity, mismatched cold repeats, missing public score lines, and any nonexact baseline.
- **Response**: `y=1` if `both_off` final UCI `bestmove` differs from original untouched recommendation; `y=0` otherwise. Count only physically reached and source-matched targets. This is a *conditional source-intervention sensitivity phenotype*, **not** a strategic superiority label.
- The 64 source games belong to **16 tournament event families**. For all out-of-sample prediction, hold out an **entire family**, train on the other 15 and never allow family ID, FEN, PGN, case ordinal, exact move UCI, position ID or outcome-dependent target re-selection as a predictor. The two correlated intervention targets from the same game remain in the same fold. The 16 families are not guaranteed iid; group them to prevent easy event/family leakage.

## Prior-specified models

All classifiers return a probability of a final move change. Use identical deterministic regularized logistic machinery, train-fold-only centering and variance scaling and identical partitions.

- **M0 no-state benchmark:** Jeffreys-smoothed train-only prevalence `(positives+0.5)/(training_size+1)`.
- **M1 GUI/public baseline:** untouched public original completed depth, final displayed numerical score normalized to cp if score type cp (otherwise HOLD), and the length of the latest public PV. **No** source event info, target root move, intervention response or event family.
- **M2 pre-treatment source-state augmentation:** M1 plus physical pre-treatment event ply and depth, futility slack `floor-beta`, selected event's progress `nodes/32000`, the null-eligible stratum, `root==original recommended move`, and `attempt`. Each is admitted from source *OPEN*, not a treated read or target `CLOSE`.
- **Not allowed:** response `C3X_R33_CLOSE` value, changed number of replies, treated completed depth, last changed root candidate, masked target return or treatment outcome, even if strongly predictive; these are **post-treatment mediators/outcomes**, not pre-treatment forecast inputs.
- **No hyperparameter search on R33 labels**: fixed ridge penalty, fixed gradient iterations and learning rate specified in the executable before evaluating the file. Training features are scaled using only training family records.

## Predefined metrics and stage gates

- Strict out-of-event-family out-of-fold predictions for all 128 targets (16 folds), saved as row-level predictions and original labels; compare M0/M1/M2 on **Brier score, log-loss, average precision, recall at threshold 0.5 and positive coverage**. Report raw counts by event family and null-eligibility stratum. Never present event-level rows as independent games.
- For model improvement report a **family-cluster bootstrap** (fixed seed, 2,000 resamples of the 16 event-family groups) on the difference `Brier(M1)-Brier(M2)` and `Brier(M0)-Brier(M2)`; a positive mean difference is improvement. Report interval and observed rather than pretending a new randomized study.
- Gate `P1_METHOD_PASS` only for full manifest/identity, no-leak feature checks, heldout partition contract and real archived-label parity. `P1_RETROSPECTIVE_PREDICTIVE_SIGNAL` only if M2 improves **both** M0 and M1 Brier by at least 0.01, with **both** resampled 95% lower bounds >0 and average precision not worse than both baselines. Otherwise mark `HOLD_NO_SOURCE_STATE_GAIN` or `NEGATIVE_TRANSFER` as applicable.
- **Regardless of model score**, interventional mediator sufficiency / minimality remain `HOLD`; predictive correlation of pre-treatment features is **not** a state-transplant/rescue experiment. No reading/response/learning effect is inferred.

## Counterexample priority and first native follow-up

Classify the first opposing cases: large source-state predicted risk with no move change; source-event changes whose bestmove stays; and sudden bestmove flips at low predicted risk. For the most surprising cases, follow only **after** independent source lineage instrumentation and a pre-treatment snapshot restore design, with 0.30 R35's specific TT/history versus node allocation ambiguity explicit.

The later prospective P2 needs a new issue (outside R33 TWIC1671, R29 TWIC1663, R30 TWIC1664 and other exposed histories), game-family disjoint to training, frozen **before** native outcomes and drawn to an original numerical denominator. It should measure the trained source-state abstraction in real new engine interventions, not adjust definitions to recover a desired gain.

## Custody and owner

Original R33 ZIP resides in Research OS Drive `C3X/04_SEALED_RESULTS_COURTS`, with source publisher The Week in Chess credited. Only small non-game-reconstructing aggregate/feature receipts and executable code should enter GitHub, and no CI action may write commits. Notion contains the governing scientific verdict, including nulls and version migration. Cite R33 native published cohort correctly, not as newly acquired 0.31 evidence.

## P1-A1 Amendment — retain score bounds as bounds (before model training)

The immutable R33 **untouched** native public logs have terminal `score cp` lines with three different semantic types: **34 exact/unbounded, 23 upper bounds, 7 lower bounds** among 64 source games. No intervention outcome labels or fitted models were consulted to discover this encoding issue. The original P1 text requiring an exact terminal cp value would lose 30 entire games (60 events) and violate its promised 128-event denominator.

**Decision:** retain all 64 game histories and all 128 selected targets, add two M1 public indicator features `public_upper_bound`, `public_lower_bound` (both false means no bound), and keep `public_score_cp` as a *numeric published threshold with an explicit bound label*, **never** an exact centipawn estimate for those 30 games. Do not claim two bound scores are intrinsically comparable. The same bound indicators must be included unchanged in M2. Public score type remains cp in all 64 source logs; mate results still require HOLD or a separately locked protocol.

**This is an outcome-blind data-schema correction, not a changed success threshold.** The original score calibration, source event features, family folds, fixed model hyperparameters, error reporting and scientific promotion restrictions are unchanged. A preprocessing refusal because of the initial exact-only restriction is preserved as an engineering finding, and the revised extractor explicitly checks 34/23/7 from genuine original stdout.
