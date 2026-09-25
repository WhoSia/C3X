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
- `claim-lattice.json` — which claims depend on which prior authorities, plus explicit non-implications;
- in schema v2, `product-field-contract.json` — the architecture × budget × mapped-state × intervention object and its index-removability tests.

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

## Why Rust here — and why that is not a repository default

The generator is a small deterministic compiler with a narrow side-effect surface. Rust is useful **for this component** because invalid states can progressively be moved from runtime conventions into typed structures and validation rules. That choice does not create a Rust-first rule, just as the repository's existing Python harnesses do not create a Python-first rule.

C3X follows a **capability-first, language-nonauthoritative** policy. Python is often convenient where `python-chess` or rapid experiment composition is materially useful; JavaScript/TypeScript can provide an independent verifier or tooling surface; C/C++ is preferable when engine-native semantics or low-level numerical behavior is itself part of the contract; R, Julia, Kotlin, Java, Ada, Go and other languages are admissible when they provide a real correctness, verification, interoperability or maintenance advantage. No language is added for diversity theatre, and no language is retained merely for uniformity.

## Generator / theory co-evolution

LawGen is not downstream documentation. A generator schema change is potentially a scientific event.

Examples:

- P25 forced `search_budget` to become a first-class axis because the fine atlas was not stable across node budgets.
- P26 promoted the schema to v2 with explicit `state_correspondence`, `product_space`, `prediction_authority`, `adjudication_support`, and descriptor-manipulability classes. It also demonstrated why architecture and budget must be represented as separate tested indices rather than folded into one state label.
- A future held-out-engine test requires prediction authority distinct from retrospective descriptor separation.
- A source-level descriptor intervention requires the ontology to distinguish *observed architecture descriptors* from *manipulable mechanism coordinates*.

The repository should therefore review ontology-schema changes with the same care as adjudication changes.

## P25 incident: canonicalization is part of scientific infrastructure

The first P25 run exposed a receipt bug before selective execution. The in-memory `atlas_receipts` object used integer budget keys. Python's sorted JSON serialization ordered those numerically while the written JSON converted them to strings; a fresh parse then sorted them lexicographically, producing a different hash.

The important scientific fact is not that JSON is awkward. It is that a precommit must survive serialization and independent reload. P25 therefore repaired hashing by normalizing through JSON before hashing and resumed from the exact outcome-blind prefix. No selective engine call had occurred before the failure.

This incident motivates a permanent rule:

> **A generated scientific receipt is not sealed until its identity survives a fresh-process round trip.**

## P26: schema v2 and product-space authority

P26 compiled a frozen field contract for `L(a,b,z_b,i)→r`, where `a` is architecture, `b` is search budget, `z_b` is a budget-indexed state mapped through a deliberately low-capacity correspondence, and `i` is the intervention. The corresponding scientific result retained both architecture and budget as necessary empirical indices under the tested correspondence.

Schema v2 therefore treats cross-budget state correspondence as an explicit authority object rather than an implementation detail. It also separates observed descriptors from descriptors that may become manipulable intervention coordinates. A descriptor classified as feasible is **not** thereby causally identified; a future experiment must still construct a source-level intervention that preserves the intended semantics and passes its own preflight.

P26 also adds a second infrastructure rule: a post-adjudication verifier may be repaired only if it reuses the identical sealed precommit and already materialized selective artifacts and does not alter any scientific computation. The P26 JS path bug was handled exactly this way.

## Near-term roadmap

1. Promote source provenance into the generated constitution rather than leaving it only in the input specification.
2. Replace ad-hoc JSON `Value` fields with versioned Rust types for atlas, intervention and descriptor objects.
3. Add JSON Schema export so external tools can validate LawGen specs without executing Rust.
4. Add a dry-run DAG renderer for experiment review.
5. Add `diff-constitution` to distinguish scientific changes from formatting changes.
6. Extend v2 prediction-authority objects before any held-out architecture outcome is opened.
7. Keep generated files reproducible: the same spec and LawGen version must yield byte-identical generated artifacts.

## Non-goals

LawGen is not intended to become a generic workflow engine, a chess GUI, an engine tournament manager, or an automated paper-writing system. Its scope is narrower: **compile C3X's scientific ontology into inspectable, reproducible experimental authority.**
