# C3X 0.31/P3-X2 — Original Physically Contacted Depth/Node Horizon Transport: 60 Native Stockfish16 Searches

**Actual new native source experiment** [CI #44895972292, SUCCESS](https://github.com/WhoSia/C3X/actions/runs/44895972292). Original source-frozen subset **exactly three P2 root flips chosen AFTER those outcomes were known**; no fresh independent-game generalization claim. Three P2 source event IDs fixed before this run: `P2-005-0` (futility-dependent), `P2-052-1` and `P2-056-1` (null-cutoff-dependent). Each source original game remained its full legal TWIC1669 move history. P2 B1 physical source `OPEN` signatures and source neural network/binary SHA verification unchanged.

**Protocol:** for each case original reported completed depth D and D+1 (D=12,11,13 respectively), node caps 32,000 or 64,000, sham twice/F-only once/Both-off twice; **12 horizon cells × 5 new independent processes = 60 real SF16 searches**. Both node and depth limits were imposed on each UCI `go` simultaneously; actual node counts differ across arms. **All 12/12 frozen source events were genuinely contacted**, every expected `OPEN/CLOSE` signature was verified, and all cold shams and both-off replays matched their original control/proof within each horizon.

## Actual root choice for every fixed horizon cell

Notation: `S` = sham/untouched, `F` = only futility disabled, `FN` = both futility and null disabled; requested node limit first, requested maximum depth second. All values below are actual original SF16 UCI moves, not human or independent chess-evaluation rankings.

| Exact source event | Node cap | Depth cap | Original S move | F move | FN move | Changed FN vs S? | FN extra vs F? |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| P2-005-0 | 32,000 | 12 | `g8f8` | `g7g6` | `g7g6` | **yes** | no |
| P2-005-0 | 32,000 | 13 | `g8f8` | `g7g6` | `g7g6` | **yes** | no |
| P2-005-0 | 64,000 | 12 | `g8f8` | `g7g6` | `g7g6` | **yes** | no |
| P2-005-0 | 64,000 | 13 | `g8f8` | `g7g6` | `g7g6` | **yes** | no |
| P2-052-1 | 32,000 | 11 | `a7c7` | `a7c7` | `e5d6` | **yes** | yes |
| P2-052-1 | 32,000 | 12 | `a7c7` | `a7c7` | `e5d6` | **yes** | yes |
| P2-052-1 | 64,000 | 11 | `a7c7` | `a7c7` | `e5d6` | **yes** | yes |
| **P2-052-1** | **64,000** | **12** | **`a7c7`** | **`a7c7`** | **`a7c7`** | **NO** | NO |
| P2-056-1 | 32,000 | 13 | `b8d8` | `b8d8` | `f5h3` | **yes** | yes |
| P2-056-1 | 32,000 | 14 | `b8d8` | `b8d8` | `h5e2` | **yes** | yes |
| P2-056-1 | 64,000 | 13 | `b8d8` | `b8d8` | `f5h3` | **yes** | yes |
| P2-056-1 | 64,000 | 14 | `b8d8` | `b8d8` | `h5e2` | **yes** | yes |

**11 of 12** physical horizon cells retained a changed final recommendation when both pruning gates were disabled. **7 of 12** had an additional root switch from F-only to F+N suppression. However, one of the already-selected cases, **P2-052-1**, lost its root switch at node budget 64k and depth cap 12: the changed source early return no longer altered the final winner at that different horizon. **This is a real non-monotonic finite computation boundary**, not proof that the source gate stopped affecting any internal search states.

In **P2-056-1**, the intervention's winning move is actually **horizon-dependent**: `f5h3` at depth cap 13, `h5e2` at depth cap 14, whereas sham `b8d8` is retained. Treating these all as one stable strategic alternative would lose precisely the path/plan information that C3X is trying to understand. The third observed legal move under the restricted horizon will require its own independent chess reply referee before any better-chess claim.

At P2-052-1, actual final reported nodes for sham/F/FN at 32k/D11 were **21,793 / 21,793 / 16,555**, and at 64k/D12 were **39,204 / 39,204 / 34,199**. This is **not equal-node work**, even when UCI depth cap matches. At P2-056-1, sham/F/FN at 64k/D14 used **39,878 / 39,878 / 48,269** nodes and still switched; external budget allowance is identical but actual search work is not. These differences may themselves be important downstream causal mediators; no individual TT/history/budget state has been restored here.

## Exact custody and claim limits

- [Drive original 60 new SF16 stdout/stderr search records](https://drive.google.com/file/d/1gxCHgBw4p1bIV8IMKQDuAVBSmnvv1Qlb/view) 120 original raw members, ZIP SHA256 `1678eaa0c6b093142cf053c0b857b2b0db1da8c94fa28a39e9c8a47c6c42bccf`.
- [Drive original full 12-cell physical horizon court](https://drive.google.com/file/d/1gmWlaw6xG-SzrBp0LSY33YqX0owSXLbZ/view), ZIP SHA256 `b17d1ceb5cd54b4e6d9c7afe29bc1f9eda2ed8b5a6d2cb629fc1a8b88557df9c`; court original JSON SHA256 `3c90be5bd0803937a6c9aaf8e55e6b15443c0a5c4f9a71605e13af28cc4da085`.
- Original P2 source/forecasts SHA `d364e6ca24599110fa19ac41e19164069a164c15aa396aac6b2833482e3818b1`, P2 actual physical source outcome SHA `be66a985016b4ceaae1379c64ee0f6347c3a2e8c4fd3660ceb394227ac237df1`; no target re-selection.
- All source originals checked again after Drive upload by SHA/ZIP CRC. Technical matrix PASS; scientific **HOLD** on mediating transposition table/history state and strategic plan advantage.

**Decision:** do not claim that same reported depth or same requested node budget mathematically blocks budget/history causation. Next actual source-instrumentation stage should inspect the TT entry reached at the frozen gate without perturbing TT replacement metadata and then perform a separately pre-registered physical mediator checkpoint/restore, with a fresh non-flip matched control.
