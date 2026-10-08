# C3X 0.13 P8-E1 — Source-Frozen Cross-Architecture Root Preference Diagnostic

**Status:** PRECOMMIT BEFORE EVERY ETHEREAL P8-E1 SCORE; developmental diagnostic, NOT independent confirmatory source replication, mechanism proof or C3X 0.14 gate. No 0.14 title or version opening.

## Source/result selection fixed
Use the WHOLE, unchanged P7-R2 cohort artifact `c3x-013-p7r2-new32-cold-tactical-depth-qualification`, actual read-only run 37727921874. Source PGNs pre-frozen by September 2026 Lichess groups ranked 17–48; original source archive SHA256 27a39d035767a30901b89602f33f2a7b27d4ab5025842071165fa079f8fff1df, selection SHA256 e5ca78464ef6bb2e95271c12428c47e8f9535efca9674d1048aed029ef1584c0. All 32 initial broadcast groups, 29 legal games, 8 P7 tactic-filtered pairs, 21 without filtered pair and 3 source HOLDS must remain in denominator. Inherited Stockfish cold-selected move pairs and P7 completed-depth scores are FROZEN; don't select pairs from Ethereal scores.

## Independent engine and provenance
Pin open-source **Ethereal classical (USE_NNUE=0)** source commit `0e47e9b67f345c75eb965d9fb3e2493b6a11d09a` of `https://github.com/AndyGrant/Ethereal`; build from `src/makefile` with `make basic CC=gcc`. This codebase is authored by Andrew Grant, distinct from Stockfish, licensed GPL-3.0 (retain copyright and source reference). This is the *open-source classical code configuration*, NOT the separately distributed current commercial neural Ethereal executable, NOR the archival historical P16 binary. Source and executable SHA256 plus UCI name/options must be recorded.

Use ONE thread and 16MB hash when supported, no tablebases. For EACH frozen P7 tactic-filtered root pair, run two independent cold engine restarts at COMPLETED depths 8,12,16, both root candidates through MultiPV2 restricted legal root moves. Record original-mover cp perspective, root PV (at least first 8 moves), depth and restart scores; HOLD on mate-score, missing PV, depth mismatch, repeat divergence, unsupported UCI MultiPV, engine crash or timeout. Emit engine version/license/source SHA and executable binary SHA.

## Predetermined comparisons and limitations
Per group report Stockfish root preference sign and Ethereal sign under each equal NUMERIC depth. Cross-engine same-depth is NOT equal effort, searched nodes, evaluation scale or methodology; never subtract two engines' raw cp values as if calibrated. "Sign concordant" is an observational directional agreement only, not causal transport. Compare all 8 P7 frozen pair signs, including seven Stockfish depth-unstable or support-HOLD cases; report strict P7 scientific criterion as only 1/8 stable across Stockfish depths, not promote it through an unrelated Ethereal preference.
Define **P8 descriptive directional transport** only if a P7 pair has repeat-comparable positive or negative score orientation at 8,12,16 in BOTH engines with no sign reversal; even this would earn *no* concept-level transport or causal explanation. A zero-gap at any depth is abstention, not matching orientation.

If Ethereal classical code cannot compile or execute, preserve SOURCE/BUILD_HOLD; do not substitute another engine, change the commit, drop groups or invent results after looking at failures.

## Following stages
P8-E1 is a cross-architecture *observation* of existing P7 selected worlds. P8-E2 must prospectively seek actual born/not-born legally and tactically matched roots from NEW source/competition independent groups, with opponent replies and concept-targeted intervention/sham; if support zero, hold. 0.14 cannot open based merely on engine score agreement, vocabulary, or this diagnostic.