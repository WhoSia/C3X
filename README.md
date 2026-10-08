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

## C3X 0.12 scoped closure and C3X 0.13 current frontier (2026-10-08)

**C3X 0.12:** CLOSED_SCOPED_HOLD. Real Stockfish 16 development evidence: 3/6 cold-qualified pairs, 3 matched legal target/sham edits, only one with near-equal margins throughout. No independent minimal strategic reason, credible rival continuation falsification or cross-engine causal transport earned. [Scoped closure receipt](c3x/receipts/c3x-012-scoped-closure-20261008.json), [full development court](c3x/receipts/c3x-012-six-source-development-review-20261008.json) and [verified source-execution archive](https://drive.google.com/file/d/1iUSW8P10DS9KX_Gl4jQIiFSGq5TAtlUk/view).

**C3X 0.13:** OPEN — [Constitution](c3x/ontology/c3x-013-constitution.md), [formal named-stage proposal](c3x/ontology/c3x-013-formal-name-proposal-only.md) (historical proposal preserved). Its first four *development* courts passed execution, NOT scientific causal explanation:

- P1: replayed P16 queen attack-map vectors. A boolean attack on e8 was to a friendly black king, not hostile pressure. 8 adversarial tests PASS.
- P2: occupancy-relative chess semantic gate; 18 combined regressions PASS, withhold concept / mechanism / human authority.
- P3: independent Stockfish16 depth12 raw measurement on P16 Ethereal worlds: original mover A-minus-B B0=-1, TARGET=+12, SHAM=+3 cp; directions opposite historical Ethereal, with unequal budgets.
- P4: Stockfish depth8/10/12/14/16, 2 independent repeats on each of three P16 worlds: B0 and SHAM flip move-preference sign across depths; TARGET does not. No cross-engine causal transport inferred.

**P5 (scoped closed, no scientific concept PASS):** Lichess September broadcast game-hash precommit selected 16 distinct broadcast groups; 14 valid legal ply-32 boards, 2 source HOLD. Center-occupancy binary board facts: 12 positive/2 negative; isolated-pawn 2/12; passed-pawn 0/14. A separate cold 10k/30k/80k engine-pair court qualified 8/14 valid boards, and a new two-run depth12 test gave concept directional prediction support: CENTER 1/3 (2 counterexamples), ISOLATION 1/1, PASSED 1/1. All three missed the precommitted minimum independent and signed-direction sample conditions. **Factual chess features are not intervention-sufficient chess strategic reasons.** [P5 scoped court](c3x/receipts/c3x-013-p5-scoped-development-closure-20261008.json), [P5 executable development archive](https://drive.google.com/file/d/1ok13bW7FtX1rH2VYZTwxKADKeplc0nw9/view).

**P6 CLOSED_SCOPED_HOLD — pawn-concept genesis mathematics, real-game support failures:** Exact isolation-file and passed-pawn blocker-set definitions proved a nonpromoting quiet pawn push preserves isolation but may create passed pawns on EITHER side. Promotion is an explicit exception. Across the frozen 16-broadcast cohort (15 valid full games), 210 quiet pawn pushes produced 0 mover-passed births and 1 opponent-passed birth; full-game reconstruction found 19 pawn births across 9 games, 10 removed blockers, 5 mixed capture/advance, 2 blocker departures, 2 pawn threshold crosses. Only 1/9 first-birth games had a legal same-piece/same-captured-type non-birth rival. That real game's Qxc7 vs Qxh6 Stockfish depth8/12/16 differences were +1201/+1085/+1082cp, FAIL the <=50cp marginality criterion: Qxh6 allowed immediate g7xh6 recapture of the queen. [Complete P6 scoped scientific receipt](c3x/receipts/c3x-013-p6-pawn-concept-genesis-scoped-closure-20261008.json), [exact mathematical genesis calculus](c3x/ontology/c3x-013-pawn-concept-genesis-calculus.md), [Drive full raw results](https://drive.google.com/drive/folders/1ehjBFtuBYo7WQdfHvQDkVxVmQRZow9h_). **No causal strategic mediator or cross-engine transport earned.**

**P7 OPEN — tactical-equivalence root-gate negative control:** A research root comparator must ensure immediate opponent legal recapture hazard does not differ, even if the move initiator, origin square and captured-piece type agree. [P7 precommit](c3x/ontology/c3x-013-p7-tactical-equivalence-root-support-precommit.md), [actual 4/4 chess-regression PASS receipt](c3x/receipts/c3x-013-p7-tactical-control-opening-20261008.json). It has not established any new engine-causal concept. A possible 0.14 *event-based concept explanation* transition is provisional and NOT opened.

[Official P1-P4 scientific-ceiling court](c3x/receipts/c3x-013-p1-p4-opening-development-court-20261008.json). [Read-only evidence archives on Drive](https://drive.google.com/drive/folders/1ehjBFtuBYo7WQdfHvQDkVxVmQRZow9h_). Explain I9 remains the separate PGN commentary product; old I8 genuine human utility HOLD is not reopened. Historical P23 FAIL, P24/P25 HOLD and Q0 DENIED unchanged. No bot-authored commits or CI writeback.

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
