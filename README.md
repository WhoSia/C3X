# C3X — Counterfactual Contrastive Chess eXplanation

C3X is a research programme for turning strong chess-engine behavior into **falsifiable, mechanism-sensitive explanations** and, ultimately, a more general black-box reverse-engineering framework.

## Long-horizon ambition

```
instrumentable chess engine
→ causal mechanism atlas
→ evidence-carrying move explanations
→ general black-box reverse engineering
→ corrigible chess world model / successor AI
```

C3X does **not** equate strong moves, Stockfish agreement, search depth, or fluent chess language with "knowing chess."

## What this repository is

This repository is the **executable engineering surface** of C3X.

It is intended to hold:
- active source and patch deltas;
- exact upstream locks and deterministic manifests;
- small fixtures and schemas;
- regression / UCI harnesses;
- CI workflows;
- promoted release-candidate metadata.

It is **not** the canonical scientific notebook. Scientific lineage, claim authority, Courts, negative results, theory genealogy, and current research state live in the Research OS / Notion lineage.

## Authority split

- **Research OS / Notion** — scientific meaning and authority.
- **Google Drive C3X data room** — persistent large/private bytes, sealed results, historical capsules.
- **GitHub** — source / patch / build / CI / release-candidate byte authority.
- **GitHub Actions artifacts** — transient build or execution receipts.
- **Local runtime** — working execution surface, never sole custody.

A green build or a commit is not a scientific result.

## Current repository phase

Repository constitution / bootstrap.

The next scientific engineering stage is **C3X 0.7.0-G9.4-P12**, which will materialize the first byte-exact Stockfish patch packet, dual-target port, UCI regression harness, and executable release-candidate path.

No P12 scientific result is claimed by this bootstrap commit.

## Core rules

See [GOVERNANCE.md](GOVERNANCE.md).

## License boundary

Stockfish-derived patches and distributed patched binaries are subject to the applicable GPLv3 obligations. C3X keeps exact upstream and corresponding-source provenance as a release requirement.
