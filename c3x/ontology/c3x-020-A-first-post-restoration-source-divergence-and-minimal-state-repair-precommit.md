# C3X 0.20-A — Residual Search-State Persistence & First Post-Restoration Candidate Divergence

**Status: READ-ONLY ORIGINAL-ARTIFACT AUDIT COMPLETE; FUTURE MULTI-STATE EXPERIMENT PRECOMMITTED IN DESIGN ONLY.** 2026-10-10. ACTIVE C3X 0.20. Historical 0.19 K4=FAIL 0/4, F19.5=FAIL, January J2/J3/J4=FAIL unchanged.

## Verifiable frozen evidence
- Actions https://github.com/WhoSia/C3X/actions/runs/38031332649 ; artifact ID 11662640185 (`c3x-019-four-original-root-return-one-site-rescue`).
- Artifact zip SHA256 `fc2f7848bc8ba67fa667819f3cee54d27f7d2229e70b3d269349d6ebb2cf7128`.
- Inner native JSON `FEB4_ONE_SITE_RETURN_ROOT_CHOICE_CAUSAL_COURT.json` SHA256 `8639dc5d512ffb9a421164fe2631698af59e76b876aa43ac2aee99378045ab47`.
- Four post-outcome selected February source cases #3 STRICT/#6 STRICT/#7 BROAD/#10 STRICT; native Stockfish 16, one return-value edit. No prospective outcome claim.

## Observed first semantic divergence (ignore only `seq` and `root_nodes`)
Events were compared **as recorded and before trace path split**, not as proof of identical hidden search state. F=baseline; V=FIRST; R=FIRST_REPAIR. Event index below is 0-based. Their total event lengths differ and **no cross-arm post-split position-by-position equivalence is assumed**.

| Game | V vs R first differing event | F vs R first differing event | Interpretation |
|---|---|---|---|
| 3 | index 113, depth4 candidate #2 move231 return -967→-1031 | index 116, depth4 candidate #5 move222 F -206 vs R -179 | First edited value restored; a later same-trial return remains different. |
| 6 | index 776, depth10 candidate #1 move1291 +114→+103 | index 777, depth10 candidate #2 move1307 F 89 vs R 96 | The NEXT candidate in the same depth10 aspiration trial is already different; beta/local exit restore does not equal trial state restore. |
| 7 | index 111, depth4 candidate #3 move2917 -642→-613 | index 257, depth7 candidate #16 F move4079/-414 vs R move3248/-432 | Identical log prefix after local repair persists to depth7, where candidate identities differ; do not compare scores as same move. |
| 10 | index 137, depth4 candidate #2 move2910 -892→-459 | index 182, depth4 candidate #2 at trial2 move2910 F -459 vs R -892 | First repaired event aligns locally; later retry has a differing return for that move. |

The F/R first-difference indices are first **observed logged** mismatches, not earliest physical or causal state differences. F and R traces are respectively 695/566 (#3), 1141/971 (#6), 513/482 (#7), and 1397/1297 (#10). A path difference or different candidate move prohibits source-event identity despite matching `root_call` and list position.

## Game6 root-outcome depth milestones (final after_sort for each depth)
- F depth10: leader move1291, value103, trial2; V depth10: leader move1291, value88, trial5; R depth10: leader move1291, value103, trial2.
- F depth11: leader move926, value194, trial7; V depth11: move1291, value102, trial2; R depth11: move1291, value119, trial2.
- F depth12: move926, value132, trial4; V depth12: move1291, value117, trial3; R depth12: move1291, value119, trial3.
- Final F `g2g4`, V/R `e3d2`; R nodes138901 vs V117111 and cp36 vs cp35.
Thus root depth10 terminal score/leader/retry **match F** after return repair, but the NEXT candidate return at depth10 already fails to match F and depth11/12 leaders do not recover. The claim that the first residual difference occurs only at depth11 is FALSE.

## What is NOT established
- Logs exclude full TT, history, PV, rootMove averageScore, and all subtree state. Equal observed prefix does not equal complete search state.
- Time-ordering and observed correlation do not identify a unique TT or persistent-state mediator.
- Comparison by equal log index after differing move order is not admissible for value attribution; mark `PATH_DIVERGED`.
- The synthetic substitution after child undo cannot reverse completed TT writes or child-search side effects.

## Bounded 0.20-B multi-state source experiment — frozen design (NOT EXECUTED)
Primary endpoint for all four existing cases: final categorical `bestmove == F`. Secondary endpoints separately: local child return, candidate score, aspiration boundary/number of retries, depth-d final root leader/value, subsequent depth leader, final UCI. No retroactive switching of primary endpoint.

Factorial limited arms per fixed case, with same F, FIRST, OBS, SHAM cold independent duplicates:
- A0: original FIRST with exact **single** return repair (existing control).
- A1: A0 + reset *only* target rootMove.score/averageScore to the F snapshot at a pre-specified source position after candidate update. Declare whether value was actually changed, and require exact source contact.
- A2: A0 + pre-specified depth/trial aspiration window reentry consistent with F's depth-boundary state, via a separately named source guard. Do not silently change alpha/beta inside a running child search.
- A3: A0+A1+A2 only if source invariants make it well-defined and the equivalent sham and matched no-contact negative controls pass. Otherwise report NOT_IDENTIFIABLE/UNIMPLEMENTABLE, not PASS.

Before running: freeze selectors per game, the exact snapshot location, score/averageScore semantics, retry-state transition and source-anchor SHA. Fail-closed on mismatched move/position/depth, missing or multiple contact, altered legality, traces exceeding logging caps, UCI drift in F/V/OBS/SHAM, or cold mismatch. Preserve TT child side effects explicitly. Report actual delivered intervention dose, not intention-to-treat alone.

**Prospective gate:** These four cases are exploratory and outcome-selected; do not treat any successful multi-state intervention as a general law. Predeclare new PGN/engine-free selector, outcome metrics and failure predictions before fresh native testing. One consolidated read-only Actions run only after source regression tests and all controls are locally checked.

## Operational doctrine
Preserve main only, WhoSia-only commits, no Actions bot pushes, historical FAIL/HOLD receipts immutable. Prefer local study to CI. If a proposed repair relies on F state from a different search history without a source-coherent insertion location, stop and document non-identification.
