# C3X 0.29–P42/R18 — Reverse the Matched Native B Event33 Draw Value Inside C's Capture-Guard World

Date: 2026-11-09 KST. **Source-exact reverse intervention hypotheses frozen before native outcome.** This is a mechanistic sublemma for the flagship causal–strategic explanation problem, not a paper on easy metrics.

## Precise observed premises

Game14 is a historic, postselected, **NNUE-OFF** Stockfish16 program. Original TT_FIRST B chooses f3f4; original precise capture-prune bypass C chooses b3a4; original B cycle event33 return-neutralization B33 also restores b3a4. Physical source events and original 16-game StageA bytes are pinned.

- R15 combined C plus ordinal33 neutralization still chose b3a4 twice, but the ordinal33 source state was NOT identical to original B event33.
- R16 genuine pinned native source-state support audit found one occurrence in C and C+B33 of the original B event33's **same board hash, ply, search depth, root context and alpha/beta window**, but **different node mod4**. B has 281 source cycle calls per physical engine, C and C+B33 403. All 403 measured C/C+B33 pre-score callback contexts and all 12 published root boundary summaries matched exactly.
- R17 genuine native source court (actual [#42551851784](https://github.com/WhoSia/C3X/actions/runs/42551851784)) proved that **C's ordinal33** actually returned +1 under original node-parity draw score and 0 under combined C+33, but the local immediate `alpha>=beta` cutoff was TRUE in both and all subsequent 370 measured cycle source contexts and final root boundaries stayed the same. Therefore simply neutralizing C's ordinal33 does not reverse original C root choice.

**New important inferential distinction:** original B event33 and C's ordinal33 are **not the same original source state**. The physically matched B event33 state may appear at a different *ordinal* in C. The prospective R18 target is exactly that matched source state, not an ordinal chosen posthoc based on whether the move flips.

## Exact reverse B-original-source intervention

The B original event33 is frozen from prior R11/R12 source trace before any R18 outcome by:
`(native position key, source ply, depth, root move, old alpha, beta)`. The entire raw target remains private in the Actions runner. C is run with the original exact C capture-prune bypass activated as in R14, plus a new source instrumentation:

- In the exact original Stockfish16 cycle-alpha expression where R12 would ordinarily emit the `value_draw()` return, match **the frozen B source identity**, **deliberately ignoring node mod4**, because changing its node-dependent returned value is the mechanistic hypothesis.
- At the **first** actual source match in each engine subprocess, force `Value(-1)`, the original B event33 draw return, rather than C's original `Value(+1)`. Instrument how many native matches are encountered; fail closed if != exactly one true intervention per physical play.
- All other dynamic source calls unchanged in source. Keep original capture guard C physically reenabled, TT_FIRST reader valid, original game legal and all original StageA SHA checks.
- Repeat in two independent cold invocations, each of which internally launches two identical physical Stockfish processes.
- Check the original C target's preintervention state prefix exactly, and the actual changed source return `+1→−1` at the physically matching source event. The initial local cutoff is **predicted** to change from TRUE to FALSE if the frozen beta=0 source window holds (all source values verified). However native logs, not theory, determine the verdict.

### Predeclared possible root outcomes

1. C+reverse root returns **f3f4** (original B): stronger evidence that the matched original draw window/value is functionally necessary for the original C b3a4 restoration **under the specific reverse intervention**, but not proof that the guard naturally transmits only via that path, since the intervention may alter dynamic support.
2. C+reverse root remains **b3a4**: that single matched source-value difference is not sufficient under this intervention to abolish C root restoration; alternate paths/compensation remain.
3. C+reverse chooses a third move: dynamic candidate-set emergence; preserve the full outcome.
4. Wrong or multiple physical source hits, mutated original C guard, TT reader/source SHA/legality failure, or cold instability: **HOLD**; never infer scientific null from instrumentation failure.

Either way, independent chess-strategic true future and NNUE-on prospective transport remain *entirely unproven*. These source scores can be causal *software machinery* without constituting human-relevant chess reasons.

## Exact executable proof and privacy

- [R18 C++ reverse source patch](../tools/c3x_029_p42_r18_source_identity_reverse_B33_in_C_overlay.py)
- [R18 original derived native compiler](../tools/c3x_029_p42_r18_original_reverse_identity_build.py)
- [Native C reverse root court](../harness/c3x_029_p42_r18_source_identity_reverse_B33_in_C_court.py)
- [9 source and 12 native verdict synthetic tests](../tools/test_c3x_029_p42_r18_source_identity_reverse_B33_in_C_overlay.py) and [native court tests](../harness/test_c3x_029_p42_r18_source_identity_reverse_B33_in_C_court.py).
- [Read-only pinned source native R18 workflow](../.github/workflows/c3x-029-p42-r18-native-reverse-B33-in-C.yml) starts [run #42552769246](https://github.com/WhoSia/C3X/actions/runs/42552769246). No conclusion asserted before logs/artifact exist.

Original private source hashes, TT keys, target score-window values, PGN and full raw traces are never written to public artifacts. Actions has contents:read; only WhoSia authored commits. Notion is semantic research log and Drive raw-byte archive; new originals still require Drive preservation verification.
