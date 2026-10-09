# C3X 0.18 — January Paired-Reader Source Probe Disappearance Court

**Status: ADAPTIVE diagnostic after independent 2026-01 J2–J4 failure, not independent confirmation.** January native SHA: 9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470. January source SHA: 5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533.

The 31 STRICT/BROAD source pair arms (25 distinct physical game-target-call pairs) each allow first and second source V independently. Together, 29/31 group arms block only the first TT value-as-evaluation reader, while the second root search call still has a native window_enter and no matching target pre-gate TT V reader witness. The other 2/31 groups fire both. Every group has full six-field UCI output identical to FIRST-only. These observations do not show whether the second subsearch visits the key, whether TT probing succeeds, or whether bound/value conditions change.

## Fixed post-observation diagnostic cases

- Game #2, STRICT, root calls 4/5, group only first reader blocked.
- Game #6, BROAD, root calls 10/11, group both readers blocked (negative case).
- Game #16, STRICT, root calls 4/5, group both readers blocked (negative case).

No source, root or target substitutions after this contract.

## New passive native C++ hook

Instrument both **main search and qsearch TT.probe(posKey, ss->ttHit)**. Only for the *selected full64 physical TT key and selected second source root-call ID*, log local ply, search depth, alpha/beta, root move ancestry, TT hit bool, physical slot and raw bound/value/eval/depth if hit. Cap at 64 records per process and mark censoring. No search policy or scores modified. A missing TT probe does not prove a search node was never entered; a node might return earlier.

Run F passive, F first-call V, F second-call V and F paired-call V, with double independent cold repeat for each, all in the source-original FEN+clock. Exact final source UCI core must match the earlier January experimental arm; root-call IDs and actual block events must be confirmed.

**DQ1 (risky, adaptive):** #2 paired-call V produces *no TT probe* for the selected key during root call5; if any probe, FAIL.
**DQ2:** #6 and #16 paired-call V still reach the selected key via TT probe with a hit at the second source root call; if not, FAIL.
**DQ3:** all native cold repeats and previous January UCI arms match; otherwise technical HOLD.
**DQ4:** no probe watcher censored and passive watcher preserves source UCI; otherwise HOLD.

Separate **no TT key probe**, **key probed but TT miss**, **hit but value-as-eval not eligible**, and **hit with physical V consumer available**. Prior independent January pair root transfer J2/J3/J4 remain FAILED, whatever adaptive probe explanation emerges.
