# C3X 0.30 — S4-H1/R1 Archived Byte Identity and S4-H2 Pre-outcome Protocol

Date: 2026-11-13 KST. Conversation: C3X 33. Research version retained: C3X 0.30.

## Verified experimental custody

- Original S4-H0 run: https://github.com/WhoSia/C3X/actions/runs/43140220882 ; outcome-blind original manifest SHA256 `1741592a52675c5170fdb076bb96b6842cbdced43e40c8a85c82f80c4ba0d247` (2026-11-12 UTC).
- S4-H1 run: https://github.com/WhoSia/C3X/actions/runs/43145442927 ; eight regression checks PASS, legal FEN replays and prefix split PASS, regenerated SHA same.
- S4-H1/R1 original-archive byte comparison run: https://github.com/WhoSia/C3X/actions/runs/43347450938 ; PASS. The original separate S4-H0 artifact was downloaded in read-only CI and compared byte-for-byte with re-generation, requiring **both** files to match a hard-coded earlier SHA. This is materially stronger than self-computing the current checksum, but GitHub provider timestamps are not an independent trusted timestamp service.
- S4-H2 pre-outcome design run: https://github.com/WhoSia/C3X/actions/runs/43347740057 ; PASS. CI sealed the fixed design using the earlier archived original, with no engine outcomes.

## Frozen S4-H2 design

Cohort: 12 researcher-authored legal histories, of which eight games (16 dependent FEN snapshots) are untouched holdout and four games (eight snapshots) form development. These are not randomly sampled human games, and the 0.29 original prospective 7/8 HOLD is not replaced.

Arms: `original, sham, zero, one, two, many` (same patched binary for all but original); two consecutive UCI searches per position/arm. Fixed native baseline: exact Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Threads=1, Hash=16 MiB, Use NNUE=false, Skill Level=20, UCI_LimitStrength=false, go nodes 12000, new game before each arm.

The plan covers **288 planned searches**, 192 of which would be on the eight-game holdout. These are NOT executed search counts. The first eligible ply-one *real hit* TT key is selected strictly by source-probe events before treatment, without consulting root bestmove, scores, PV, any labels or outcomes. Positions with no eligible key remain in the denominator; no replacement or post-treatment cherry picking.

Primary output must report paired root move changes versus sham per game and arm, including eligibility and no-effect negatives. Source mask receipts must have actual `hit_before=1` and `hit_after=0`. Native arithmetic `root_score=-child_return` is not sufficient for full counterfactual mediational causality; invocation-ID and physical-source linkage require exact verification. Logs may truncate, so missing logs cannot be treated as negative events. Paired game cluster uncertainty is exploratory with only eight lineages.

## Next development gate, not yet executed

Implement a standalone TT first-hit eligible-key discovery that cannot read scores/PV or root selection, a manifest-driven source-native runner reusing S4-G instrumentation without breaking provenance, and physical event-specific chain comparison. First run development cases and freeze the unmodified protocol before any holdout run. An independent label audit is required before F3 risk-coverage or method-superiority claims.

## Scientific verdict

PASS: Original archive byte identity; legal history split; preregistered future experiment schedule.

HOLD: New native holdout trials; actual TT-key eligibility; ancestor/root counterfactual mediation; independent empirical SARFA-vs-fusion benchmark; claims of paper superiority; original C3X 0.29 prospective 7/8.

All authored commits are connector-driven under WhoSia; GitHub Actions never writes a commit.
