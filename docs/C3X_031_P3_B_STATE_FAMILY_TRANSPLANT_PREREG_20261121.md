# C3X 0.31/P3-B — Prospective within-source State-Mediator Rescue Preregistration (NO NATIVE B RUNS YET)

**Preregistered 2026-11-21 after P3-A0 exposed retrospective source-trace diagnosis.** This plan is a *new physical instrumentation and intervention* design, not a report of performed rescues or a claim that TT/history causes the final root preference.

## Physical explanandum and frozen source prefix

Frozen original development game: **P2-028-0**, legal full history in [P2 original privately frozen game ZIP](https://drive.google.com/file/d/1Aj02UgRoHYw6sKqPjwOmtDETfTnESpe8/view). Earlier R26 already selected the **FIDE World Open U20 Rapid** macro family while this game belongs to **FIDE World Open U20 Blitz**, so P3-B is **development of a mechanism in a historically exposed source family**. Any true new-family replication must use a different, pre-frozen tournament/macro family and only after the mechanism is fixed.

Native engine must be the original **Stockfish16 `sf_16` source** at commit `68e1e9b3811e16cad014b590d7443b9063b3eb52` plus the exact audited R27/R29/R30/R31/R33 patches. Prior R33-patched binary hash `ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1`, prior R31 reference binary hash `78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb`, NNUE SHA256 `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`. One engine thread, fixed 16 MiB TT, fresh exact full UCI history, original source options.

Natural target is physical source **`C3X_R33_OPEN event=19`**, root `d4e5`, attempt16/iteration13, excluded `e5f6`, tested `g7b7`, source key `18244396700095567446`, ply5/depth1, incoming alpha−2634, beta−2633, original return −2429. Treatment skipping futility/null at the *same exact open event* returned −2500 and examined 2 legal replies. The physically reachable **synchronization boundary** is **after complete root iteration13/attempt16 END and before root iteration14/attempt17 START**, not a hypothetical arbitrary board-state splice in the middle of a search stack.

P3-A0 found that attempt16's root candidate values, leader updates, and move order were identical despite +18 treated nodes. At attempt17/iteration14 same-move `f4e5` return first differs (2265→2280) with no leader change. At attempt18/iteration15 the `f4e5` update first differs (2238/update0→2256/update1), and attempt19's initial alpha-beta windows diverge. This is the **total-effect observation to mediate**, not already-proven mediator identity.

## P3-B0 — Passive state source mapping and noninterference first

Before changing any source TT/Heuristic fields, compile an **observer-only** binary that logs (bounded and lossless within the primary checkpoint):
- The native TT **physical slot identity**, full query Key and *16-bit stored fingerprint*, full writer-key sidecar when available, generation/age, value, depth, bound, move, evaluation and writer identity for all writes induced between the targeted physical source event and iteration14 `f4e5` returns; report overwrite vs move-only preservation.
- Every **actual reader** at a logged query; classify exact full-key match vs 16-bit collision/reuse and whether a read affects candidate ordering, a TT cutoff, a fail-low return, the adjusted history path or future write.
- Main-history, continuation-history, killer/countermove and root ordering structures only where they actually differ by the exact END16 checkpoint; distinguish read-before-write from read-after-write and log first divergence.
- Real cumulative nodes at each checkpoint and actual root candidate attempt/iteration/alpha/beta; bound outputs must preserve `LOWER/UPPER/EXACT` and legal move/provenance identities.

**Reuse existing original C3X source:** [0.14 physical TT slot lineage patch](../tools/c3x_014_native_TT_slot_lineage_patch.py), [0.15 CSWP writer/reader/window patch](../tools/c3x_015_CSWP_TT_writer_reader_bound_window_patch.py), [0.30 P11-S4D noninterference proof](C3X_030_P11_S4D_NATIVE_SOURCE_PARTIAL_ANCESTRY_NONINTERFERENCE_20261111.md), and the real [R33 early gate patch](../patches/stockfish16/R33-prospective-gates.patch). These are **donor methods**, not automatically compatible drop-in code: their source anchors were for earlier patch stacks; preserve current production source semantics. **Do not count a 16-bit fingerprint as a unique TT writer identity.**

**Passive logger gate:** original R31 reference vs R33 observer-disabled vs observer-only new binary match *complete normalized public UCI, root producer, bestmove, exact completed depth, candidate order, and actual node counts* for both P2-028 arms and depth15/16. If a supposedly read-only full-key sidecar or stdout tracer changes work, **HOLD_PASSIVE_NONINTERFERENCE**, not a causal result. No result may be called contact proof if source event19 is missed/reordered or the source search truncates logger output. Original source binary remains separately preserved.

## P3-B1/B2/B3 — Source-state family interventions

Freeze the actual naturally reached END16 checkpoints in both the unmodified `A` (futility return) and `B` (same event bypass). Define a **paired state family** as only the physically touched, identified objects whose full original scope and access identity can be proven:

- **TT family `T`:** individual exact table slots and their byte-exact fields, including generation and full-key writer attribution, not naive UCI move-hint/score alone. Compare post-END16 table snapshots from both native arms; candidate lists predeclared by *causally reachable writes* and independently confirmed later reads. A new passive run must confirm the entire queried table state, not merely selected truncated entries.
- **History/order family `H`:** main/continuation history, killer/countermove and root move-order producer values with actual diverging bytes and observed future reads. A "restored" history that was never read cannot explain a later root move.
- **Budget/iteration context `B`:** actual completed nodes, remaining nodes under a fixed stop rule, aspiration-window construction, and loop metadata. **Never falsify the node counter by setting it back** after different work and then claim a same-budget experiment. Instead define explicit matched-depth and separately matched-node experiments with true recorded work, and call any different work a treatment effect or confound according to the estimand.

The causal targets are two downstream **predeclared endpoints**, not a post hoc arbitrary bestmove:
1. `Y_1`: `f4e5` source value in iteration14/attempt17 at its source-executed common alpha2289; source baseline 2265 vs treatment 2280, both update0.
2. `Y_2`: `f4e5` leader update in iteration15/attempt18; baseline 2238/update0, treatment 2256/update1, both initial root windows [1973,2677]. The final `d4e5→f4e5` bestmove is a secondary final-choice endpoint.

**Physical arms at the frozen boundary (all cold repeated and accompanied by sham):**
- `A`: original untreated source; `B`: exactly event19 `both_off`; `A_SHAM`, `B_SHAM`: identical copy/restore of same-arm checkpoints.
- `B_TO_A_T` / `A_TO_B_T`: replace **TT family only** with the physically observed reciprocal arm's table state at precisely the same synchronization boundary.
- `B_TO_A_H` / `A_TO_B_H`: replace **history/order family only** analogously.
- `B_TO_A_TH` / `A_TO_B_TH`: joint replacement to test interaction and failure of additivity.
- Control `NO_CONTACT`: irrelevant source event ID with identical source flags; `PLACEBO`: verified unqueried entries that must have no effect; negative artifact and mismatched-snapshot rejection cases.

**Do not manipulate source-state families that fail the reader or same-origin checkpoint identity check**. The treated checkpoint has already performed more work; TT/H replacement does not erase that effect. Report work difference and short-circuit effects explicitly. A single successful `B_TO_A_T` rescue at one depth is at most *a conditional necessary-intervention witness for T under this checkpoint policy*, **not universal uniqueness** or proof that every TT write is necessary. A sufficient mediator claim needs reverse transfer, repeated source parity, robust contact and independent source histories; mixed T+H rescue does not alone distinguish T from H.

## Reproducibility and predefined scientific verdicts

For both fixed depth15 and16, every source arm requires identical legal game history, source SHA, NNUE, original R33 target identity, root menu and completed depth. Each arm gets at least two fresh-native cold repeats; sham outcomes must equal their own parent arm on the **complete root candidate ledger and source node accounting**. All artifacts get original stderr, stdout, source patch, source/binary SHA, full resolved intervened object identity lists and an outcome manifest; large raw files in Drive, small schema and verified verdict in GitHub, meaningful scientific evaluation in Notion.

### Promotion and falsification gates

- `P3_B0_PASSIVE_SOURCE_NONINTERFERENCE`: observer-only and original native complete source agreement, no logger loss at the checkpoint.
- `P3_B1_TT_CONDITIONAL_RESCUE`: exact physically read TT object identity restored at matched checkpoint and `Y_1/Y_2` reset toward original in same source world, with valid sham and reverse transfer. Distinguish reset of `Y_1` alone from `Y_2` or final move.
- `P3_B2_HISTORY_CONDITIONAL_RESCUE`: same requirements for actually read history/order state.
- `P3_B3_INTERACTION`: joint restoration rescues while single-family restoration fails, with all source-bounded identity checks.
- `HOLD_CHECKPOINT_STATE_INCOMPATIBLE`: mismatched source reader/event, unreachable state transplant, source observer affects original, missing TT/history snapshot, or no source contact.
- `NEGATIVE_MEDIATOR_FAMILY`: physically valid specific T/H restore does **not** rescue predeclared `Y_1/Y_2` in fixed world. Negative is not absence of **other** state mediators.
- `HOLD_STRATEGY_AND_HUMAN`: irrespective of source mediation, objective chess merit and student learning require independent separate experiments.

**P3-B currently:** *preregistered and unexecuted*, no source compile, no new search, no original TT/history transplantation done. P3-A0's actual root chronology remains a verified observation, not an experiment on the mediating state.
