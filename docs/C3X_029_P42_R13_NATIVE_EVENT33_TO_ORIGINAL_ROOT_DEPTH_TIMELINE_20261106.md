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
