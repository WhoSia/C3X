# C3X 0.24-P2 — Executed Descendant Search Lineage and Causal Certificate Falsification

**Status:** DESIGN PRECOMMIT ONLY / NO NEW P2 NATIVE EXECUTION / Version C3X 0.24 ACTIVE.

## Triggering negative evidence

P1 on disjoint August2025 Lichess games: 16 games, 64 roles, 64 genuine physical FIRST reader contacts, 6 root UCI flips in 2 games. Git-literal M3 identically predicts M0 in every role. Scores M0 58/64, M1 57/64, M2-depth11 57/64, M3 58/64. **M3 does not outperform no-change null.** This is a falsification of the current predictive advantage, not justification for model revision on the same data.

Native P1 CI #38076866358, literal model preseal a6d4b5f3af342d0d270697e74c2ba6de0497229a, [P1 canonical receipt](../receipts/c3x-024-P1-Aug2025-presealed-M0-M3-native-FIRST-prospective-negative-20261011.json). Do not re-use the August cohort for M3 model selection.

## Primary research question

On the original May2026 development cases (#11 F/STRICT qsearch, #2 O/STRICT quiet), does the exact SEE pruning-guard decision actually cause **the candidate move to execute `do_move`, the subsequent child search to enter and return, and a source-matched change in subsequent candidate/root survival**? A guard-pass alone is insufficient: another gate may prune the move before recursion.

## Ordered source certificates

- **C0:** Origin/legal position and license provenance (source-only SHA, immutable game identity).
- **C1:** Exact physical TT writer→reader and source SEE call identity, full ancestor keys, root candidate, frame and threshold.
- **C2:** T4 actual native `ACTUAL_CONTINUE` vs `PASSED_SEE_GUARD` with cold no-observer equivalence; T4 run #38072795238.
- **C3a (new):** Observed next relevant source milestone after guard: `CANDIDATE_ADMITTED`, `REJECTED_AT_LATER_GATE`, `DO_MOVE_EXECUTED`, `CHILD_ENTERED`, `CHILD_RETURNED` or `NO_CHILD_WITHIN_BOUNDED_TRACE`. A `PASSED_SEE_GUARD` must never be relabeled `CHILD_ENTERED` without a source witness. A recursive engine branch may be bypassed via LMR or other path; preserve event sequence rather than assume unique child return.
- **C3b:** Join these events with exact native position/parent keys, ancestor vectors and depth/window frame, then with root candidate return. Explicitly classify `PATH_DIVERGED` / `CENSORED` / `NO_CONTACT` rather than aligning logs by ordinal alone.
- **C4:** Independently precommitted model predicts literal exact UCI on a **new** source-disjoint cohort, surpassing M0 in game-clustered scores. Not a P2 development claim.

## Pre-execution controls

1. Retain only May #11 and #2 previously source-locked exact T2 targets. May #1/#12 and #8/#3 remain HOLD. Do not select alternative successful cases based on existing T3/T4 outcomes.
2. Instrument actual native `search.cpp` source branches immediately following each exact guard with **read-only**, opt-in observation; no alteration to Stockfish move legality, TT, SEE value, pruning gate, root order or recursion. Run both no-observer and observer and require entire T3 private result SHA when disabled, plus exact UCI, nodes, score, every root depth and contact count when enabled.
3. Execute 2 games × 4 arms × 2 cold runs; require 8/8 unique exact source C2 contacts. Do not interpret missing events as negative proof of unreachable descendants. C3 results are conditional on contact and **development only**.
4. Freeze required event vocabulary, bounded log count and abort policy before compilation. Include source-order monotonic event ordinal, exact parent→child key (not hash-only parent conjecture), root candidate, ply/depth/window. C3 `NO_CHILD` only after instrumenting all relevant alternate branches; otherwise `UNKNOWN_OR_CENSORED`.
5. Compare #11 with #2 without post-outcome redefinition of the success criterion. Branch-survival effect on a fixed source event and root-UCI effect may decouple.
6. No statements of natural TT→SEE mediation, cognitive mechanism, causal necessity/sufficiency, cross-engine transfer or improvement of model M3. A candidate explanation is conditional on this exact engine build and treatment.

## Independent forecasting after P2

For any P2-inspired M3-v2 model: perform design/debugging ONLY on historical May and P1 August as marked development; prospectively select another previously unexposed official Lichess source, prove rights and historical FEN4 nonoverlap, Git-seal literally one predicted UCI per eligible predeclared role **before source-native treatment**, and compare game-clustered against M0 and the original M3. Do not use the already tested August outcomes for reported model validation.

## Governance

GitHub Actions `permissions: contents: read`; no bot-authored or bot coauthored commits. No republishing entire original PGNs, TWIC private email or modified Stockfish binaries. SHA-gate before public rights-scanned aggregates. Technical scan PASS is not legal clearance. Any unsuccessful source anchor is TECHNICAL_FAIL and should stay recorded, not become scientific NEGATIVE. This document is a design lock, not actual P2 execution.
