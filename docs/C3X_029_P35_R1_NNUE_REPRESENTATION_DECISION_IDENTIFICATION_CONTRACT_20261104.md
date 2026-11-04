# C3X 0.29-P35/R1 — NNUE Representation-to-Decision Identification Contract

Date: 2026-11-04 KST. Status: **DESIGN / PRE-REGISTERED TEST CONTRACT, NO NEW EMPIRICAL PASS**.

## Inherited exact evidence (do not relabel)

- Scientific predecessor: [P34/R4 source-direct SF16 evaluation](C3X_029_P34_R4_DIRECT_NNUE_STATIC_REVERSE_ENGINEERING_AND_SEARCH_BRIDGE_20261104.md).
- Original source: SF16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`; original source-game JSON SHA256 `6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c`.
- Original P34 static trace archive SHA256 `2b426b81c97d1483581e398c7a300b221a39ebe6d9e5e0194bec4d3f2885547e` ([Drive raw archive](https://drive.google.com/file/d/1l6RVNZ79XyB_VORm79q-AUIQEwMtqa0_/view)).
- Historical development case10 after black `...Kf7`: legal white `Re1` vs `e4`; classical (-0.20,-0.29) and raw NNUE (-0.44,-0.32) white pawns. Reversal is measured **between two legal child boards**, not a claim of a neuron or an identified natural mediator.
- Search reference: different worst reply under NNUE and classical at equal requested 40k nodes; causal propagation and human explanatory benefit are **NOT IDENTIFIED**.

## Exact target estimands

Let `h` be the complete original legal move history and `x(h)` the reached board with context. Let `a,b` be legal opponent replies after a fixed root move, and `E_N(x)`, `E_C(x)` be source-direct *white-view* raw NNUE and classical evaluations with no `go`.

- **Static difference-in-differences** `D(h;a,b) = [E_N(x(ha))-E_N(x(hb))] - [E_C(x(ha))-E_C(x(hb))]`. Units: pawn; same perspective required.
- For case10 `a=Re1,b=e4`, `E_N(a)-E_N(b)=-0.12`, `E_C(a)-E_C(b)=+0.09`, hence `D=-0.21 pawn`. This arithmetic is derived from already measured, rounded P34 numbers, NOT a new native execution.
- **Cold-replay reliability** `R`: proportion of exactly reproduced board-specific raw trace fields across two *independent process invocations* pinned by source SHA, NNUE weight SHA, UCI options, FEN, complete move history, hash/threads; zero-missing required before activation claim.
- **Legal counterfactual contrast** `L`: compare board changes induced by genuine legal UCI moves from the same preceding game history. Do not equate native NNUE piece-deletion diagnostic with a legal chess action.
- **Search transmission** `T`: change in root move/value under a precisely stated source-level intervention, conditional on matching legal history, equal resource budget, source/net identity, instrumented leaf evaluation events and search-node ancestry. Paired *final search output agreement alone does not identify T*.

## Distinct interventions / failure modes

1. **Observational direct eval**: rerun twelve historical P34 legal boards twice in new cold processes. Hold source, compiled binary, architecture, network, options and complete histories fixed. Require bit-level/raw score reproducibility and inspect residual non-determinism. If missing: `HOLD_REPLAY`.
2. **Source observability only**: instrument `nnue/feature_transformer.h` accumulator inputs and activation output with explicit indexing, side-to-move and king bucket, PSQT/network bucket, and file/source SHA before/after. Prove bestmove/nodes parity with source original where instrumentation is read-only. If evaluation perturbation: `HOLD_INSTRUMENTATION`.
3. **Concept-level legal perturbations**: define prospective legal move-pairs to vary a named tactical/positional property while preserving as much background as possible. Record all changed input features and confounders; a legal move usually changes multiple features. Do not call the contrast a single-feature manipulation without checking.
4. **Internal representation intervention** (later stage only): if a channel is targeted, specify numeric accumulator/feature identity, exact change, interaction with quantization/clamps and off-manifold risk. Use sham, random matched-channel and compensating controls. Effects on raw NNUE evaluation are **not by themselves** effects on root choice.
5. **Search mediation** (later stage only): hold common random/engine configuration; measure actual source-specific activation→evaluation→alpha/beta/TT/SEE→parent→root event paths; fixed-budget paired evaluator arms alone measure a total regime difference, not natural direct/indirect effects.

## Negative and positive controls

- Native NNUE virtual piece-removal map: **diagnostic, potentially illegal board**; mandatory negative control against identifying "material value" from its number.
- After `...Bxf4`: both direct evaluators rank `e3f4` over `f3f4` while NNUE 40k search ranks the latter worst for black. Mandatory negative control against leaf-score-to-search collapse.
- Dummy constant channel perturbation and randomized index-label permutation must not support stable chess-specific semantic interpretation.
- Training/exposed cases 10/14 may be used for development but never counted as independent out-of-sample evidence.

## Interpretation gates (strict)

| Claim | Minimum evidence |
|---|---|
| Static rank reversal | Exact legal histories + independent native raw evaluator outputs + fixed white perspective |
| Stable NNUE activation signature | Source-net SHA, cold replay, indexed activations, provenance and path parity |
| Named chess concept encoded | Prospective legal contrast family, multiple independent boards, strong confounder controls, out-of-family test |
| Causal NNUE-to-root transmission | Explicit intervention, verified native ancestry, negative controls, matched resources |
| C3X explanation superiority | Independent game-disjoint cohort, strong engine+PV and concept baselines, equal cost, pre-fixed evaluation and nontrivial coverage |

No row inherits authority from the previous row without a new admissible receipt. Maintain earlier P34 negative results and historic P27/P28 HOLD.

## Next execution

First produce a **cold replay and provenance gate** on 12 P34 histories, including exact mapping and SHA checks. Then source-read and design narrowly scoped accumulator read-only logs; do not intervene in neural weights until instrumentation parity passes. Separate mainline scientific results from engineering checks.

## Repository and data governance

GitHub commits: authenticated **human/user actor** only. GitHub Actions: compute and upload non-repository artifacts, no source writeback, commit, push, merge, tag or ref movement; `github-actions[bot]` **forbidden**. Drive raw bytes; Notion scientific meaning. A commit is not a scientific pass.
