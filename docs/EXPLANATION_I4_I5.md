# C3X Explanation Implementation I4–I5 — Causal Certificate Objects, Verified PV Evidence & Atomic Renderer

## Authority
Implementation track only. This release cannot strengthen, repair, or reinterpret Track A P18.

## I4 — Evidence authority becomes explicit
- C3X causal certificates are normalized into first-class graph objects.
- A causal certificate node points to the exact evidence atom it authorizes through `authorizes_causal_scope`.
- The normalized object preserves pair, bound, family, collapse target, replication state and authority ceiling.
- Position mismatch or missing certificate identity/pair/bound is rejected.
- Engine PVs are legally replayed before any line statement is surfaced.
- The current line adapter deliberately says only what was verified in the bounded PV. It does not infer a human strategic plan.
- Retrieval-corpus governance audits source URI, license state, tags and excerpt bounds.

## I5 — Surface prose becomes atomically auditable
Each rendered sentence is represented as:
`claim_id → text → atom_ids → provenance → authority → factuality result`.

The deterministic renderer:
1. refuses to surface atoms without bounded surface text;
2. preserves causal-vs-heuristic provenance;
3. rejects causal surface wording without causal provenance;
4. requires a first-class certificate object for `causal_contrast`;
5. records abstentions rather than filling semantic gaps;
6. emits a corpus-level atomic renderer benchmark.

The benchmark is **not** a human usefulness score. Strategic completeness and pedagogical quality remain separate future measurements.

## Why this matters for the ultimate chess commentator
The product can now combine:
- engine candidate comparison,
- verified tactics and board proxies,
- legally replayed candidate lines,
- licensed/retrieved commentary references,
- position-specific C3X causal certificates,

without flattening them into one undifferentiated prose claim.

That makes the intended next language model a **renderer over a typed evidence graph**, not a replacement for chess verification.

## Remaining frontier
- richer verified chess-native consequence adapters;
- explicit threat/plan semantics only with formal/verifiable witnesses;
- free-form NLG constrained by the bounded claim packet;
- adversarial factuality tests;
- human evaluation by rating band and learning benefit.
