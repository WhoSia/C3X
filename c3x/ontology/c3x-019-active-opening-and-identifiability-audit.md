# C3X 0.19 — Endogenous Search-Memory Rewriting & Counterfactual Lineage Preservation: Versioned Transposition-Table Writers, Selective Consumer Restoration, Search-Window Path Dependence & Independent-Ecology Falsification

**State: ACTIVE, adopted 2026-10-10.** C3X 0.18 is CLOSED for phase administration, with independently failed and unresolved scientific claims **carried forward as unresolved**, not transformed into PASS. [0.19 formal name proposal](c3x-019-formal-name-proposal-endogenous-search-memory-rewriting-and-lineage-preservation.md) is the accepted formal name. Frozen engine: Stockfish 16 commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`.

## Primitive question

When an intervention on an earlier search consumer changes later memory writes, what *physical search-memory state* suffices to preserve and identify a later real engine consumption event, and which consequences of this phenomenon survive on independently frozen inputs and another search engine?

## Immediate P0.19 priority: attack an identification trap before adding discoveries

The C3X 0.18 physical consumer suppression operator checks a sidecar `(full64 key, slot, epoch)` and root/search-guard criteria, while the native TTEntry is a 10-byte record whose numerical bound/depth/value/eval can change. Reinstating **both** native bytes and a sidecar tag causes the V-gate to match its original target again. That does not itself identify whether restored **native bytes**, **writer identity tags**, or **search-path changes** made the second *would-have-been-consumed* event reappear. Even more importantly, a `reader_block` event proves the V gate *suppressed* use at the branch, **not that the engine subsequently used the value**. The prior publication terminology must therefore remain `restored eligible/source-matched V contact`, not "restored natural TT use" unless measured independently without V.

A separate, genuinely falsifiable factorial must disentangle physical payload and sidecar identity:

| Native TT 10B bytes | Shadow full64 writer ticket | Label | Purpose |
|---|---|---|---|
| new version | new version | NONE | natural modified F/V search baseline |
| old version | old version | FULL | previous synthetic repair replay |
| old version | new version | BYTES_ONLY | semantic payload restoration without satisfying original epoch-targeted V gate |
| new version | old version | SHADOW_ONLY | *dangerous tag-only positive-control*: original V gate can recontact without native byte restoration |
| no accepted writer write | original old version | SKIP | previous source-suppression baseline |

**Hard falsification criterion:** If SHADOW_ONLY produces a `reader_block` while raw last-writer bytes disagree, the existing "consumer restoration" is at least partly a consequence of the observer/actuator's epoch-addressing rule. It is scientifically invalid to infer a naturally restored memory-use path solely from such a contact. BYTES_ONLY may preserve native evaluation while failing original physical epoch matching. Report that divergence as a real result, not as a test failure to be hidden.

**Measurement independence:** Run an unblocked **passive** evaluation-consumer recorder to assess whether native engine use resumes; do not infer native use from suppressed `V` branch. Detect physical/raw payload mismatch **at each site**, not by assuming reader and writer epoch fields are equivalent.

## 0.19 provisional research lanes

1. **A — Physical payload-versus-tag identifiability:** Factorial FULL/BYTES_ONLY/SHADOW_ONLY/SKIP, paired real consumer and passive use audits. Technical gate: no search behavior drift in all unmodified cold UCI cores.
2. **B — Causal writer proposal locality:** Prove the ordering of first reader, qualifying `TTEntry::save` decision, selected root trace and next probe. Separate pure move16 refresh from 10-byte write, and distinguish score, depth and bound.
3. **C — Minimal source-state sufficiency:** Find a predictive quotient involving value, bound, depth, TT keys, resident epoch, root context and search window, with explicit counterexamples and non-identifiability certificates.
4. **D — Blind independent-cohort and cross-engine audit:** Freeze never-used February 2026 Lichess PGN by engine-free protocol *after* risk predictions, and inspect a second engine only after mapping its actual TT cache semantics.

## Scientific stop/continue logic

**Continue** source-exact TT debugging and falsification. **Stop claiming** (until independently supported) unique natural mediation, direct chess positional concepts, general cross-engine law, or an explanation of an entire root bestmove flip from a single repaired TT event. In the existing January independent sample J2/J3/J4 remain **FAIL**. The earlier P1 unbounded R5 **FAIL** remains a permanent historical result even though its refined time-qualified gate later passed.

This phase is valuable only if it narrows conditions under which a physical writer/consumer effect can be identified, including conditions where it cannot. Treat new post-outcome P0.19 factorials as **ADAPTIVE**, not independent confirmation.

## Phase references

[C3X 0.18 final P0/P1 source receipt](../receipts/c3x-018-P0P1-exact-save-predicate-and-temporally-scoped-writer-rescue-20261010.json) · [July–January failure/attrition source](../receipts/c3x-018-january31-pair-physical-TT-epoch-rewrite-mechanism-20261010.json) · [0.19 proposal](c3x-019-formal-name-proposal-endogenous-search-memory-rewriting-and-lineage-preservation.md).
