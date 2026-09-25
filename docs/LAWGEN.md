# C3X Law Generator

`c3x-lawgen` is the executable projection layer between C3X theory and C3X experiments.

It exists because a research programme with many prospective freezes can fail in two opposite ways:

1. the prose theory becomes richer than the executable experiment, so important distinctions disappear in code; or
2. the implementation silently acquires degrees of freedom that were never granted by the theory.

LawGen makes that boundary explicit.

## Contract

Input: a frozen ontology specification under `c3x/ontology/`.

Output:

- `constitution.json` — typed scientific objects and immutable authority choices;
- `execution-matrix.tsv` — the prospective order of world constitution, measurement, precommit, selective intervention and adjudication;
- `claim-lattice.json` — which claims depend on which prior authorities, plus explicit non-implications.

The current Rust crate is `crates/c3x-lawgen`.

## What belongs in the ontology

A LawGen specification may declare:

- parent scientific authority;
- exact-world population and freshness boundary;
- engine identities and source locks;
- architecture descriptors frozen before selective outcomes;
- search-budget axes;
- outcome-blind state coordinates and quotient levels;
- intervention algebras;
- response fingerprints;
- prospective claim criteria;
- claim ceilings and forbidden inferences.

It should **not** contain observed selective results.

## Authority model

LawGen is intentionally weaker than a theorem prover and stronger than a workflow template.

It can reject malformed constitutions, duplicated engine identities, missing descriptors, non-monotone budget axes, or an experiment that attempts to execute selective stages before a precommit. It cannot establish that an ontology is scientifically adequate merely because it is well typed.

The authority chain is:

```text
research question
    ↓
prospective ontology
    ↓
LawGen validation + compilation
    ↓
outcome-blind materialization
    ↓
sealed precommit
    ↓
selective intervention
    ↓
independent adjudication
    ↓
claim update
```

A green LawGen build means **the declared experiment is internally executable**, not **the scientific claim is true**.

## Why Rust

The generator is a small deterministic compiler with a narrow side-effect surface. Rust is useful here because invalid states can progressively be moved from runtime conventions into typed structures and validation rules. The goal is not to rewrite Python orchestration in Rust.

Python remains the right layer for `python-chess`, exact-world semantics, engine orchestration and rapid scientific adjudication. JavaScript/TypeScript remains useful as an independent verifier and report/tooling layer. C++ should enter when an engine-native or independent numerical implementation gives a real additional failure mode. Kotlin should enter only if C3X gains a durable JVM-native inspection application.

## Generator / theory co-evolution

LawGen is not downstream documentation. A generator schema change is potentially a scientific event.

Examples:

- P25 forced `search_budget` to become a first-class axis because the fine atlas was not stable across node budgets.
- A future held-out-engine test may require `descriptor_prediction_authority`, distinguishing descriptors used for retrospective separation from descriptors allowed to make prospective predictions.
- A source-level descriptor intervention would require the ontology to distinguish *observed architecture descriptors* from *manipulable mechanism coordinates*.

The repository should therefore review ontology-schema changes with the same care as adjudication changes.

## P25 incident: canonicalization is part of scientific infrastructure

The first P25 run exposed a receipt bug before selective execution. The in-memory `atlas_receipts` object used integer budget keys. Python's sorted JSON serialization ordered those numerically while the written JSON converted them to strings; a fresh parse then sorted them lexicographically, producing a different hash.

The important scientific fact is not that JSON is awkward. It is that a precommit must survive serialization and independent reload. P25 therefore repaired hashing by normalizing through JSON before hashing and resumed from the exact outcome-blind prefix. No selective engine call had occurred before the failure.

This incident motivates a permanent rule:

> **A generated scientific receipt is not sealed until its identity survives a fresh-process round trip.**

## Near-term roadmap

1. Promote source provenance into the generated constitution rather than leaving it only in the input specification.
2. Replace ad-hoc JSON `Value` fields with versioned Rust types for atlas, intervention and descriptor objects.
3. Add JSON Schema export so external tools can validate LawGen specs without executing Rust.
4. Add a dry-run DAG renderer for experiment review.
5. Add `diff-constitution` to distinguish scientific changes from formatting changes.
6. Add held-out descriptor prediction objects before any P26+ architecture-expansion outcome is opened.
7. Keep generated files reproducible: the same spec and LawGen version must yield byte-identical generated artifacts.

## Non-goals

LawGen is not intended to become a generic workflow engine, a chess GUI, an engine tournament manager, or an automated paper-writing system. Its scope is narrower: **compile C3X's scientific ontology into inspectable, reproducible experimental authority.**
