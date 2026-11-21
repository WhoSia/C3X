# C3X 0.31/P2 — Outcome-Blind New-Game Transport Prefreeze (Source Acquisition Gate, NOT YET EXECUTED)

**Scientific status, 2026-11-21:** Candidate prospective follow-up **protocol committed before any P2 engine interventions**. This is **not** a pre-registered completed sample, not a newly run Stockfish search, and not an independently successful P2 study. Source archive raw byte identity, overlap audit, frozen selection receipt, engine patch/binary and P2 intervention signatures must all be locked before calling this a true prospective native cohort.

## Why P2 is justified after P1

P1 actually rechecked 0.30's 64-game/128-event R33 data and held out its 16 historical tournament event families. M2 source-open fields improved retrospective Brier only +0.00328 against M1, with uncertainty spanning zero and true flip recall 0/11 at threshold 0.5. Those data were exposed before P1; they do **not** establish transport to a new real-game cohort.

P2 asks a more limited, decisive question: *When a frozen physical-event selector is applied without consulting outcomes to a new independent game/event-family source, does source-pre-treatment information improve prediction of the same final-bestmove sensitivity phenotype, and are its false positive/negative cases reproducible in original code?*

## Candidate source, with explicit nonadmission

Publisher [The Week in Chess 1670](https://theweekinchess.com/html/twic1670.html), Mark Crowther, issue **1670**, **2026-11-09**, publicly listed as **8,391 recorded games**. It is **not** TWIC1663/1664 (P1 predecessor R29/R30), TWIC1671 (0.30 R33 / 0.31 P1). The issue number alone is **NOT sufficient to claim game-disjoint novelty**: identical tournaments and even identical complete games can reappear between different weeks. TWIC1670 is a *candidate* source; an issue/PGN SHA and an overlap-censored cohort must be acquired and sealed first. All publisher rights and original attribution continue to apply.

The true prospective frozen sampling receipt must enumerate the publisher file SHA, physical PGN parse count, valid-game count, rejected game/family/board overlaps against **all** 0.29/0.30/0.31 source-development cases (including the P1 R33 group), an original sample seed and exact histories, even if zero games remain. Do not label an unknown group as independent.

## Fixed dataset selection rule (BEFORE treatment scoring)

- Target at most **64 distinct complete-game histories**, one checkpoint each; **hold out whole tournament events** from the 16 R33/P1 event families and every preceding development cohort. Use event-family string normalized only by Unicode NFC/trim and source-published event header; do not use an outcome-informed name mapping.
- Candidate checkpoints are the game's legal full-history positions at the **first predetermined ply in [40, 41, 50, 51, 60, 61, 70, 71, 80, 81]** whose board meets the original R33 source selection prerequisites. Evaluate potential eligibility only on untreated baseline source traces; prefer deterministic round-robin source-game ordering frozen before touching any intervention.
- Choose at most one game per normalized event family until available distinct families are exhausted; if multiple games of same family are later sampled, keep them **together** in any uncertainty estimate or training split, and state family-level effective sample size.
- Selection must use only original PGN metadata, legal move histories and **untreated** source event logs. It must never use downstream `both_off` move changes, independent referee values or fitted P1 prediction risk to choose the cases.
- Within each selected game, nominate the same two R33 source-eligible early-return strata (`null_eligible=0,1`) with frozen tie breaking (minimum nonnegative futility-floor slack, first event ordinal tie). Record **all no-contact/no-eligible cases as explicit denominators**, not silently replaced. The recorded sample may have less than 64 eligible games, and an underfilled denominator is a scientific HOLD, not a new eligibility threshold.
- Freeze raw SHA and matching code/binary/NNUE SHA **before** any treatment case is executed. Require full UCI initial history and same TT/hash/thread controls as R33; preserve source-side physical event ID, parent/root candidate, attempt, public score+bound flag and target signature.

## Prospective model transfer: lock, do not retrain on heldout labels

- Transport the **feature definition** fixed in P1: `M0` previous train-only event rate; `M1` untouched public depth, published cp threshold and bound indicators, full PV length; `M2` adds physical open event depth, ply, futility slack, progressed nodes, attempt ordinal, null eligibility and `root==original untreated bestmove`.
- Genuine P2 predictive testing requires **model coefficients/scaling fitted once on all P1 R33 games, sealed with SHA before P2 event outcomes**. P1 cross-validation alone does not provide a locked final model artifact. Build this frozen fit as an independent P2 preoutcome artifact. Preserve P1's fixed ridge `0.02`, gradient iterations `900`, step `0.10`, and numerical feature transformation; no P2 refit or threshold tuning after outcomes.
- Forecast the binary **intervention bestmove changed** outcome for each actually targeted event; evaluate Brier, log loss, AP, recall at 0.5 and calibration/abstentions, preserving the full natural event family denominator. The scientific gain threshold remains the earlier P1 ≥0.01 Brier difference over both M0 and M1 with strict >0 family-cluster interval lower bounds, and AP not lower. Because P2 is new, **report both** that fixed threshold and count of independent families; do not label tiny success samples as confirmatory.
- Source treatment arms: unchanged and source-observed controls, physically nominated futility disabled, futility-plus-null disabled, irrelevant-target sham, exact repeat, and restoration where the actual source patch supports it. The binary y is tied **only** to the frozen primary `both_off` intervention, not to an opportunistically selected successful arm. No-contact and observer-affecting controls mark HOLD and are counted.
- Additionally report original vs treatment completed depth, node count, root menu and bound-labeled score to detect budget-mediated changes. A new final move is **not** independent strategic superiority, even if the source event is physically contacted.

## P3 state transplant is a separate scientific gate

The P2 prediction study **does not certify minimality or causal mediation**. Only after the prospective source experiment can P3 define **physical pre-contact checkpoints** with synchronized TT occupancy, history heuristics, stack fields and remaining search budget. Compare a single state-family transplant with matched sham and true restoration, separately record whether the causal effect is rescued or blocked, and forbid invisible node-budget adaptation. The P3 natural mediator route must be supported by source-level read/write events, not inferred from the logistic model weights.

## Predeclared failures and stop

1. **Pre-freeze failure:** wrong published archive SHA, PGN corruption, overlapping tournament/game families, insufficient independent groups, or missing original source trace → `HOLD_SOURCE_PREFREEZE`; do not execute treatments.
2. **Physical execution failure:** event not reached at exact signature, observer changes baseline, sham creates a move flip, repeated logs disagree, target not contacted → explicit `HOLD_SOURCE_PARITY_OR_CONTACT`; report all cases.
3. **Predictive null:** M2 fails either fixed Brier threshold or 95% positive improvement bound or AP condition → `NEGATIVE_PROSPECTIVE_TRANSPORT`; do not revise feature list on those outcomes.
4. **Mechanism null:** total effect changes but source-state transplant cannot rescue it → `HOLD_MEDIATOR_UNIDENTIFIED`, not a no-effect result.
5. **Chess validity:** actual new winning move under source treatment not referee-covered or a plausible plan fails under actual legal opponent replies → retain both source effect and independent strategic negative.

**Administrative freeze vs experimental freeze:** This document freezes the *method and admission conditions*. The physical PGN/game sample and source intervention recipient IDs have **not yet** been frozen. Stage status remains `P2_PROTOCOL_ONLY_NO_NATIVE_OUTCOME` until raw acquisition, source overlap and pre-treatment selection receipts exist.

**Prior literature:** [P1-L causal abstraction prior-art/vacuity audit](C3X_031_P1_LITERATURE_CAUSAL_ABSTRACTION_AND_VACUITY_20261121.md). Physical source state and complexity constraints are necessary to avoid a vacuous all-information trace mapping. Generic causal-abstraction theory is already established in Geiger et al. (2025) and others.
