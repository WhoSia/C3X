# C3X 0.29-P9-R14–R15 — Evidence Joins and Root Bound Partial Order

Date: 2026-10-31. Archival public receipt verification and executable-contract authoring, NOT a new native Stockfish run.

## R11-R13 read-only CI
A read-only public-source GitHub Actions regression workflow was created at .github/workflows/c3x-029-p9-public-receipt-regression.yml; triggering push workflow uses permissions contents:read. It runs Python syntax, archived T3 receipt synthetic/original tests and R12/R13 contract tests, and checks numeric categorical outputs. No unverified CI success is claimed. Workflow later extended to R14 and R15 tests. No original PGN or modified engine binary shipped.

## R14 historical evidence type safety
tools/c3x_029_p9_r14_cross_receipt_type_audit.py and its regression test validate distinct original historical receipts: 0.23-T3, 0.24-C3b R2 and 0.24-R3. Two FULL root candidate paths reached but LOST final bestmove; two paths PARTIAL, four guard CONTINUE. May game2 JOINT TT1/SEEflip selects b1b4 but the watched exact guard in that arm CONTINUED; it is not the same as the FULL traced sham branch. This audit checks consistency of counts; it never joins execution events from different runs. Schema/identity/count change fails closed.

## R15 mathematically sound bound comparison
tools/c3x_029_p9_r15_root_bound_comparison.py defines candidate score intervals: exact cp => [v,v], lower cp => [v,+infty), upper cp => (-infty,v]. For comparable process/root/attempt, strict A winner is certified only if lower(A)>upper(B), and strict B winner if lower(B)>upper(A). Equal exact scores identify equality; all overlapping/one-sided intervals yield ABSTAIN. This elementary inequality is not a novel chess result. It is a safety gate preventing unwarranted candidate-score conclusions.

Code review REQUIRED more metadata: source-engine SHA, process, treatment arm, root call, depth, aspiration attempt and score POV; both entries must denote completed searches of distinct candidates. Missing or mismatched coordinates => ABSTAIN. Original initial R15 draft omitted treatment-arm and completion checks; fixed in later separate commits and extended tests. We do not have actual May b1b4 vs e1g1 candidate-level scores, so R15 cannot explain that historical winner yet.

## New caveat discovered
Reported root cp across different TT/SEE runs cannot be passed to R15 as if they were candidate scores for a single attempt. The R15 input has a meaning only if the collector verifies source-native score/bound annotation and comparable root perspective, including aspiration retry state. It is not a substitute for instrumenting Stockfish.

## Evidence provenance
- c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json
- c3x/receipts/c3x-024-P2-R2-native-ancestor-root-full-and-partial-development-20261011.json
- c3x/receipts/c3x-024-P2-R3-source-root-candidate-reached-but-not-final-and-May11-partial-20261011.json
- docs/C3X_029_P9_R12_R13_NUMERIC_INTERACTION_AND_REPLAY_GATE_20261031.md

## Current verdict
PASS separate code and small GitHub commits; static review of original receipts; local arithmetic smoke test (two exact published 2x2 cases).
PENDING remote Python suite CI execution status (no authoritatively retrieved successful run), original Stockfish replay, original candidate score logging and natural mediation.
No missing academic paper found in the already verified Drive relevant collection.
