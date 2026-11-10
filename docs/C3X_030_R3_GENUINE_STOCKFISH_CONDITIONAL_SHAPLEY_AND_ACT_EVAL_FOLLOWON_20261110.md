# C3X 0.30/R3 — Genuine Original Stockfish Conditional Three-Piece Shapley Pilot

**Date** 2026-11-10 KST. **Verdict:** real native original Stockfish evaluations for a mathematically exact **conditional** three-piece Shapley attribution in two previously exposed source chess worlds. NOT the complete Spinnato (2025) SHAP chess benchmark; NOT original search-mechanism mediation or a prospective demonstration.

## Owned original primary and inherited methods

- [Spinnato (2025), *Towards Piece-by-Piece Explanations for Chess Positions with SHAP*, full original in Drive](https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view). First-hand inspected its mathematical feature definition and \(p(s)=1/(1+e^{-\beta s})\), \(\beta≈3.68×10^{-3}\), King-only neutral baseline and SamplingExplainer up to 10,000 chess perturbations, originally using Stockfish17.1. The original explicitly cautions that removing pieces need not be legal chess play.
- [R2 previous exact finite-coalition mathematical implementation](../harness/c3x_030_r2_exact_piece_shapley_kernel.py), [R2 SUCCESS #42747317750](https://github.com/WhoSia/C3X/actions/runs/42747317750). Exact Shapley requires all subset outcomes and additive reconstruction.
- [0.29/R30-D native source SARFA pilot](C3X_029_P42_R30_DRIVE_00_TO_10_PRIOR_ART_IMPLEMENTATION_SARFA_SANDMANN_MAPPING_20261110.md), [previous SUCCESS #42745545135](https://github.com/WhoSia/C3X/actions/runs/42745545135), previously ran 24 forced-root Stockfish16 searches on the same historic Sahel and Cerrado source positions; this R3 does **not** conflate SARFA's chosen-action estimand with Shapley's whole-board scalar outcome estimand.

## Authentic source data and actual new code

[Implementation](../harness/c3x_030_r3_native_stockfish_conditional_piece_shapley.py) · [9 isolated legal/UCI/mock-engine tests](../harness/test_c3x_030_r3_native_stockfish_conditional_piece_shapley.py) · [read-only original-native Action](../.github/workflows/c3x-030-r3-native-conditional-piece-shapley.yml)

Exactly the same P37 original source archive and pre-referee prediction bytes are SHA validated before original two exposed R23 chess positions reconstructed from full original legal UCI prefixes. The full history is then cleared **in all comparison conditions equally** for an explicit *static chess feature-perturbation* pilot. The source identity, original castling/en-passant metadata and side to move are not fabricated by the caller.

Choose the lexicographically first triple of nonking occupied squares such that **every one of eight 3-piece ablation masks yields `board.is_valid()`, nonterminal and a distinct full FEN**. Ranking makes **no use of engine score or independent judge outcome**. Other pieces are **held fixed** in every coalition. Thus the empty subset is NOT two kings only, but the source position minus exactly these three selected pieces.

For all `2 historic worlds × 8 chess-valid coalition masks = 16` states, run genuinely compiled original unmodified Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, `Use NNUE=false`, 1 thread, 16MB hash, depth10, independent UCI `game=object()` between positions. Report exact actual node counts, source cp from WHITE perspective, king-check legality, raw score-mate type and explicit ±10000cp surrogate if necessary. Map source cp via original paper's \(\beta=0.00368\) logistic to an **uncalibrated white win-proxy** between zero and one, without claiming actual empirical probability.

Use inherited R2 exact Shapley kernel on the 8 actually observed values, exactly check `baseline+sum(phi)=full_value`, and archive every coalition's original score, search depth and nodes (not just summary values).

## Executed evidence, failures and reproducibility

- [First CI #42748289909](https://github.com/WhoSia/C3X/actions/runs/42748289909) FAILED in one mock boundary test due to Python `Mock.side_effect` overriding an intended `return_value`. This was a **test fixture mistake**, not a failed engine search or SHA gate. Preserved failure and repaired fixture without changing original source datasets, original value or any source admission policy.
- [Final successful genuine native run #42748378432](https://github.com/WhoSia/C3X/actions/runs/42748378432), **17 tests including the R2 eight mathematical and R3 nine legal/UCI contracts**, all successful. Original source archive and the full pre-referee predictions SHA gates passed; genuine Stockfish rebuilt and independent 16 depth10 leaf-searches completed.
- Two cases and actual node costs:

| Original case | Three selected piece features | No selected features (white logistic proxy) | All features restored (white logistic proxy) | Native nodes |
| --- | --- | ---: | ---: | ---: |
| Sahel International Chess Festival | `a1:R`, `c1:B`, `f1:R` | 0.0378798511 | 0.5531583435 | **81,581** |
| Cerrado Internacional Garcia-Palacios | `c1:R`, `d1:Q`, `f1:R` | 0.0151155546 | 0.4926405315 | **86,586** |

**Total 16 genuinely executed original Stockfish16 native evaluations and 168,167 nodes.**

- Source JSON SHA256: **`5bab62f215795766530798d82825ad6f452f552355c9d5bda60add860b4a2a66`**.
- CI artifact `c3x030-r3-native-16-coalition-conditional-piece-shapley`, artifact ID **13731613101**, ZIP SHA256 **`7ce842ae52c87d120b0b1238a3903411bff2116dc26a45dfa034d69d7f88fdf7`**.
- No Chat-mode chess package installed; chess 1.11.2 used only in isolated read-only runner. Author commits only by WhoSia.

## Scientific ceiling and next implementation

These scores describe value sensitivity to **artificial non-reachable piece deletions**. The full-piece Spinnato baseline is king-only rather than 3 removed pieces with others held fixed, and original Stockfish17.1 plus up-to-10k SHAP SamplingExplainer and interactive chess explanation/human tests are NOT reproduced.

In 0.30/R4, implement [Hebbar et al., ACT-Eval original owned Drive PDF](https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view)'s **atomic tool-checkable chess fact interface** first: piece position, material, legal move, capture and check. Apply to authentic original P37 prefixes and include deliberately false atomic foils. The original ACT-Eval also involves generative claim parsing, LLM routing, gold strategic references, and human calibration, NOT to be claimed until measured.

C3X's original scientific claim remains **HOLD**: a piece attribution of source board evaluation cannot by itself identify *why original search selected a final root move* or show same-world source-computation/contingent-plan causal mediation. Likewise original prospective eight-game gate remains 7/8 HOLD.

## Drive 미보유 원문

None for R3/R4 primary methodological sources. Both Spinnato and Hebbar et al. original PDFs were checked directly in Drive.
