# C3X 0.29-P34/R4 — Direct Original-Source NNUE World-Model Probe, Search-Isolated Chess Evaluations

Date 2026-11-04 KST. **First executed, source-native, search-free STATIC NNUE / classical / hybrid evaluation comparison on the same full-history chess boards** in C3X 0.29. This is not an identified learned strategic concept, causal engine-choice mediator, or a new heldout study. It extends P34/R2 equal-requested-budget natural search results.

## 1. Immutable original source and actual execution

- Original 0.18 Lichess October 2025 full UCI game history source, 16 source games, JSON SHA256 `6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c`; four adaptive P34 roots drawn from exposed development cases #10 and #14.
- P34/R2 original NNUE/classical symmetric, full legal first-response deep-reference JSON SHA256 `c80704f2f81c4920597fbf6b559ef38dbae60f35458c7a2f665f1cf57d2563dc`, verified before this R4.
- Unmodified official Stockfish 16 source git commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`; native UCI `position startpos moves [complete source history] ... eval`, with `Use NNUE true`, preserving original game history. NO search command `go` issued in R4.
- Four original roots, each immediately after root and after two evaluator-referenced worst legal opponent replies = **12 direct static evaluation trace outputs**. All 12 returned valid classical, raw NNUE, and final values; none were in-check unavailable.
- Actual independently checked GitHub Actions run **[41778762120](https://github.com/WhoSia/C3X/actions/runs/41778762120)** completed SUCCESS, `Direct static source` and NNUE piece deletion trace checks completed.
- Original raw source trace files, including *full original NNUE::trace per-piece deletion chessboards, PSQT/Layer bucket contributions, and classical/NNUE/final scores*, archived under C3X/04_SEALED_RESULTS_COURTS in Google Drive: **[P34 R4 native raw trace ZIP](https://drive.google.com/file/d/1l6RVNZ79XyB_VORm79q-AUIQEwMtqa0_/view)**. ZIP SHA256 `2b426b81c97d1483581e398c7a300b221a39ebe6d9e5e0194bec4d3f2885547e`; direct raw JSON member SHA256 `07d78a9261dd87d12b900bc3cec715d4d28aa739212ef3c81507b918a6ba14f9`; 12 full raw trace strings, no downsampled excerpts; official original NNUE `NNUE derived piece values` and `NNUE network contributions` regions present in every trace.
- Reproducible source program `harness/c3x_029_p34_r3_direct_nnue_classical_eval_trace.py`, tests `tools/test_c3x_029_p34_r3_direct_eval_trace.py`, CI `.github/workflows/c3x-029-p34-r4-nnue-source-trace.yml`.

## 2. Direct NNUE-vs-classical STATIC ranking reversal at the SAME chess root and legal opponent branches

Original game case #10: Black played candidate `...Kf7` (UCI `e8f7`). After it, two actually legal White replies were `Re1` (`f1e1`) and `e4` (`e3e4`). Both full-history boards were generated with the ORIGINAL root and a DIFFERENT legal White reply; each resulting board is evaluated by the **same unmodified executable without running search**.

Direct `eval` static values in **pawns, WHITE point of view**:

| Original history+root+response | Classical static | Raw NNUE static | Hybrid final static |
|---|---:|---:|---:|
| `...Kf7, Re1` (`f1e1`) | -0.20 | -0.44 | -0.42 |
| `...Kf7, e4` (`e3e4`) | -0.29 | -0.32 | -0.31 |

Under **classical static** evaluation, White prefers `Re1` over `e4` by +0.09 pawn. Under **raw NNUE** evaluation, White instead prefers `e4` over `Re1` by +0.12 pawn. This is an **actual static evaluator-order reversal** at two legal post-root response boards: the evaluator itself differs, without search confounding *this direct comparison*. The same-board per-reply NNUE-minus-classical raw differences are -0.24 pawn after `Re1` and -0.03 after `e4`; it is the relative ranking that reverses.

In separate P34-R2 **40,000-node search per every legal opponent reply**, the Classical referee worst (for Black's root) was `Re1` and NNUE referee worst `e4`. This is *concordance*, not an established path-specific causal link from raw evaluator to final search choice. Both ref conditions used same search code with different evaluator and its downstream induced pruning/order/TT state.

## 3. Search cannot be reduced to static NNUE evaluation

Original case #10 root `...Bxf4` (`e5f4`), White can immediately take the bishop either `e3f4` or `f3f4`:
- Raw classical static WHITE after `e3f4`: **+0.29 pawn**, after `f3f4`: **+0.20 pawn**.
- Raw NNUE static WHITE after `e3f4`: **-0.04 pawn**, after `f3f4`: **-0.14 pawn**.

Thus **BOTH static evaluators prefer `e3f4`**, yet the search-based NNUE referee at 40k nodes selected `f3f4` as its worst first White reply for Black (0cp vs -8cp for classical's `e3f4`). The NNUE search-order difference in this world therefore cannot be explained merely by this one-step raw static ranking; deeper followups and search-pruning transitions remain necessary.

Other direct worlds:
- Case14 root `c2c3`, after `e7h4`: classical -0.24, NNUE +0.59 (white pawns); after `d8d7`: classical -0.54, NNUE +0.52. Their sign and magnitude differ substantially. But static vs searched response ranks are not one-to-one; this is no direct proof of specific NNUE idea of the position.
- Root `e5f4` immediately after capturing the knight: classical static -2.24 white pawns, raw NNUE -0.71, hybrid -0.59. The NNUE-vs-classical absolute score disparity is striking but cannot be interpreted as a unique semantic "recapture foresight" signal without source-level activation and counterfactual tests.

## 4. Official source: why pure NNUE, network trace and final engine score differ

This is source **reverse engineering** from the exact pinned official SF16:
- [`src/evaluate.cpp`](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/evaluate.cpp) uses `bool useClassical = !useNNUE || abs(psq) > 2048`. If NNUE option is active but PSQ advantage exceeds threshold, the **real evaluate() dispatch can still route to classical**. C3X original 0.14 native receipt counted 19,842/606,141 NNUE-enabled evaluation calls using that classical route (3.273%), on different historical worlds.
- In NNUE route, `NNUE::evaluate(pos, true, &nnueComplexity)` enters a formula blending NNUE, non-pawn material and search-thread `optimism`; rule50 damping and clamps then apply. This makes `eval`'s raw NNUE, hybrid final and iterative search score **different statistical/causal objects**.
- [`src/nnue/evaluate_nnue.cpp`](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/nnue/evaluate_nnue.cpp) implements `NNUE::trace(pos)`, which produces `NNUE derived piece values` by **temporarily removing a non-king piece from the position and recomputing NNUE**. This is a native diagnostic deletion and can produce chess-illegal hypothetical boards; it is NOT a legal action counterfactual. It also exposes network-contribution tables by `PSQT` and `Layers` and selected network bucket. These tables do NOT directly provide human chess concepts or individual hidden-neuron intervention evidence. Raw complete text is preserved from our native run.
- This confirms a **three-level empirical separation**: (I) original board static evaluators' preference, (II) their induced selective Stockfish search/candidate outcome, (III) actual source-site/NNUE activation causal evidence. P34/R4 establishes examples of (I), P34/R2 covers (II) descriptively, and (III) remains explicitly unproved.

## 5. Research path toward NNUE 'how it sees the board': concrete reverse-engineering tasks

1. Use exactly the saved P34 12 full source-history legal worlds. For each, verify the raw NNUE-derived piece-removal diagnostic against true legal action-based counterfactuals, and **record which pieces' diagnostic removal rankings diverge from legal move consequences**. This provides a negative control against misinterpreting NNUE heatmaps as chess plan values.
2. Replicate the direct `eval` and raw layer bucket values with cold processes and fixed net SHA. Compare candidate response pair `f1e1` versus `e3e4` for case10 using independent original source observations; raw NNUE differences must survive cold replay. The current R4 already uses one cold process per board but does not provide a second paired repeat.
3. Add *read-only instrumentation* to the pinned official NNUE `featureTransformer` accumulator input channels, network bucket, output-layer preactivations and actual eval routing, anchored by exact source hash. Separate positional feature effects from search-induced feature selection and PSQ fallback.
4. Only after identifying stable source-native activation patterns: intervene selectively on a well-defined feature channel/activation while holding legal world and relevant source model parameters fixed; test difference in raw NNUE score and separately in subsequent search score/TT/root choice. Both causal intervention scope and off-manifold risks must be reported.
5. Run cases from independent original full-history games as a new source-hash-sealed cohort. Compare a simple score+PV / native `eval` baseline against C3X plan-conditioned policy explanation **with measured human transfer or independent chess outcome** and equal budget. Failure must be admitted, not repackaged as an interpretability victory.

**Current evidence supports studying NNUE's chess-world valuation behavior, not claiming that a learned latent representation named 'tempo', 'plan', 'king safety' or 'future potential' has been identified.** Source code is GPL governed; engine is unmodified for every native P34 run, and no source authorship occurred through GitHub Actions bot.
