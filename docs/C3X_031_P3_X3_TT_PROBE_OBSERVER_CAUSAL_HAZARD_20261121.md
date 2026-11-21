# C3X 0.31/P3-X3 design audit — A second TT.probe is NOT a passive observation

**Source verified:** official Stockfish16 pinned `68e1e9b3811e16cad014b590d7443b9063b3eb52`, [src/tt.cpp lines 120–130](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/tt.cpp#L120-L130), inspected from the exact primary source. In that version, `TranspositionTable::probe(key, found)` is declared `const` but modifies the matched entry's **`genBound8` generation/age metadata** when a matching key16 or an empty slot is seen:

```cpp
tte[i].genBound8 = uint8_t(generation8 | (tte[i].genBound8 & (GENERATION_DELTA - 1))); // Refresh
```

That is an *actual write to search memory*. A seemingly harmless extra `TT.probe` inserted by a C3X logger can change the age of stored entries and thereby influence subsequent TT replacement decisions. It would **invalidate a 'passive observer' claim unless independently controlled**. This is not just a CPU timing issue. The lookup is also only a **16-bit partial key match** inside its bucket, so a raw TT slot observed later must not be declared the same full position without verifying that identity.

## Concrete implementation contract for the next native source patch

1. Do **not** call a new `TT.probe` from `C3X_R33_OPEN` or `C3X_R33_CLOSE` merely to log TT state. Reuse the source's **already performed** lookup `tte = TT.probe(posKey, ss->ttHit)`, its `ttMove`, `ttValue`, and `ttPv` in scope before a registered futility return. Include original `posKey`, cutoff window `alpha/beta`, score boundary `floor`, original parent `statScore`, original `thisThread->nodes`, raw TT hit flag, bound, depth and entry value; do not dereference an unvalidated full-position identity.
2. For after-child logging, if retaining the same previously obtained `TTEntry*` pointer in the existing `R33Call` structure, treat its later content as a **physical slot snapshot** that may have been replaced by a different position. Never call it a `posKey`-verified post-treatment same-position TT state without separate key identity evidence. A shadow map of original writes keyed by full source `posKey` is an alternative observer, but its memory/time costs and observer parity must be measured; it is not a cost-free probe.
3. **Observer equivalence required:** original identical R33 binary with logger off; proposed overlay binary with logger off; proposed overlay with new TT logging on; each native original root UCI and producer parity. Add restore/cold repeat, and keep any execution that changes the original source recommendation as failed instrumentation, not an 'interesting source effect'.
4. **Mediator identification not obtained by snapshot:** TT post-state differences across futility/null interventions can merely be downstream consequences of changed search work. An actual causal mediation claim requires **restoring a specified TT entry state at a specified original search boundary** while controlling history/order and budget as separately as possible, plus valid sham, swap and reverse-swap arms. TT collisions, generation refresh, event eligibility, and stop budgets are confounders to report.
5. The P2 source pair `P2-052-1`, `P2-056-1` is especially informative for **null-dependent** root flips and the separate `P2-005-0` for **futility-only** root flips; all are already exposed, so treat these as mechanism development, not blind validation.

**Decision:** source-correct TT observer first; no unguarded extra `TT.probe` is allowed. A new TT-snapshot result by itself can never promote 0.31 to proved minimal intervention-stable state.
