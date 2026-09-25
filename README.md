# C3X — Counterfactual Contrastive Chess eXplanation

> **Causal reverse engineering of chess-engine search.** C3X turns source-level interventions in strong chess engines into falsifiable, exact-world mechanism claims.

C3X is a research programme for moving from *"the engine chose this move"* to *"this search mechanism made a causally testable difference under a controlled counterfactual."* Chess is the laboratory; the longer-horizon target is a general methodology for reverse engineering complex decision systems.

```text
instrumentable engine
      ↓
outcome-blind state measurement
      ↓
source-level mechanism intervention
      ↓
exact-world counterfactual adjudication
      ↓
cross-version / cross-architecture transport
      ↓
evidence-carrying explanation
```

C3X does **not** equate engine strength, Stockfish agreement, search depth, probe accuracy, saliency, or fluent chess language with mechanistic understanding.

## Current scientific frontier

**G9.4** studies whether persistent search-memory mechanisms transport across engine architectures.

- **P20–P22:** constituted and stress-tested cross-engine relation laws over Stockfish 19, Berserk and Ethereal, with Inanis as a topology-specific negative-control architecture.
- **P23:** showed that a scalar pre-intervention qsearch-state quotient is response-relevant but does not recover a universal cross-architecture causal law. The current authority is *architecture-indexed and search-state-modulated*.
- **P24 (active):** prospectively builds a multivariate, outcome-blind search-state atlas and tests nested quotient refinement, intervention-response bisimulation, and the point at which a universal law must give way to an architecture-indexed law family.

Scientific meaning and claim authority live in the Research OS / Notion lineage. This repository is the executable byte authority for the code that realizes those tests.

## Repository architecture

```text
C3X/
├── c3x/
│   ├── protocol/       # prospective constitutions / presealed courts
│   └── receipts/       # promoted machine-readable closures
├── compiler/
│   └── exact_world/    # exact chess-world constitution
├── crates/
│   └── c3x-atlas/      # Rust scientific kernels (P24+)
├── harness/            # engine orchestration + adjudication
├── matcher/            # deterministic prospective matching
├── analysis/           # independent numerical certificates
├── patches/            # engine-specific source interventions
├── upstream/           # exact upstream locks / provenance
├── tools/              # independent verifiers and report tooling
├── docs/               # theory genealogy and engineering notes
└── .github/workflows/  # reproducible build / experiment courts
```

### Why a polyglot stack?

The languages are separated by epistemic role rather than taste alone.

| Layer | Default | Why |
|---|---|---|
| Scientific kernels, deterministic partitioning, certificates | **Rust** | strong invariants, reproducible binaries, good audit surface |
| Chess semantics, exact-world generation, orchestration | **Python / python-chess** | expressive domain model and rapid scientific composition |
| Independent receipt/schema verification, reporting | **JavaScript / ESM** | lightweight second implementation and excellent tooling surface |
| Engine-adjacent or independent numerical checks | **C++** | native fit with chess-engine ecosystems and useful implementation diversity |
| JVM services/UI | **Kotlin when justified** | intentionally not placed on the scientific critical path without a real JVM-native role |

No result becomes stronger because more languages were used. Independent implementations matter only when they test a real failure mode.

## P24: outcome-blind atlas

P24 deliberately avoids an outcome-trained representation map. Within each material-family × side-to-move stratum, named SHAM telemetry is transformed to empirical-copula ranks separately for each engine. The three engines are then aligned into an engine-symmetric shared coordinate system using coordinate-wise medians plus explicit cross-architecture disagreement coordinates.

A frozen balanced refinement tree creates nested state quotients `K=1 → 2 → 4 → 8`. Only after this atlas is sealed are the source-level memory interventions executed. The court then asks whether greater state resolution actually earns cross-architecture causal transport or merely reveals a finer architecture dependence.

See [`docs/P24_THEORY.md`](docs/P24_THEORY.md) and [`c3x/protocol/p24-preseal.json`](c3x/protocol/p24-preseal.json).

## Reproducibility model

C3X uses an explicit authority split:

- **Research OS / Notion** — scientific interpretation, claim authority, Courts, negative results and theory genealogy.
- **Google Drive C3X data room** — persistent large/private bytes and sealed result capsules.
- **GitHub** — source, patches, manifests, tests, workflows and promoted machine-readable receipts.
- **GitHub Actions artifacts** — transient execution evidence.
- **Local runtime** — working surface only; never sole custody.

A green workflow is evidence that a declared computation ran. It is **not by itself a scientific conclusion**.

## Design rules

1. **Prospective before selective.** State definitions, thresholds, interventions and adjudication rules are frozen before the corresponding outcomes are opened.
2. **Fresh worlds when reuse threatens identification.** Failed support is recorded as failure; gates are not relaxed after seeing results.
3. **Exact-world adjudication over engine self-agreement.** The engine under study does not define its own truth criterion.
4. **Negative controls are constitutive.** A mechanism claim must survive channels that should not matter.
5. **Transport is earned.** Version, engine family and architecture are possible causal indices, not nuisances to average away automatically.
6. **Negative results are first-class artifacts.** A failed transport law narrows the ontology and remains in the lineage.
7. **No post-hoc representation rescue.** A sufficiently expressive alignment can make almost anything look equivalent; alignment capacity is part of the scientific hypothesis.

See [`GOVERNANCE.md`](GOVERNANCE.md) for repository-level rules.

## Long-horizon ambition

```text
instrumentable chess engine
→ causal mechanism atlas
→ evidence-carrying move explanations
→ general black-box reverse engineering
→ corrigible chess world model / successor AI
```

The point is not to make an engine narrate itself. The point is to make an explanation **survive interventions, counterfactual worlds, rival architectures and attempts to falsify it**.

## License boundary

Stockfish-derived patches and distributed patched binaries remain subject to the applicable GPLv3 obligations. C3X keeps exact upstream and corresponding-source provenance as a release requirement. Repository-native C3X components may have their own license metadata; upstream obligations take precedence where derivative code is involved.
