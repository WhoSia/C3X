# C3X 0.31/P3-X3 — Original Stockfish16 Non-Mutating Pre-Futility TT-State Witness (63 Actual Native Searches)

**2026-11-21, technical PASS**: [CI #44896745183](https://github.com/WhoSia/C3X/actions/runs/44896745183), 11 source-guard regression tests, exact original `sf_16` commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, eight consecutive experimental source patches R27→R29×2→R30→R31×2→R33→**new R39** applied and compiled, **63 new independent-process Stockfish16 searches**, zero new P2 outcome training or selection.

This is **a verified pre-source-event TT-state observation**, *not* TT-state mediation, sufficiency, chess quality or generalization.

## Why the naive TT observer would be an intervention

In [official Stockfish16 original `src/tt.cpp`, lines 120–130](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/tt.cpp#L120-L130), `TT.probe` refreshes a matched entry's `genBound8` age/replacement metadata. Thus a second `TT.probe` for an ostensibly "passive" source trace can *alter the search state being observed*. The [R39 patch](../patches/stockfish16/R39-source-gate-tt-snapshot-readonly.patch) instead reads the `tte`, `ttMove`, `ttValue`, `ttHit`, `ttPv` and parent-stat fields **already produced by the source's original lookup**. The read-only code was mechanically gated against adding `TT.probe(` (diff-side grep) and additionally verified by observer OFF/ON physical source parity.

## Actual 7-case × 3 arm × 3 observational replay

Seven original pre-selected, **post-P2-outcome-exposed** physical source gate cases: the six conditional null-gate final choice flips plus the original futility-only flip `P2-005-0` as a contrast. For each original complete legal game history and signed B1 source event, physically replay `sham` (F0N0), `futility_only` (F1N0), `both_off` (F1N1), each with **R39 snapshot OFF once and snapshot ON twice**, **63 actual new native Stockfish16 `go nodes 32000` calls**. Every source arm and both snapshot-on cold processes matched the *original P2* public UCI, R23 root-producer, source R33 PRE/CLOSE and returned child value, and repeat transcript, across **21/21 physical arm combinations**. All **7/7 sites** had identical pre-gate TT snapshot in the three different arm interventions. New source logs did not call an extra TT probe. Original pre-gate event SHA and original source binary/NNUE were checked.

- R39 patched Stockfish executable SHA256 **`c13646305c707a25e2a4971ff23e967981802baed790d41edb4019b23a780d78`**. R39 patched `src/search.cpp` SHA256 `69f73bc48ee18d4e3b9dece62ca874865ad7703f9749de00d3d4d589fec921c7`. R39 patch exact SHA256 `e69796335e55e271fa19f120d99a581a6401ed8411f3aaedc8e13763a7a89b79`; full eight-patch-order and compiler original build receipts are archived with binary.
- R39 result original JSON SHA256 `bec82bce2dcb5782f0dbe38ee2fed5900060098a233ebb14e053cd838562b06e`.

## Seven original pre-futility TT states (signed source results, not inferred from PV)

The original `TTEntry` classification below follows [pinned original `src/types.h`](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/types.h) (`BOUND_NONE=0, BOUND_UPPER=1, BOUND_LOWER=2, BOUND_EXACT=3, VALUE_NONE=32002`). A "hit" can mean that the slot contains **only a static evaluation** and not a valid search bound, depth or TT move. Values below are native engine-internal units, **not centipawn-normalized chess values**.

| Original frozen source gate | P2 physical effect class | TT hit? | Stored TT move | Stored depth | TT bound | Stored search value | Pre-futility state classification |
| --- | --- | ---: | --- | ---: | --- | ---: | --- |
| `P2-005-0` | futility-only final-root flip | **1** | `c6b6` | **1** | LOWER (2) | 179 | **Only case with usable old TT search bound+move** |
| `P2-013-1` | incremental null source flip | 1 | (none) | −6 | NONE (0) | VALUE_NONE | static eval only (−306) |
| `P2-021-1` | incremental null source flip | 0 | (none) | −99 (miss sentinel) | NONE (0) | VALUE_NONE | TT miss |
| `P2-041-1` | incremental null source flip | 1 | (none) | −6 | NONE (0) | VALUE_NONE | static eval only (+157) |
| `P2-052-1` | incremental null source flip | 0 | (none) | −99 | NONE (0) | VALUE_NONE | TT miss |
| `P2-056-1` | incremental null source flip | 1 | (none) | −6 | NONE (0) | VALUE_NONE | static eval only (+1099) |
| `P2-058-1` | incremental null source flip | 0 | (none) | −99 | NONE (0) | VALUE_NONE | TT miss |

**Totals**: 4 actual raw TT-hit / 3 TT-miss events. Among TT hits, **one stored bound-and-move**, **three eval-only placeholders**. All **six physically verified incremental null-cutoff-dependent final-root flips** were at a child whose *existing pre-futility TT entry had no usable stored search value or move*: three eval-only, three misses. This **falsifies a narrowly defined explanation** that those six changes arose solely by reading a pre-existing useful TT bound at that *same child gate*. It does **not** falsify a broader explanation involving TT hits elsewhere, post-treatment TT writes, history/order updates or changes in nodes/iteration scheduling. In the original R39 observer, the post-gate live TT entry and full-search memory are not yet measured or swapped, and TT matching has known 16-bit key/index collisions.

## Raw original research custody, verified after upload and readback

- [Drive original R39 63 genuine native stdout/stderr logs](https://drive.google.com/file/d/1-lm-RAha6XUruOGh7JBFDnewLx4aDUVM/view), **126 original files**, ZIP SHA256 `9363f98b20bf663bab3d19129e43f7cbe870d848e50d710a792d5e6955e65082`.
- [Drive complete newly built pinned R39 Stockfish16 executable, exact eight-patch order and source SHA receipt](https://drive.google.com/file/d/1yt4M9XcYwadJkyE3sisI0ydej4z8QTPh/view), ZIP SHA256 `05b3e890bbb6f88a2a41156abc1fd12e6f95c8e7ba7815721966ce4be99f399b`.
- [Drive original seven source TT-state witness court](https://drive.google.com/file/d/1mUdForuK-mwMaBHNBUCuGtbMcmGO2508/view), ZIP SHA256 `a1d7b2a5672853ee707e7be3519632df6a0ac5fe66028a1ce0a311121781f08b`, original JSON SHA256 `bec82bce2dcb5782f0dbe38ee2fed5900060098a233ebb14e053cd838562b06e`.
- All three Drive uploads were separately downloaded, original GitHub Actions ZIP artifact SHA256 matched byte-for-byte, and ZIP CRC test passed. The R39 binary itself and complete build recipe are preserved, not replaced with a generic current Stockfish version.

## New mechanistic research decision (P3-X4, not yet run)

1. In each of the seven source events, **the PRE-gate TT fields are equal across all 3 causal arms**; the observed final change must originate *after* a branch is suppressed and additional computation occurs, not from unequal original pre-gate TT state.
2. The physically observed null cutoff is an early return that changes which subtree is searched next. If identifying the *mechanism that carries the effect to the root* is the goal, record actual **post-gate child return, root parent comparison, TT writes by full source key and history updates**, then specifically intervene on a single candidate mediator. Do **not** add extra `TT.probe` in that observation (it mutates age).
3. A **future conditional TT-entry restore/swap** needs narrow source-scoped state capture at one actual search boundary, independent sham and reverse restore, cold-process repeat, hash-collision audit and explicit node budget. Until then **TT/history/search-budget mediation remains HOLD**. Similarly independent legal-opponent chess plan evaluation and human learner benefit are not measured by this TT snapshot.

**Verdict:** `PASS_PRE_GATE_PASSIVE_TT_WITNESS_NO_MEDIATION`; a genuine new observation excludes a common but wrong pre-existing child TT-bound story for the six null-dependent root flips, while highlighting a concrete next state-transmission experiment.
