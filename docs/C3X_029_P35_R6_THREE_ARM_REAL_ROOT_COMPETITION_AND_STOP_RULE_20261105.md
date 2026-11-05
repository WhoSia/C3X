# C3X 0.29-P35/R6 — Actual Root Competition Restored: Forced, Paired and Unrestricted SF16

Date: 2026-11-05 KST. **STATUS: IMPLEMENTED / SOURCE REVIEWED / NATIVE CI RESULT NOT YET VERIFIED.** No new native search PASS or chess-explanation superiority should be asserted from this record.

## One scientific correction, one bounded experiment

Prior P35/R5 code `go searchmoves {one_root} nodes 24000` forces the only legal output candidate, so matching `bestmove` across unmodified and instrumented engines never tested competitive root choice. This violates the original C3X goal and repeats the risk discovered in 0.29-P9: search can select a *third candidate* outside an A/B model.

Repaired [actual source harness](https://github.com/WhoSia/C3X/blob/main/harness/c3x_029_p35_r5_search_route_court.py) to include three distinct experimental arms on the **same full original mainline history**:

1. `forced_one`: four original root choices (case10 e8f7/e5f4, case14 c2c3/d5d3). May certify native actual dispatch and instrumentation parity in the forced subtree. **Cannot** certify natural choice.
2. `pair`: exactly two originally paired legal candidate root moves per original case, using `go searchmoves a b nodes 24000`. Tests competition *conditional on pair restriction*, not true unrestricted engine choice.
3. `unrestricted`: `go nodes 24000` without `searchmoves`, one run per original source game. Tests source-native natural selection and whether a third candidate wins at these conditions.

Total: **8 distinct conditions × 2 engine builds = 16 new Stockfish processes** at 24,000 requested nodes per search. Same source history, Threads=1, Hash=16, Use NNUE=true, same node resource limit. A 2-game *source-exposed* development cohort, not 8 independent cases.

## Experimental observables and automatic failure

- Real search-executed `Eval::evaluate` dispatch log: HCE/NNUE, PSQ, position key, returned score; read-only stderr, never a repository writeback.
- Paired source-identical vanilla vs patched output parity: final bestmove, score type/score, full PV and actual nodes. Any mismatch => `HOLD_SOURCE_INSTRUMENTATION_PARITY`. Note this is a *strict engineering admissibility test*; if it fails, diagnose overhead or nondeterminism, never selectively discard discordant trials.
- In pair arm, bestmove must belong to the two legal roots; unrestricted bestmove must be legal on original board.
- `third_candidate` records the unrestricted winner outside the preselected two-root set. A forced root agreement is explicitly flagged `natural_choice_evidence=false`.
- Full root competitor win ≠ proof NNUE internal representation causally altered root: dispatch is observational, and changing source code or evaluator changes search trajectories. Actual mediation remains HOLD.

## Test and verification boundaries

- [UCI three-arm protocol mock tests](https://github.com/WhoSia/C3X/blob/main/tools/test_c3x_029_p35_r6_three_arm_uci_contract.py) added: one forced, paired two-root, unrestricted third root and duplicate-root rejection. Mock integration tests check orchestration, **not real Stockfish**. At creation, these new mock tests and native workflow have NOT been independently observed to finish in CI; do not report PASS prematurely.
- [Read-only SF16 CI workflow updated](https://github.com/WhoSia/C3X/blob/main/.github/workflows/c3x-029-p35-r5-eval-dispatch.yml) with new mock test invocation, original full-game data SHA checks, official SF16 exact source clone, original and instrumented source build, 16 native searches, JSON+hash artifacts and contents:read permissions. GitHub Actions may upload artifacts but **never commit/push/merge/tag/move refs**. This workflow updates same R5 artifact path to avoid proliferating method variants; name indicates R6.
- The authenticated connected GitHub interface has not returned the latest native workflow completion; use **HOLD_NATIVE_EXECUTION**, not PASS.

## Confronting original competing explanations

This correction does NOT yet show a useful chess explanation. The next admissible strategic experiment is one precommitted legal-history, near-equal foil; action-conditioned opponent response consequences scored at matched compute against **Stockfish+PV, simple foil-aware plan JSON, and C3X conditional plan**. Report equal forecast set size, legality/factual error, selective coverage/abstention, game-disjoint confidence and cost. The previous P34 A/PV was strongest under NNUE→NNUE reference on four exposed roots; no branching format uniformly dominated. Must not conceal it.

## New claims NOT made

No source-proven intervention from NNUE accumulator to decision; no named chess concept discovery; no independent heldout; no human teachability; no cold R4 PASS inferred. Historical local motif and classifier failures preserved. R6 is a narrow repair of R5's false competition premise, not a new generation.

## Next decision / stop rule

**RUN-ONE-FATAL-TEST:** inspect actual R6 run artifact and job trace. If source patch does not compile or output parity fails, correct *that* single defect before any source-neuron expansion. If native dispatch and unrestricted search pass, compute exact per-case HCE/NNUE event counts and root winning move, then return to a **real chess-valued explanatory comparison**. No further instrumentation mini-versions unless these results show unique scientific necessity.
