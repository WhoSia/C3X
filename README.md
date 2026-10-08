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

## C3X 0.12 current research and custody (2026-10-08)

**Stage:** OPEN / DEVELOPMENT ENGINEERING PASS / SCIENTIFIC REASON IDENTIFICATION HOLD (not a 0.12 scientific PASS). Six pre-outcome source-game worlds from archived provider PGNs: 3/6 cold qualified pairs, 3/3 target/sham board edits measured at post-pilot fixed depth 12 with exact repeats. Cross-budget near-equal support across B0, TARGET and SHAM survived only 1/3, and no unique chess-strategic mediator or cross-engine transport was identified. Non-mainline opponent replies were legal but lexical developer controls, not validated best-response falsifiers.

- [Canonical 0.12 evidence and Drive custody receipt](c3x/receipts/c3x-012-six-source-development-review-20261008.json)
- [Six-source frozen development seeds](c3x/data/c3x-012-six-source-development-seeds.json)
- [Read-only Stockfish CI](.github/workflows/c3x-012-six-source-qualification.yml)
- [Drive verified final evidence archive](https://drive.google.com/file/d/1iUSW8P10DS9KX_Gl4jQIiFSGq5TAtlUk/view)
- [0.13 formal-name proposal only — NOT OPENED](c3x/ontology/c3x-013-formal-name-proposal-only.md)

Explain I9 commentary is a separate Track B implementation (37 recent regression tests PASS); it cannot upgrade chess-science authority. P23 FAIL, P24/P25 HOLD, Q0 DENIED unchanged. No bot-authored commits or CI writeback permitted.

## Current scientific frontier

**G9.5** is now returning the mechanism programme to C3X's founding chess question: explaining marginal preference between near-equal legal moves.

- **P13 (closed):** reconstructed root-candidate competition and found local exact-event preference-boundary crossings, but no frozen winner/rival-oriented transport signature.
- **P14 (closed / PASS):** prospectively promoted the unordered legal-move pair to the scientific object. Across 24 fresh positions × 3 engines, 19 pairs were admitted, 352 exact targets fired, and 42 pair-edge reversals produced two replicated orientation-free signatures spanning engines, positions, and both source months. Reciprocal multi-engine geometry remained local-only.
- **P15 (authorized):** returns from search-event causality to chess-board structure. The target estimand is a prospectively matched, legal-pair-preserving board intervention that changes exact-event susceptibility and pair preference in a controlled board × search factorial.

C3X now has a binding **two-track constitution**:
- **Science / Novelty Mainline:** why this near-equal legal move rather than that one, with causal authority earned prospectively.
- **Explanation Implementation:** build a practical **PGN → explanation/commentary** system using C3X certificates where available and clearly labelled conventional techniques elsewhere.

See [`docs/C3X_TWO_TRACK_CONSTITUTION.md`](docs/C3X_TWO_TRACK_CONSTITUTION.md).

Scientific meaning and claim authority live in the Research OS / Notion lineage. This repository is the executable byte authority for the code that realizes those tests and the implementation surface for the separately governed explanation system.

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

C3X has **no repository-wide preferred implementation language**. Language is non-authoritative: choose the implementation that best reduces scientific or engineering risk for the specific component, and document why. Existing Python code is precedent, not a mandate.

| Work shape | Typical fit — not a default | Why it may fit |
|---|---|---|
| Typed scientific kernels, deterministic constitutions, graph/certificate compilers | **Rust** | strong invariants, reproducible binaries, explicit failure surfaces |
| Chess legality/features and rapid experiment composition | **Python / python-chess** | use when the chess library or fast orchestration is a material advantage |
| Independent receipt/schema verification, browser/report tooling | **JavaScript / TypeScript** | useful second runtime and tooling ecosystem |
| Engine-native instrumentation, search-critical or numerical checks | **C / C++** | preserve native engine semantics and avoid adapter distortion |
| Statistical audit | **R / Julia / Python as justified** | choose by the numerical method and independent-failure-mode value |
| Durable JVM tooling or services | **Kotlin / Java when justified** | use only when a JVM-native role actually exists |
| Other components | **Any suitable language** | Ada, Go, OCaml, Haskell, Zig and others are admissible when they improve correctness, verification, interoperability or maintainability |

Do not add a language merely for variety, and do not keep Python merely for uniformity. A result becomes stronger only when an independent implementation tests a real failure mode or when the chosen language makes the scientific contract more auditable.

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

See [`docs/LAWGEN.md`](docs/LAWGEN.md), [`docs/P25_THEORY.md`](docs/P25_THEORY.md), [`c3x/ontology/p25-lawgen-spec.json`](c3x/ontology/p25-lawgen-spec.json), [`c3x/ontology/p26-lawgen-spec.json`](c3x/ontology/p26-lawgen-spec.json), [`c3x/receipts/p25-closure.json`](c3x/receipts/p25-closure.json), and [`c3x/receipts/p26-closure.json`](c3x/receipts/p26-closure.json).

## P24–P26: from a frozen atlas to an architecture × budget law field

P24 deliberately avoided an outcome-trained representation map. Within each material-family × side-to-move stratum, named SHAM telemetry was transformed to empirical-copula ranks separately for each engine. The engines were then aligned into an engine-symmetric shared coordinate system using coordinate-wise medians plus explicit cross-architecture disagreement coordinates. A frozen balanced refinement tree created nested state quotients `K=1 → 2 → 4 → 8`.

P25 preserved that constitution and asked a harder question: **is the atlas itself stable as search budget changes?** It is substantially more stable at coarse `K=2` than at fine `K=8`. That means a fine search-state label cannot silently be treated as an engine-independent, budget-independent natural kind. The next ontology must therefore distinguish the architecture index from the search-budget index rather than folding both into a single state name.

P26 then tested the product space directly. Even after a frozen low-capacity cross-budget K8 correspondence, architecture was invariant in only 1/64 cells and budget was stable in 0/48 trajectories. The current scientific object is therefore an empirically required **architecture × budget indexed intervention-response field** within the tested authority ceiling.\n\nThis remains a **finite intervention-response** programme, not a claim of full dynamical MDP bisimulation. P25 descriptor compression remains finite-set descriptive factorization, while P26 only audits which descriptors are plausible intervention candidates; causal descriptor effects remain future work.

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
