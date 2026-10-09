# C3X 0.18 — Source-Witnessed Search Memory, Reentrant Root Selection & the Limits of Mechanism Equivalence

**Status: ACTIVE / experimental mechanism finding, not a natural-mediation closure.** Research source frozen at Stockfish 16 `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Threads=1, Hash=16 MB, NNUE disabled, depth12 unless stated. Frozen standalone source FEN worlds are not the original repetition histories.

## 1. Primitive issue

If two exact interventions produce the same chess engine root move, evaluation, node count and PV, must they traverse the same search episode, or can distinct writer/reader changes realize the same report?

**Observed answer:** no, source-level macro-search trajectories need not agree. The statement applies to the tested finite source worlds, not all chess engines.

## 2. Treatment ontology and empirical contacts

- **F/O/Z:** legal native first-move root-order intervention, original and no-contact sentinel, whose original P4 six-field UCI cores and 72 native searches are source-frozen.
- **W1/W2/Wn:** inhibit the first 1/2/n matching *accepted source save attempts* at a specific current key64/physical slot/next accepted payload-write ordinal. Source suppression affects the whole `TTEntry::save()`, potentially including `move16`.
- **P:** inhibit accepted key/depth/bound/value/eval payload but leave source `move16` update possible. Hybrid TT entries are an artificial intervention.
- **R:** inhibit the exact full-key-shadow-matched TT early cutoff branch, but not other TT uses.
- **M:** inhibit the physical writer-matched `ttMove` hint before move ordering and associated move-based pruning/heuristics. This is broader than a single `MovePicker` action.
- **E:** recompute position evaluation rather than use a matching cached `tte->eval()`.
- **V:** inhibit bound-conditioned use of TT score as a *better static positional evaluation*, not the TT early cutoff. It leaves TT storage untouched.
- **S2:** suppress first matching writer, permit the *second original source* `TTEntry::save()` to proceed without synthetic TT payload injection. S3 is a not-fired rescue negative control.
- **WV:** nested writer W2 plus bound-conditioned TT evaluation V; do not interpret until its native run is verified.

## 3. Three source-native falsifiers

**(A) A write budget is not a monotone preference knob.** In case #6, W0/W1 returns F's `e4d6`, W2 through W21 return `c3a4`, and W22/W23 return `e4d6` again. This directly falsifies monotone nondecreasing restoration of the O bestmove *for this exact source operator*.

**(B) Numeric contact count is not physical event identity.** W/P writer-proposal fingerprint matches only the first write in #6 across budgets 2/21/22/23. At the second attempted write the caller's proposed key/move/depth/bound/value and old TT score/depth/bound are still equal, but `prior_move` is **0 under W and 3164 under P**. Hence the very next matching physical TT slot has different source state; equality of event ordinals cannot identify a common natural event. Case #8 W/P at budget2 matches both source fingerprints and the final complete UCI core; at budget74 they match only the first four fingerprints.

**(C) Exact output equivalence is weaker than source search episode equivalence.** In case #2, V blocks one bound-value evaluation override and W2 blocks two writer saves. The final UCI tuple agrees exactly, and all **846** recorded root event records agree; both report 7,032 main/qsearch TT cutoff branches. In case #5, the same final UCI tuple agrees exactly, but the root event streams agree for only the first **137** events; event #138 under a matched candidate and `alpha=-433, beta=-391` has `child_return=-653` under W2 and `-1026` under V. This is a directly recorded source-level mechanism-equivalence counterexample.

## 4. Independent-source and search-horizon challenge

Across the **ten other original game histories in the frozen twelve-world selection** (not a new sampling population), W1 changes bestmove in 2/10, W2 in 3/10, and R in 0/10. Nulls and nonfiring cases remain in the denominator; controls preserve prior O/F/Z UCI cores.

In five targeted frozen worlds at depths 8/10/12, W1 changes bestmove in 4/15 world-depth cells, W2 in 9/15 and R in 0/15. For #6, O and F **swap their preferred chess move direction** between depth10 and depth12 even as W2 returns O's preferred move at each tested depth. This rules out treating a fixed move-label restoration as an engine-depth-invariant concept.

## 5. Competing source consumers — what survived

At selected #1/#2/#5/#6/#8 depth12 worlds, W2 changes bestmove in 5/5. Selective R and M each change bestmove in **0/5**; M actually contacts the targeted physical move hint in #5 and #6 (3 times each), so a zero in the other three is not an informative negative for that route. E contacts the targeted cached-eval route and changes bestmove in **0/5**.

**V changes the root move in #2 and #5 (2/5)** and reproduces W2's entire final UCI core with **one actual full-key-shadow-matched reader consumption** in each. For #2 the V reader occurs at root call 6, root candidate native 2073, ply2, depth2, `alpha=196, beta=197, ttValue=-1435`. For #5 V reader occurs at root call 7, root candidate native 3437, ply1, depth3, `alpha=426, beta=427, ttValue=1026`.

These facts elevate *bound-conditioned TT score-as-evaluation reuse* to a witnessed, source-specific **competing mediator candidate**. They do not establish that it is the sole natural carrier of the writer perturbation. The nested WV interaction, stronger field-specific restoration, non-selected histories and other TT uses must still be attacked.

## 6. Required authority ladder

1. Original native source SHA, member ZIP SHA, source write-contact marker, exact sham and cold repeats.
2. Same physical slot/key writer epoch and an actually exercised, typed consumer branch.
3. Within-arm root call/trial/candidate matching **before divergence**; after a first mismatch, equal numeric call IDs do not force cross-arm event correspondence.
4. Cross-intervention output reproduction, distinguishing final-only equality from entire recorded episode equality.
5. Selective rescue and explicit competing-mediator exclusion before claiming natural mediation. **Currently HOLD.**
6. Independent population, additional engine and true original move-history transport before declaring any invariant chess explanation. **Currently HOLD.**

## 7. Reproducible court receipts

- [Full four-court fingerprint / root genealogy / ten-history / selective source-write restoration](../receipts/c3x-018-four-native-courts-matched-proposals-root-genealogy-heldout-rescue-20261010.json)
- [Five source worlds, three search horizons](../receipts/c3x-018-five-source-worlds-three-depth-TT-operator-transport-20261010.json)
- [TT move-hint vs early cutoff reader comparison](../receipts/c3x-018-TT-move-hint-vs-early-cutoff-native-five-root-20261010.json)
- [TT cached eval vs bound-conditioned evaluation score override](../receipts/c3x-018-TT-eval-cache-vs-bound-override-V-reproduces-W2-cases2-5-20261010.json)
- [V vs W2 whole-root-event comparison](../receipts/c3x-018-W2-V-final-equivalence-but-distinct-root-genealogy-20261010.json)

**Do not manuscript-freeze.** These are source-specific finite-depth mechanism interventions, not demonstration that Stockfish learned tactical concepts, nor proof of a unique natural TT mediator.
