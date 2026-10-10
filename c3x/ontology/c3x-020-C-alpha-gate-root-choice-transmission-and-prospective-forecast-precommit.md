# C3X 0.20-C — Threshold-Mediated Root-Candidate Promotion & Search-Path Reentry

**PRE-NATIVE-OUTCOME REGISTRATION • 2026-10-10 • C3X 0.20 ACTIVE**  
**Scientific objective:** explain and predict *final root-choice changes*, not the number of instrumentation events. This is a mechanistic adversarial test of a known adaptive result followed by a disjoint prospective prediction design.

## Historical claims kept exactly

- 0.18 physical TT-writer and actual score-consumer evidence: validity of source contact ≠ proof of root choice.
- 0.19 February F19.5 **FAIL**, January J2/J3/J4 **FAIL**, old P1 R5 **FAIL**; 0.19 one-site return K4 **FAIL 0/4**.
- 0.20-B source-native four-case court https://github.com/WhoSia/C3X/actions/runs/38033739366 **SUCCESS**; in previously outcome-selected game #3 STRICT, `SECOND_ONLY` returns `a1c1` in place of V `e1e3` by restoring exact depth4/rootcall4/trial1/move222/index5/alpha−190/beta−166 child return −179→−206. No second-return recovery in games6/10; game7 event not source-aligned. This is **a real bounded interventional root-choice rescue in ONE adaptive case**, not a universal alpha-gate law.

## Exact source competing mechanisms

At pinned official Stockfish16 commit `68e1e9b3811e16cad014b590d7443b9063b52` in `src/search.cpp`, after native child search / `pos.undo_move(move)` / stop check, root node:
1. `rm.averageScore = (2*value+oldAverageScore)/3` (or first value) **regardless of crossing**.
2. For nonfirst root moves `value > alpha` updates `rm.score`, `rm.uciScore`, `rm.pv`, bounds; otherwise `rm.score=-VALUE_INFINITE`.
3. Independently `value > bestValue` followed by `value > alpha` may update root `bestMove`, alpha and next search depth; `value >= beta` may trigger fail-high.
4. In iterative deepening the aspiration retry window and `stable_sort(rootMoves)` transmit candidate state into deeper trials.

The **exact native source gate** is `moveCount==1 || value>alpha`, and the target is **moveCount=5**. For #3, alpha=−190, beta=−166: the V −179 return is > alpha; −206 is < alpha. This gate crossing is a plausible mediator, but `averageScore` (and downstream score magnitudes) are alternative channels. Newly instrument three gate booleans directly at the exact native return site: `candidate_update_gate`, `alpha_improvement_gate`, `beta_boundary_gate`. Source event and unchanged OBS/SHAM controls are mandatory.

## 0.20-C1 bounded critical-value ladder: predictions FROZEN before any fresh native results

Same frozen February game #3, first-return restoration OFF in all arms. The only edit is the same actual C++ second-return site from the 0.20-B source code. Independently replay frozen F, V FIRST and read-only OBS, impossible-move SHAM, each twice cold. **No choosing another index from outcomes**.

Exactly these six treatment targets, in this fixed order:

| ID | Target value | Difference relative to native α=−190 | Predicted gate | Predicted final `bestmove` under sharp-gate H_G |
|---|---:|---:|---|---|
| L0 | −206 | −16 | 0 | `a1c1` (historical replicate, not independent) |
| L1 | −191 | −1 | 0 | `a1c1` |
| L2 | −190 | 0 | 0 | `a1c1` |
| L3 | −189 | +1 | 1 | `e1e3` |
| L4 | −180 | +10 | 1 | `e1e3` |
| L5 | −179 | +11 | 1 | `e1e3` (natural-value sham) |

**Primary H_G risky prediction**: in all six contacted two-cold runs, final categorical bestmove equals predicted value above; a single mismatch FAILS this sharp-gate threshold classifier. Additional primary `H_C`: across **L2 and L3**, one-unit change with unchanged source move/position/contact makes the candidate gate change 0→1 and the final bestmove change `a1c1→e1e3`. If either half fails, FAIL. Reject post hoc bestmove bucketing or approximate gate widths. **Competing H_M**: if target values on one side of alpha produce differing final choices, continuous `averageScore`, PV/TT state or other magnitude-sensitive routes compete with the sharp gate. Keep all outcomes and no-contact runs.

Measured secondaries: exact native root-site contact, gate booleans, cold identity including full UCI, first observed terminal `after_sort` leader at depth4, first later leader divergence depth5–12, total nodes, retry counts. These are not replacements for primary outcomes.

Technical fail-close: loss of exact source site, missing/duplicate contact, source gate log not matching `int(target>alpha)`, changed OBS/SHAM full UCI, F/V root UCI drift from 0.20-B original, or cold mismatch. Failure is TECHNICAL_HOLD, not biological/chess hypothesis FAIL. Preserve original 0.20-B artifact and B result as separate identities.

## 0.20-C2 genuinely independent next-ecology design (NO OUTCOMES INSPECTED)

**Candidate new archive:** March 2026 Lichess broadcast PGN `https://database.lichess.org/broadcast/lichess_db_broadcast_2026-03.pgn.zst`, subject to independently confirmed availability and provenance. A fixed script SHALL select **16 new positions without ANY chess engine**. Use the February engine-free selection contract (first 20k games, first 512 legal eligible, >=70 plies, ply 30+(first8 game-header/mainline SHA mod15), source-SHA sort first16), while excluding historical P4 October–February FEN4 overlap (including February's current cohort) and duplicated game hashes. New source SHA, selected FEN4 / clocks / legal move metadata and source fingerprints frozen before a single native engine run. If fewer eligible or archive unavailable, `SOURCE_HOLD`, no replacement month/selection tuning.

**Independent mechanistic prediction rule (pre-outcome):** For each source-selected March game, evaluate **one** fixed STRICT and one fixed BROAD existing source TT-consumer role with **existing unmodified 0.19 criteria**; preserve NO_ELIGIBLE and all original denominator records. In a separate shallow source-native depth4 reconnaissance for original F vs V FIRST, using first original semantically matching nonfirst-root `candidate` event with equal move and alpha/beta, classify `GATE_UP` (F child ≤ alpha; V child > alpha), `GATE_DOWN` (F > alpha; V ≤ alpha), or `SAME_GATE`. This reconnaissance must be source-native, predeclared, with no 12-depth outcome exposed. **Risky prediction:** at depth4 terminal leader, `GATE_UP` predicts V elevates a different leader relative to F and `GATE_DOWN` predicts F elevates a different leader relative to V; `SAME_GATE` predicts no same-depth terminal leader change. For categorical final depth12 `bestmove`, predict **at least one flip in GATE_CROSS eligible arms and no flips in SAME_GATE**. If any SAME_GATE has a final categorical flip, this restrictive theory FAILS; if the GATE_CROSS denominator >0 but none flips, FAIL; if none eligible, `NO_ELIGIBLE / INCONCLUSIVE` not PASS. Further, any gate-cross case with no predicted same-depth leader outcome is a signed prediction failure. These are purposefully risky, not retrospective classifications.

**Independent integrity:** fixed denominators 16 games × two source-role selectors (max 32), duplicate role/physical keys reported separately; original FF/FIRST source masks preserved; unmodified source game context, cold twice, field-complete UCI output, valid position and full64 TT key check. No assumption March eligibility/rates; not a promise of generalization. A depth4 probe cannot be considered identical to the first 4 depths of a depth12 run if process history differs: use fresh cold engine for each, clearly distinguish their observational contexts and count any misalignment as epistemic HOLD.

## Development and operational policy
1. Few purposeful source edits, modular pure classification with unit and metamorphic tests; no rank-guessing after observing results.
2. One meaningful combined read-only Actions run after fixed tests for C1, then separately authorize March source freeze/independent holdout only after verifying actual source provenance. No auto GitHub commits or bot authors; WhoSia-only, main-only.
3. Explicit STOP if merely increasing counter traces without a testable chess-choice forecast. Preserve all original failed verdicts. C3X final target is **causal explanation of different legal chess moves**, not TT-cache taxonomy.
