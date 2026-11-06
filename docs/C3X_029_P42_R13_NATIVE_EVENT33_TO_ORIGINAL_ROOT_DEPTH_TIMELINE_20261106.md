# C3X 0.29-P42/R13 — Same-Execution Original Cycle Event 33 to Root Iteration Timeline

Date: 2026-11-06 KST. **Program-execution mechanism experiment, pre-outcome chronology interpretation.** Not a standalone metrics publication, not a proof of independently valuable chess future.

## Proven original source intervention

R11 native [#42177462049](https://github.com/WhoSia/C3X/actions/runs/42177462049) identified **four** actual cycle-alpha `value_draw` cutoff decision disagreements within B's first 33 native same-input pre-return events. R12 [#42179676099](https://github.com/WhoSia/C3X/actions/runs/42179676099), original pinned Stockfish16, Game14 postselected/NNUE OFF, source verified the four actual original B cycle events selected before observing any single-event root result: **30,31,32,33**. Each independently neutralized (two `cold()` invocations, each two physical engine `play()` subprocesses): 30/31/32 each keep B=f3f4, **event 33 alone changes B=f3f4→b3a4**. This is a true source-local functional counterfactual, not natural-mediator uniqueness. [R12 downloaded ZIP and verified SHA manifest](../evidence/C3X_029_P42_R12_SINGLE_CYCLE_EVENT_NATIVE_RECEIPT_MANIFEST_20261106.json).

## The next source question

**Which observed root iterative-deepening boundary first diverges AFTER event 33 changes the native cycle-alpha cutoff?** This does not yet establish how every ancestor's search-window value was transported. It does confront a specific executable cause with an original 0.27 root observable under the same physical engine history.

Existing old `tools/c3x_027_game14_passive_lineage_overlay.py` (not reinvented here) already emits `event=ROOT_BOUNDARY depth=D leader=L score=S average=A` into `C3X027_GAME14_LINEAGE_LOG` for every completed search depth. R13 uses **the identical actual source run's private file** for BOTH `C3X027_GAME14_LINEAGE_LOG` and `C3X042_R11_CYCLE_WINDOW_TRACE`. Each native `play()` thus has a single interleaved chronological trace of source cycle windows and original root depth summaries. This is stronger than comparing different binaries or timestamps from separately run traces.

The `cold()` helper launches exactly **two distinct physical `play()`/UCI engine processes**, then verifies output equality. Before analysis, R13 splits the two identical complete mixed native source logs, requires deterministic equality, and invokes the original strict `parse_boundary_lines` court to validate exactly two monotonically increasing and identical depth runs. R10 source-call counts must equal two times the per-physical-play R11 cycle events.

The source patch compiled into R13 is unchanged from the fully successful R12: only the native **33rd cycle-alpha draw return**, and only within an independent physical B engine, is set to 0. Everything before source event 33 must match original source position hash, ply, depth, node bit, incoming alpha and beta. The original B=f3f4 and target33 B=b3a4 must both reproduce twice. The **first** root boundary that differs in leader, score, or average must physically occur **after** the 33rd source event in both original and target runs. If it occurs earlier, native chronology contradicts the proposed causal ordering: HOLD.

## Falsifiers and reporting boundaries

- Any source SHA/StageA or physical TT reader drift: HOLD, no re-selection.
- Original vs target event33 pre-source state mismatch: HOLD.
- Two native processes within one `cold()` have nonidentical source-event/interleaved-depth logs: HOLD.
- Root boundary iteration support changes: **separate HOLD** (important dynamic support, not a fabricated alignment).
- Any pre-target root-boundary change or root divergence preceding event33: HOLD on simple temporal bridge.
- Event33 physically precedes the first root score/leader divergence with stable cold: local source event-to-observed root *temporal relation* PASS. **This is NOT a complete measured value/bound ancestor chain or natural guard-to-root mediator identification**, because TT/history/other search states may propagate the cause and root leader summaries are still aggregates.
- Independent chess-counterplay strategic meaning, NNUE mediation and heldout games remain unverified; R13 must not claim an authored paper or prospective causal transfer.

Implemented [same-native-run temporal court](../harness/c3x_029_p42_r13_native_single_cycle_to_root_boundary_court.py), [11 synthetic adversarial tests](../harness/test_c3x_029_p42_r13_native_single_cycle_to_root_boundary_court.py), [read-only native workflow](../.github/workflows/c3x-029-p42-r13-native-event33-root-bridge.yml). Native [run #42180911683](https://github.com/WhoSia/C3X/actions/runs/42180911683) registered and started; final genuine native result not asserted at document creation. Initial [#42180783786](https://github.com/WhoSia/C3X/actions/runs/42180783786) failed synthetic test due to overescaped *regex used to parse exact root depth*, preserved as technical failure and corrected; not a chess causal falsification.

As always, raw chess source histories, source keys, child frames, modified GPL binaries and complete per-event logs stay private; only rights-gated aggregate root boundary results released. GitHub authors human WhoSia, Actions `contents:read`; Notion semantic truth, Drive immutable original bytes when actually verified, no invented mirror.


## 2026-11-06 — Native original same-execution event33→root boundary result (verified)

[Read-only pinned SF16 native run #42180911683](https://github.com/WhoSia/C3X/actions/runs/42180911683) **SUCCESS** after strict source regression, full original 16-game StageA verification, physical TT reader certification, original B=f3f4 and target-only event33 B=b3a4 cold controls. Two independent `cold()` runs each contained two actual physically independent engine `play()` processes, and exact interleaved source-cycle/root-depth logs were validated as equal between the two physical subruns.

The **first root iterative-deepening boundary that differs is depth 9**, and the physically selected source cycle-alpha event #33 is observed **before that root boundary** in both original and source-intervened B executions. They completed **12 depths**, with **4 different root depth boundaries**.

| Native root depth 9 | B original TT_FIRST | B with only source event33 changed |
|---|---:|---:|
| source leader native move | 1373 | **1112** |
| source best score | -74 | **-89** |
| source average score | -70 | **-80** |
| final unrestricted root UCI action | f3f4 | **b3a4** |

This provides **controlled local functional causation + within-the-same-engine source temporal precedence + original root boundary change**, not simply a value correlation or a reconstructed generic PV.

### Historical C guard intervention has a related but NOT identical root boundary

Previously verified old C3b [R7 report](C3X_029_P42_R7_NATIVE_FAIL_LOW_WITH_ROOT_RESTORATION_CAUSAL_DIAGNOSIS_20261106.md) also places the first B/C root divergence at **depth9**, with original C (one exact `capture_prune` guard bypass) native root leader **1112**, score **-89**, average **-79**. The new independent R13 source event33-only B root at depth9 has the **same leader 1112 and score -89**, but its average -80 differs by 1. Both interventions restore final root b3a4.

**This is a concrete, important convergence candidate**, NOT yet identification of an equal natural causal pathway or identical full search state. Equality of source root leader and score at a particular completed depth does not imply equality of TT tables, alpha-beta ancestry, search tree, aspiration states or eventual strategic future value. The average-score difference demonstrates that even the depth9 source summary vectors are not perfectly identical. A next intervention should compare B, exact old C and B33 **in one compiled source native cohort**, with source state and depth-by-depth boundaries, checking earlier/later divergent source trajectories. The old C candidate score is historical separately-run evidence, not yet matched to the new B33 within one process pair.

**Direct independently downloaded artifacts and SHA:** ZIP #13485611324, SHA256 `0819ecc5d2251db6dbdc3c75cf05ec89646a8183994ba8bfb930ea153ec5a8f0`; contained `C3X042_R13_EVENT33_ROOT_BOUNDARY_CHRONOLOGY.json` member SHA256 `cd7fc80c1e75bf5f13e6434353db513934c988e76b96241e1948044ac86b1909`. [Permanent custody manifest](../evidence/C3X_029_P42_R13_SINGLE_EVENT33_ROOT_BOUNDARY_RECEIPT_MANIFEST_20261106.json). Raw source keys and chronological log private, never transferred to public artifact.

**Early R13 technical CI:** [#42180783786](https://github.com/WhoSia/C3X/actions/runs/42180783786) failed a synthetic test because root-depth regex was overescaped and could consume adjacent whitespace. The exact source parser was repaired without changing any original Stockfish code. Later successful #42180911683 is the valid native experiment; the initial failure is retained.
