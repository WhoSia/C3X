# C3X 0.25-P4/P5 — Two-Axis Theory ↔ Implementation Contract

**Formal name retained:** C3X 0.25 — Mechanistic Search-Lineage & Falsifiable Engine Dynamics: Physical TT Read-to-Use Attribution, Exact-State SEE Activation, Frontier Bifurcation, Root-Candidate Survival, Intervention-Preserving Optimization & Source-Blind Prospective Generalization.

**Phase:** SOURCE-BASED MECHANISTIC THEORY + EXECUTABLE FINITE TESTS ONLY (2026-10-11); no unexposed chess outcomes, no new native TT improvement, no M5 model, NO causal natural TT→SEE mediation proof. Register scientific obligations here **BEFORE implementing/executing P4/P5**.

## Two irreducible research axes

**A — Microstructure theory:** the ontology of a search decision must distinguish (a) TT probe contact from (b) state mutation induced by a probe from (c) stored-move use and stored-score/bound use; separately SEE call/argument/guard execution, ancestor frame return, root competition, observable final UCI. Treat actual events as partial, ordered data, never infer unique causes from a shared chess board or coincident bestmove. The counterfactual comparison must know what information is *not observed*.

**B — Implementation science:** produce a narrowly source-derived, executable reference model for exactly **upstream SF16 at Git commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`** and a fail-closed checker for eventual event-chain certificates. The reference is NOT a compiled/native SF engine and its parity with all C++ code paths has not been established. Prove individual bounded semantics with executable finite tests and explicit witness JSON. Record original upstream SHA, no modified GPL engine code redistribution, no public original chess records.

## P4 theoretical object: field-sensitive physical TT microsemantics

An abstract TT cluster is three entry records `(key16,depth8,genBound8,move16,value16,eval16)`, generation `G∈Z/256`. A probe of key `k` linearly inspects the three slots and returns the first with `key16 = k mod 2^16` **or** `depth8=0`. On such a return it updates `genBound8 := G | (genBound8 & 7)`, and returns `found := bool(depth8)`. When no slot qualifies, it returns the slot minimizing `depth8 - ((263 + G - genBound8) & 248)`, tie broken by the first scanned slot, without generation refresh. `new_search` adds 8 modulo 256. `TTEntry.save` updates `move16` if new move !=0 or low16 key changed, *even when the stored numeric value is NOT overwritten*. The score/depth/gen+bound/score update requires exact bound, low16 key changed, or `newDepth - DEPTH_OFFSET + 2*pv > oldDepth8 - 4`; `DEPTH_OFFSET=-7`. Model only this isolated single-threaded cluster transaction; SF16 C++ TTEntry writes can be racy under multiple threads and this model has no NNUE, alpha-beta, SEE, bestmove or strength estimate.

### Four conjectures frozen for finite verification

**P4-I (probe-observation non-inertness).** There exist reachable abstract TT states `s` and a query `k` for which the caller does not consume the returned TT value but `probe(s,k)` nevertheless changes the future replacement target of a subsequent *different-key miss* compared with a **non-refreshing counterfactual lookup**. If observed, the proper conclusion is TT *resource-history* coupling, not proof that July2025 TT FIRST changed root through generation.

**P4-II (mixed-field provenance).** A same-key, non-EXACT, insufficient-new-depth `save` can update `move16` without updating `value16`, `eval16`, `depth8` or `genBound8`. A single "last writer" event attached to the entire native TT entry therefore need not identify the writer of every field. An instrumented TT auditor should track at least `move_writer` and `score_writer` separately. The P4 Python reference models values but does not identify real native writer epochs.

**P4-III (16-bit key alias ambiguity).** Distinct 64-bit keys `k≠k'` with the same low16 bits, **if they map to the same cluster**, can match the same TTEntry as `found=True` in the native compact probe. Thus same low16 probe hit is insufficient for a certified full64 physical writer-reader lineage; actual C3X shadow writer certificate remains necessary.

**P4-IV (bounded model versus true engine).** Finite tests may establish consistency of our isolated reference transitions and supplied code anchors, **not** native full-engine observational equivalence, TT policy superiority, Elo gain, or natural TT→SEE mediation. A future native cross-language oracle would need exact source key+slot, generation, depth, score/move, race-free single-thread transactions and cold UCI parity.

## P5 theoretical object: proof-carrying search-event certificates

An event chain has a per-arm monotone native serial and one-to-one parent event pointer. Its kind is from `TT_PHYSICAL_READ, TT_SEMANTIC_USE, SEE_CALL, BRANCH_DECISION, CHILD_RETURN, ROOT_CANDIDATE, FINAL_UCI`. A source observer's complete comparison state includes **root iteration + retry + source root candidate, exact ancestor vector, native position, native move, ply, depth, alpha/beta, PV/cut node, rule50, SEE threshold/occupied and native operator site**. The checker is a schema-level *necessary-condition verifier*: it rejects missing parent, non-monotone serials, same-position/different-window aliases, missing actual TT semantic-use, missing branch/return, missing terminal source candidate, and trace-censored false negatives. Identical source chess key/path with unequal native search state must **not** be called the same computational event. If all observed links are valid, status is `TRACE_CHAIN_COMPLETE_NONCAUSAL`, **not** `NATURAL_MEDIATION_PROVEN`. An intervention-controlled proof of mediator-specific path and independent prospectively predictive UCI is a different causal experiment.

### Explicit falsification cases (locked before code)
1. Probe refresh changes which of three old age-stamped entries gets replaced after one new miss despite caller ignoring the first result.
2. Same compact key but distinct full64 keys is a false physical identity assertion.
3. Same-key shallow save changes move but not numeric entry values; a single unified writer is insufficient.
4. Broken serial ordering, absent native TT score use, missing branch/return, missing UCI terminal, duplicate or censored node all **fail closed**.
5. Same FEN and ancestor path but different alpha/beta or PV context **cannot** get `FULL_STATE_EQUAL`.
6. A perfectly complete synthetic event chain only receives `TRACE_CHAIN_COMPLETE_NONCAUSAL` with natural mediation set false.
7. Any future M5 treatment outcome built from July2025/Sept2025 exposed role cells **cannot** be labeled independent. P4/P5 run *no* future model forecasts.

## Prior cumulative evidence and future gate

P3 September2025 M3v2 **NEGATIVE** (448/501 versus M0 449/501). P4 July2025 M4 **NEGATIVE** (915/1012 versus M0 916/1012), 96 physically changed root bestmoves over 48 games and 12 prior HOLD; game-event bootstrap CI includes zero. C3X0.25 P0-D0 and P1 coflip source evidence, P2 partial native TT-after-use SEE chronology and P3 SF16 TT source audit CI are **developmental**. Archive hashes and failures unchanged. The new P4/P5 tests are a constructive theory/implementation bridge, NOT post-hoc validation of M4 or measured TT improvement. Next P6 will require native single-thread source-and-trace alignment before claiming applied relevance. Any future preFIRST M5 model must use distinct, truly fresh source game SHA+FEN4 and human Git literal UCI registry, followed by separate physical TT FIRST and game/event-cluster court.

**Governance:** human `WhoSia` Git author/committer; Actions `contents: read`; SF16 upstream code cited under GPLv3, Lichess July2025 CC BY-SA4 without complete original PGN/players; failure remains a first-class result.
