# C3X 0.19 — P4 First Divergent Root Return, One-Site Counterfactual Restoration Court

**Protocol frozen before running the new native intervention. Status: ADAPTIVE source-case falsification (NOT an independent population study).** Four February-2026 games, known after the independent F19.5 FAIL: game #3 STRICT, #6 STRICT, #7 BROAD, #10 STRICT. Original source-only SHA `2942b1933030227f36b669faff41f15ff234c27127dbf2403bf2e8e4f12ebdc8`; full prior prospective source SHA `2a67839faf37c19ac1749c9b88200546c04f33e2b397159435a4ab97434fee74`; adaptive full root witness SHA `6601dc3397ce939ce61a5bd85ec91190292e823a40230978569f5705e717d613`. Frozen upstream SF16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`.

## Question and surgical point

Does fixing the **first *observed* semantically divergent root child return** to its unchanged-F source value, only after child search has completed and the move is undone, alter that trial's stored root candidate score, aspiration outcome, or final root choice? This is an artificial direct edge intervention `do(root_return := F_observed_value)`, not a restoration of a TT writer, the recursive search or the counterfactual entire history.

Patch one unique source site in `src/search.cpp`: immediately after stop condition and before `if (rootNode) { RootMove& rm... }`, where child return is in mutable local `value`; perform match only when `rootNode` and ALL these predicates match from the frozen source FIRST event: root depth, observer-local root call and trial, move ID, move index, alpha, beta, and expected pre-repair source return. Allow **one actual edit only**; log the native before and after values plus exact predicates. A separate passive OBS mode must record without editing. If the source state is not reached, report `NOT_FIRED`; never select another candidate.

| Game | Depth | Call/trial | Move ID / index | α, β | Original F return | FIRST return |
|---|---:|---|---|---|---:|---:|
| 3 STRICT | 4 | 4 / 1 | 231 / 2 | -190, -166 | -1031 | -967 |
| 6 STRICT | 10 | 19 / 2 | 1291 / 1 | 94, 114 | +103 | +114 |
| 7 BROAD | 4 | 4 / 1 | 2917 / 3 | -343, -334 | -613 | -642 |
| 10 STRICT | 4 | 4 / 1 | 2910 / 2 | 103, 123 | -459 | -892 |

These event identities were obtained from the *same semantic prefix* of F and FIRST logs, not selected after any new rescue-arm output. Observer counters and root-node counts are not matching criteria.

## Frozen test arms, every game

- **F:** native F mode, TT reader observer only; complete six-field original UCI must equal original February F.
- **FIRST:** original native V-FIRST source TT consumer gate; complete original six-field UCI and actual first V block must reproduce prior February.
- **FIRST+OBS:** same V-FIRST with read-only return-site event witness, no value change. Must produce exact FIRST UCI and one source match with original FIRST child return.
- **FIRST+REPAIR:** same V-FIRST plus one return substitution FIRST→original F at the locked root source site. Record actual value before/after, current root-call/ply/candidate and later trial/leader outcomes.
- **FIRST+SHAM:** same V-FIRST plus an impossible native move ID (65535) that produces no return-site contact and exactly preserves FIRST six-field UCI.

Each arm is run in **two independent cold processes** with Threads1, Hash16, depth12, NNUE OFF, same authentic half/full move FEN; every original source game and selection is frozen. Preserve all raw `c3x017_root_event` records (cap 4096), P4 root contact, original TT reader gate events and any native-use evidence. No editing chess legality or replay history.

## Explicit scientific failure predictions

- **K1_EVENT_CONTACT:** 4/4 FIRST+REPAIR runs match exactly the pinned original source candidate and fire **once**. Less => FAIL / NO_SOURCE_CONTACT (do not retarget).
- **K2_LOCAL_RETURN:** 4/4 actual changed child returns equal the frozen F return and produce the expected source candidate-after behavior. For #6, +114 (β)→+103 (interior), candidate-after must change to 103; for #3/#7/#10, both returns remain below α and source candidate-after remains `-32001`.
- **K3_BETA_GATE_TRANSPORT:** #6 root depth10, source call19/trial2, must cease its immediate β crossing; if stored candidate-after does not change as predicted, FAIL. This is only a local score gate prediction.
- **K4_FINAL_ROOT_RESCUE:** **at least one** of the four final bestmoves is restored from FIRST's move to the original F bestmove by the one-site return repair. Zero => FAIL, and original F19.5 remains failed.
- **K5_SHAM_NONINTERFERENCE:** four source sham arms have zero contact, preserve FIRST full six-field UCI and exact first TT block identity; FIRST+OBS also preserves FIRST UCI.
- **K6_SOURCE_COUNTERFACTUAL_IDENTITY:** all matching predicates, physical first TT block and prior unmodified full UCI match frozen source; any mismatch technical HOLD.
- **K7_FULL_DENOMINATOR:** all four fixed games, all five arms, cold duplicates, no report omission, no root trace censorship; source error => HOLD, no new game selection.

Local C++ restoration after undo does **not** roll back child-node TT writes, search counters or iterative history; if final bestmove isn't rescued it establishes the insufficiency of that **one edited return site**, not that downstream root competition is TT independent. An actual final root rescue, if it occurs, establishes only *sufficiency of a synthetic local return intervention* on this adaptive fixed game, not unique upstream natural mediation or external validity.

## CI budget and contributor contract

Build source patch and fail-closed unit/source tests in several human-authored GitHub commits. Run **one combined read-only GitHub Actions** after all code is finalized. GitHub Actions permissions `contents: read`, never push/commit/merge. Only WhoSia author/committer; no bot coauthor. Preserve every old independent FAIL: January J2/J3/J4, February F19.5 and original unbounded P1 R5.