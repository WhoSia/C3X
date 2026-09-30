# C3X Explanation Implementation I3 — License-Bearing Retrieval, Typed Evidence-Graph Merge, Multi-Axis Commentary Evaluation & Human-Utility Readiness

## Status

**CLOSED / PASS — IMPLEMENTATION AUTHORITY ONLY.**

Canonical implementation CI:
- workflow: `c3x-explanation-implementation`
- run: `36681118823`
- head: `134f0ccce1724f31aa98d5dfbe4f5abac2570327`
- conclusion: PASS

## What I3 adds

I3 turns retrieval and explanation-graph construction into explicit product contracts rather than letting a language model improvise from raw engine output.

### License/source-bearing retrieval

Every retrieval record must carry:
- `source_id`
- `source_uri`
- `license_state`
- retrieval tags
- a bounded excerpt no longer than 240 characters.

Records with missing provenance, inadmissible license state or oversized excerpts are rejected before graph merge.

The retrieval layer ranks sources only by declared tag overlap. Retrieval is reference evidence, never causal authority.

### Typed evidence subgraph

Each selected PGN moment now has a typed subgraph with:
- played-move root node;
- evidence-atom nodes;
- provenance-object nodes for source IDs and C3X certificate IDs;
- explicit support/provenance edges.

Graph structure does not upgrade the authority of any atom.

### Multi-axis evaluation packet

The output records evidence coverage separately for:
- structural;
- motif;
- tactic;
- position judgment;
- semantic;
- contrastiveness;
- provenance.

Human utility fields remain deliberately `null` until an actual human study adjudicates correctness, pedagogical clarity, trust calibration, baseline preference and subsequent move understanding.

### CLI

`c3x_explain.cli` now accepts a retrieval index and bounded top-k retrieval while preserving the same provenance firewall.

## Literature connection

I3 incorporates the 2026 ACT-Eval lesson that fluent chess commentary must be decomposed into atomic claims and checked against tools / expert-grounded evidence. This is an engineering donor only; it does not supply C3X scientific authority.

## Authority firewall

- Retrieved commentary is always `CONVENTIONAL_HEURISTIC_COMMENTARY`.
- Only a specific `C3X_CAUSAL_CONTRAST` certificate may authorize causal engine-preference wording.
- Typed graph edges, retrieval similarity and human-written source text cannot promote a Track-A causal claim.
- Track B CI has no authority over P18 science.

## Next

I4 should connect C3X causal certificates as first-class graph objects, add verified line-backed planning/threat adapters, govern retrieval corpora, and benchmark a bounded renderer using ACT-Eval-style atomic factuality before any free-form LLM prose is promoted.
