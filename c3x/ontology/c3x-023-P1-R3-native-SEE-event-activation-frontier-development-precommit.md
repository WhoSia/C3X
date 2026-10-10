# C3X 0.23-P1-R3 — Search-Frontier SEE Activation, One-Sided Native Operator Events & Chess-Microstructure Causal Limits

**2026-10-11 KST | READ-ONLY development precommit before first R3 frontier result. No SEE Boolean actuator.**

## Frozen input and why R3 differs from T2

- C3X 0.23 S0 licensed source32: SHA `0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61` (May2026 broadcast CC BY-SA 4.0 plus CC0 nonmate puzzles).
- Stage A native untreated SHA `fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442`.
- R2-T1 exact source window observation SHA `1975a515755e31a4c9445239750bde88211a13c328f667d86cabba2ce58effeb` (6 previously outcome-selected dev games; 21 post-real-TT common events; 2 trace-censored).
- R2-T2 exact source SEE site 2x2 SHA `e72ec883b78ed2a600c6c3ae8a095805485fe031649b7aade0437f08d35cbad3` (one actual qsearch_prune source site, two physical bool doses, zero terminal UCI added changes; 5 HOLD). T2 **NEGATIVE** preserved.

A shared SEE event after TT source use is a **common descendant**, not an identified mediator. Exactly perturbing one shared qsearch event had no additional final bestmove effect. This motivates a DISTINCT read-only question, not retrospective rescue: **do native SEE invocation / search-window states occur on only one branch of the TT first-consumer counterfactual?**

## Fixed controls and event sets

Use EXACT SIX preidentified dev cells `(1,O,STRICT),(8,O,BROAD),(11,F,STRICT),(12,F,STRICT),(2,O,STRICT),(3,O,STRICT)`; no resampling, including 2 no-flip controls and 2 censored cases. Original native SF16 pinned `68e1e9b3811e16cad014b590d7443b9063b3eb52`, 1 Thread Hash16 NNUE OFF depth12. Native score-used/cutoff original and real TT `reader_block` must correspond to original source physical `key64/slot/epoch/root-call/root-candidate`; duplicate cold baseline and TT-FIRST required; original six-field UCI baseline invariant. Reproduce complete R2-T1 source result SHA *byte-for-byte* before any frontier finding; if drift -> stop. **No SEE value flips in any arm**.

For each root and arm, observe native SEE events AFTER (strictly later UCI line ordinal than) original first actual TT score use/cutoff or the TT-FIRST physical blocked reader event. Each native `see_ge` event represented by:

`E=(full original ancestor key vector, rootcall/root candidate, native pos.key and parent, native move, four-site source name, threshold, ply/depth/alpha/beta/PV/rule50/initial occupancy, original boolean)`.

Define in-arm multiplicity; duplicate exact event fingerprints are ambiguous and quarantined. Let `E_0,E_1` be observed post-source event sets (window-limited to first 32 source watches, NOT the entire engine search tree):
- `C=E_0∩E_1`: common full measured SEE state.
- `D_0=E_0\setminus E_1`: observed original-only post-source events.
- `D_1=E_1\setminus E_0`: observed TT-FIRST-only post-source events.
- `W`: same chess path and SEE site/move/threshold seen both sides but different live computational window; classify as **state divergence**, not absence.
- `P`: an event observed after source in one arm but only before source in the other: temporal migration, not simply absent.

Compute per-original-site counts for `capture_prune`, `quiet_prune`, `qsearch_prune`, `qsearch_futility`, with original Boolean true/false if recorded. **No union across strata as independent games**; report per-game status, original vs first, flag censored and whether actual bestmove flips.

## Hard limits

- A **first32** event observer that censored ANY arm cannot certify source-event absence. Mark one-sided events as `OBSERVED_PREFIX_ONE_SIDED__NOT_GLOBAL_ABSENCE`, not causal extinction.
- Any 64-bit path hash match that disagrees with full hexadecimal ancestor key vector is not the same event. All caller alpha/beta, rule50, occupancy input and full descendant path must be compared; source recursion implicit states may still differ.
- For capture source SEE, `occupied` is a possibly uninitialized **OUTPUT** of Stockfish `see_ge`. NEVER dereference it; original `pos.pieces()` is the defined input occupancy. Also, native capture SEE false is not equivalent to actual move prune due extra discovered-attack checks.
- A state `E_0` absent from `E_1` is **evidence of observed search-path/activation asymmetry**, not automatically a proven TT→SEE→final-choice mediated causal effect. Need independent source-identity-specific gate intervention and root-choice outcome to test that.
- Source game #2 no-flip has 14 late common original and V native SEE records; it is the negative control to keep causal explanation falsifiable.
- Dataset already developed on R1 outcomes. No M3 predictive claims; new M3 exact-UCI positive validation requires later blind cohort.

## After empirical evidence (future T4, never performed as part of R3)

If stable one-sided source events exist and have their actual path source provenance and pruning decision, preregister a **branch-activation intervention** (targeted enable/disable exact source site without changing chess legality or SEE algorithm). Do not arbitrarily toggle an event at a different node in the opposite arm. Investigate geometric recapture and defender edges at actual descendant chess positions; do not mistake named pin/SEE motif labels for measured causal mediation.

**T3 read-only status: PRECOMMITTED.** Rights: share only aggregate/source hashes/Stockfish patch SHA; no complete PGNs, player names, modified Stockfish binary, or source-derived full board history.
