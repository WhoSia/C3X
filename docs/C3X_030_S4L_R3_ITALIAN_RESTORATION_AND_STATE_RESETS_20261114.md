# C3X 0.30 S4-L/R3 — Italian Root-Value Restoration and State Resets

2026-11-14 KST. One exposed development position, Stockfish16 source 68e1e9b3811e16cad014b590d7443b9063b3eb52. One thread, 16 MiB hash, classical evaluation, two consecutive UCI go commands each capped at 12000 nodes. Fresh process for every condition. Final design 37 conditions, 74 searches, 888989 reported nodes per pass. Entire design independently replayed in fresh processes using the same build. Parsed results identical. No holdout searches. [Prior R2](C3X_030_S4L_R2_ITALIAN_RETURN_AND_WARM_CHOICE_20261113.md).

## Root consumption intervention

Insert the intervention after all child calls for the first d4 root move in iteration 2, epoch 1, window [138,160], before the root score update. A single receipt links root 43, child 44. In the two-hit treatment, the child still returns -149 via qsearch after restoration, while the root consumes +134 instead of +149. These are internal score units.

| Condition | Go 1 | Go 2 |
| --- | --- | --- |
| Sham natural | b4 | b4 |
| Sham, substitute +149 | b4 | O-O |
| First eligible hit masked | b4 | b4 |
| First two eligible hits masked | O-O | O-O |
| First two eligible hits masked, restore +134 | b4 | b4 |
| First two eligible hits masked, identity +149 | O-O | O-O |

Restoration abolishes the observed flip under the same mask selection policy. In the restored run the second mask lands at child 102 (parent 101), compared with child 84 (parent 83) without restoration. The experiment intervenes on the consumed value and permits later search to respond. It does not fix the identity of the second mask or all downstream state. The complementary sham substitution establishes a warm-go effect for this surgical override but leaves go 1 unchanged.

## Between-go resets

Go 1 matches the archived R2 condition in all reset arms. All mask receipts occur in go 1. Each reset is issued after bestmove and synchronized with the search thread before go 2. TT is TT.clear. Histories is main()->clear, which clears counterMoves, mainHistory, captureHistory and continuationHistory in this single-thread run. Prior is the extra four main-thread fields reset by ThreadPool::clear (callsCnt, bestPreviousScore, bestPreviousAverageScore and previousTimeReduction). Threads combines histories and prior.

| Go 2 | None | TT only | Histories only | Prior only | Threads | TT + histories | TT + prior | TT + threads |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sham | b4 | O-O | O-O | b4 | O-O | b4 | O-O | b4 |
| First hit | b4 | b4 | b4 | b4 | b4 | b4 | b4 | b4 |
| First two | O-O | b4 | O-O | O-O | O-O | b4 | b4 | b4 |
| Second eligible hit only | O-O | b4 | b4 | O-O | b4 | b4 | b4 | b4 |

Under second-hit-only, preserving TT and histories supports the observed warm flip in the tested reset matrix. The prior-field reset alone preserves that flip. Under first-two, only arms including TT clearing remove the warm flip. Sham switches under individual TT/history clearing and returns to b4 under their joint clearing. This is an intervention interaction on the observed decision; clearing affects all entries in the selected group. Entry-level sufficiency or transplant effects remain untested. Stockfish16 UCI Clear Hash calls Search::clear, which clears both TT and Threads and additional state. It cannot stand in for the TT-only arm.

Next: swap TT and history state between sham and treatment at the go boundary, holding prior fields constant, then narrow the successful swap to concrete TT entries and history cells. Strategic significance and learner outcomes remain unresolved.

[Patch](../harness/c3x_030_s4l_r3_patch.py) · [Runner](../harness/c3x_030_s4l_r3_italian.py) · [Raw UCI and stderr, manifests and replay](https://drive.google.com/file/d/1Yzmtbcvz8QJrewvdeEsXBef0WfQfZc8h/view). ZIP SHA256 baa92ecadd679ce6a2d5b79edab9d8ac3c540abf137e562f65ddded0bc4f62a3. Instrumented binary SHA256 5f9685f35f99b2894f70e54a4f68e136d5b94070d1e4f20bcd29e6b0e499f984. Build the pinned original with make build ARCH=x86-64, copy that binary, apply R3 patch to the archived R2 search.cpp and pristine UCI source, rebuild with the same flags, and pass both binaries, a new output directory and archived r2.json to the runner.
