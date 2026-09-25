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

**G9.4** studies whether persistent search-memory mechanisms transport across engine architectures and search budgets.

- **P20–P22:** constituted and stress-tested cross-engine relation laws over Stockfish 19, Berserk and Ethereal, with Inanis as a topology-specific negative-control architecture.
- **P23:** showed that a scalar pre-intervention qsearch-state quotient is response-relevant but does not recover a universal cross-architecture causal law. The authority became *architecture-indexed and search-state-modulated*.
- **P24 (closed):** replaced the scalar cut with a prospectively frozen multivariate atlas at `K=1,2,4,8`. No level recovered universal strict transport or conditional naturality; at `K=8`, **0/8** states formed an architecture-free intervention-response bisimulation block. A nonconstant **architecture-indexed causal-law family** was constituted within the frozen P24 authority ceiling.
- **P25 (closed):** replicated architecture-index necessity on **384 fresh exact worlds**, measured the atlas at `40k/80k/160k/300k` SHAM node budgets, and introduced the typed **C3X Law Generator**. The fine `K=8` atlas proved materially budget-sensitive (`40k↔300k` agreement `0.331`, ARI `0.103`; `80k↔300k` agreement `0.440`, ARI `0.159`). Architecture-free `K=8` response states again remained **0/8**. A frozen source-descriptor court found minimal cardinality **2**, but every sufficient descriptor map still separated all three engines, so P25 earned **descriptor factorization without nontrivial law-family compression**.

Scientific meaning and claim authority live in the Research OS / Notion lineage. This repository is the executable byte authority for the code that realizes those tests.

## Repository architecture

```text
C3X/
├── c3x/
│   ├── ontology/       # typed theory inputs / architecture descriptors
│   ├── protocol/       # prospective constitutions / presealed courts
│   └── receipts/       # promoted machine-readable closures
├── compiler/
│   └── exact_world/    # exact chess-world constitution
├── crates/
│   ├── c3x-atlas/      # deterministic search-state atlas kernel
│   └── c3x-lawgen/     # typed theory → constitution / matrix / claim-lattice compiler
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
| Scientific kernels, typed constitutions, deterministic partitioning | **Rust** | strong invariants, reproducible binaries, good audit surface |
| Chess semantics, exact-world generation, orchestration | **Python / python-chess** | expressive domain model and rapid scientific composition |
| Independent receipt/schema verification, reporting | **JavaScript / ESM** | lightweight second implementation and excellent tooling surface |
| Engine-adjacent or independent numerical checks | **C++** | native fit with chess-engine ecosystems and useful implementation diversity |
| JVM services/UI | **Kotlin when justified** | intentionally not placed on the scientific critical path without a real JVM-native role |

No result becomes stronger because more languages were used. Independent implementations matter only when they test a real failure mode.

## C3X Law Generator: theory as an executable constitution

P25 adds `crates/c3x-lawgen`. It is deliberately **not** an automatic truth generator. It compiles a frozen ontology specification into three inspectable artifacts:

```text
c3x/ontology/*-lawgen-spec.json
              ↓
        c3x-lawgen (Rust)
        ↙       ↓        ↘
constitution  execution   claim
   .json      matrix.tsv  lattice.json
```

The generator gives theory an executable projection: engine identities, source descriptors, search-budget axes, state quotients, intervention algebras, claim dependencies and non-implications become typed objects that CI can reject before selective outcomes are opened. In the other direction, implementation failures expose hidden theoretical assumptions. P25's JSON-key canonicalization incident is kept in the scientific lineage precisely because executable constitutions are useful only when their own authority boundaries are auditable.

The intended feedback loop is:

```text
theory → typed ontology → generated constitution → prospective execution
   ↑                                              ↓
claim repair ← failure localization ← adjudication / counterexample
```

See [`docs/LAWGEN.md`](docs/LAWGEN.md), [`docs/P25_THEORY.md`](docs/P25_THEORY.md), [`c3x/ontology/p25-lawgen-spec.json`](c3x/ontology/p25-lawgen-spec.json), and [`c3x/receipts/p25-closure.json`](c3x/receipts/p25-closure.json).

## P24–P25: from a frozen atlas to an architecture × budget law field

P24 deliberately avoided an outcome-trained representation map. Within each material-family × side-to-move stratum, named SHAM telemetry was transformed to empirical-copula ranks separately for each engine. The engines were then aligned into an engine-symmetric shared coordinate system using coordinate-wise medians plus explicit cross-architecture disagreement coordinates. A frozen balanced refinement tree created nested state quotients `K=1 → 2 → 4 → 8`.

P25 preserved that constitution and asked a harder question: **is the atlas itself stable as search budget changes?** It is substantially more stable at coarse `K=2` than at fine `K=8`. That means a fine search-state label cannot silently be treated as an engine-independent, budget-independent natural kind. The next ontology must therefore distinguish the architecture index from the search-budget index rather than folding both into a single state name.

This remains a **finite intervention-response** programme, not a claim of full dynamical MDP bisimulation, and the descriptor court remains finite-set descriptive factorization rather than causal identification of source-code features.

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
5. **Transport is earned.** Version, engine family, architecture and search budget are possible causal indices, not nuisances to average away automatically.
6. **Negative results are first-class artifacts.** A failed transport law narrows the ontology and remains in the lineage.
7. **No post-hoc representation rescue.** A sufficiently expressive alignment can make almost anything look equivalent; alignment capacity is part of the scientific hypothesis.
8. **Executable theory is not self-validating.** Generated constitutions may constrain a court, but only world contact and adjudication can update scientific authority.

See [`GOVERNANCE.md`](GOVERNANCE.md) for repository-level rules.

## Long-horizon ambition

```text
instrumentable chess engine
→ causal mechanism atlas
→ architecture × budget causal-law field
→ evidence-carrying move explanations
→ general black-box reverse engineering
→ corrigible chess world model / successor AI
```

The point is not to make an engine narrate itself. The point is to make an explanation **survive interventions, counterfactual worlds, rival architectures, changing search regimes and attempts to falsify it**.

## License boundary

Stockfish-derived patches and distributed patched binaries remain subject to the applicable GPLv3 obligations. C3X keeps exact upstream and corresponding-source provenance as a release requirement. Repository-native C3X components may have their own license metadata; upstream obligations take precedence where derivative code is involved.
