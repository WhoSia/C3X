# C3X 0.30 S4-L/R2 — Italian d4 Return and Warm-Search Choice

2026-11-13 KST. One exposed development FEN. Archived S4-L JSON SHA256 a27b961985d2ba4475f51916c41be3426d8a32d3130bce0fab04497ca2eac5c9. Stockfish16 source 68e1e9b3811e16cad014b590d7443b9063b3eb52 and exact archived S4-L intermediate source SHA verified before instrumentation. The local build has different binary hashes from CI. Original, sham and prefix-two reproduce all six archived final move/depth/nodes/score/PV tuples.

[Patch](../harness/c3x_030_s4l_r2_child_link_patch.py) · [runner](../harness/c3x_030_s4l_r2_italian.py) · [raw logs, build inputs and judge sweeps](https://drive.google.com/file/d/1OqMymcFtHJQiuKLqyXKvfwMHBSqKdyqt/view). ZIP SHA256 7e653f68935e525ef9d8cb5d8055f8448ca841c1371f1aecbaabed7ac448cf29. Build both with make build ARCH=x86-64 from the pinned source; build the instrumented arm after applying the patch to search.cpp. The launcher filtered custom environment values in the local environment. The five arms use separate working directories with the same file-based control format. 10 final-protocol searches plus 10 repeat searches, identical parsed results. Each pass reports 120128 nodes. One thread, hash 16 MiB, classical eval, 12k node cap per go, two consecutive go commands without clearing state. All applied masks were in go 1.

| Arm | Go 1 | Go 2 |
| --- | --- | --- |
| original | b4 | b4 |
| sham | b4 | b4 |
| first hit only | b4 | b4 |
| first two hits | O-O | O-O |
| second eligible hit only | b4 | O-O |

The frozen key is after d3d4, a third root candidate. In go 1 the first 39 root score receipts in the archive are identical. At receipt 39 (zero indexed), the root invocation 43 consumes the return of child 44, PV phase, iteration 2, root window [138,160]. Sham hits, returns normally at -134, and root consumes +134 below alpha. First-hit and two-hit arms mask the TT hit; absent ttMove lowers depth from 1 to -1, delegates to qsearch, returns -149, and root consumes +149 inside the window. These are internal units. Same-run links use epoch and invocation IDs, with move/value/stop consistency checks. The qsearch itself can probe TT; its post-return ttHit=1 is logged. No inference that the TT entry was erased.

The second masked call under the two-hit policy is child 84 at iteration 3, root window [138,160], +149, compared with the same call slot at +134 and a normal return when only the first hit was masked. With only the second eligible hit masked, its identity is instead child 103 at iteration 2, root window [123,149]. Its normal-versus-qsearch route changes while its immediate root value remains +134. The offset is an event-selection policy, and its selected event depends on preceding interventions. The warm-go outcome differs even with equal immediate returned value at the touched call. TT, histories and other search state have not been separately reset or restored. This leaves the complete causal path to the b4/O-O decision unresolved.

## Same-position strategic check

Separate Stockfish 15.1 NNUE run, no mask, 39 and 40 legal Black replies after b4/O-O, 100k per reply and nine 600k follow-ups. After b4, ...Bb6 scored +31 and ...Nxb4 +227; after O-O, ...Bb6 scored +33, ...O-O +23, ...h6 +26, and ...a5 reported an upper bound of +19. At a 1M forced root cap b4 was <=0 and O-O >=+30 in that evaluator's finite reported search. This is a same-family external measurement; repeat in another engine before calling a robust preference. The d4 return path does not yet identify a plan that explains b4 versus O-O. Archived holdout not evaluated. Full mediation, strategy mechanism and learner outcomes remain open.

Next diagnostic: selectively restore the child-44 root return while preserving descendant side effects and separately vary which state survives go 1. The restoration tests sufficiency/necessity in a hybrid execution and should be interpreted alongside the natural same-bin pair.
