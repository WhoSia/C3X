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

**P7 CLOSED_SCOPED_HOLD — actual tactic-matched and depth-dependent root support court:** Pre-frozen 32 new September broadcast groups distinct from P5's first 16 yielded 29 legal ply32 boards. From 22,336 legal pairs, only 1,705 matched immediate legal opponent recapture class, 11 matched passed-birth-toggling root pairs in just 3 broadcast groups, ZERO passed-birth contrast with identical original mover square. Real Stockfish16 cold 10k/2×30k/80k qualified 17 baseline near-equal pairs, 8 also tactic-matched and 5 same-origin; **only ONE of the eight tactic-matched pairs kept the same nonzero preference sign and <=50cp at completed depths8/12/16** (CECLUB f3f4 vs g3g4 gaps +29,+31,+42cp, 2/2 repeats per depth, no identified chess-concept cause). Five others reversed preference over depth, two lost margin support. In a distinct mathematical subcourt, all original 19 real passed-pawn birth events were decomposed by the 2×2 pawn-coordinate × enemy-blocker configuration into 5 position-alone, 12 opponent-configuration-alone, 2 either-alone, 0 joint-required; this is board-predicate geometry, **NOT legal root intervention or engine causal mediation**. Same frozen 32 games at ply32/64/80 had zero STRICT birth root matches throughout; later-ply denominators are duration selected. [Full P7 real empirical court](c3x/receipts/c3x-013-p7-scoped-closure-20261008.json), [Drive full results](https://drive.google.com/drive/folders/1ehjBFtuBYo7WQdfHvQDkVxVmQRZow9h_).

**P8 OPEN — actual two-engine, corrected en-passant and continuation-confluence experiments completed (mechanism HOLD):** [P8 experiment constitution](c3x/ontology/c3x-013-p8-event-context-mediation-precommit.md). P8-E1 real pinned classical Ethereal versus Stockfish on eight prior frozen tactical pairs: only ONE stable across all three complete search depths in both engines. P8-R1 independently froze a new 32 Lichess-broadcast source cohort; R2 found 8 legal born/not-born comparisons with actual two-engine same-direction scores, but **EP1 repaired en-passant victim matching** and disqualified ONE, leaving 7 currently tactically eligible historical score contrasts without any identified causal chess concept. P8-R3 naive own/opponent passed-pawn sign rule failed on 3/8 retrospectively tested pairs; P8-R4 two-reply conditional controls supported 4/8 and Stockfish showed one reply-dependent orientation reversal. Under EP2 natural NZ and EP4 source-frozen TCEC, a white pawn's one-versus-two-square push can create or not create a passed pawn, yet normal/en-passant BLACK captures reach exactly the SAME FULL six-field FEN; **neither engine selected those converging captures as immediate best reply** in the two cases. EP3 frozen 32 FRESH additional broadcasts (ranks81–112): 14 legal exact two-ply confluences from 7 source groups; four toggle a newly passed pawn but only ONE matches repaired tactical hazard. EP5 real two-engine PV check across all 14: 3 motifs actually use BOTH corresponding converging opponent replies in BOTH engines at at least one common completed depth, but the ONE birth-toggling search-used case FAILS hazard equality and near-equal comparison; stable two-engine/PV search use does NOT identify a pawn-concept mediator. EP6 proved a carefully scoped history-safe conditional confluence lemma: capture decreases the mover's pawn count from N to N−1, ensuring pre-capture histories cannot repeat in future, unlike generic FEN equality (counterexample verified). [EP2–EP4 canonical scoped receipt](c3x/receipts/c3x-013-p8-ep2-ep4-confluence-scoped-court-20261008.json), [EP5–EP6 canonical scoped receipt](c3x/receipts/c3x-013-p8-ep5-ep6-pv-and-history-scoped-court-20261008.json), [all raw science archives on Drive](https://drive.google.com/drive/folders/1ehjBFtuBYo7WQdfHvQDkVxVmQRZow9h_). **No P8 causal/transport/human science PASS. C3X 0.14 is ONLY an unnamed, unopened paradigm candidate; no formal title yet.**


**P8-EP7/EP8 continuation — genuine three-arm engine observation, bounded Track B integration (not a causal promotion):** EP7 established that a legally convergent reply gives an identical history-safe post-capture continuation but cannot force equality of original root move values when other opponent replies exist. EP8 then compared (i) actual free opponent choice after each root, (ii) the *genuine UCI `go searchmoves` restriction* to the convergent capture, and (iii) a separately cold-restarted identical post-capture FEN at depth minus one. At pre-frozen TCEC S30 rank111 ply48 `b2b3` vs `b2b4`, the convergent `c4b3` capture is legal (normal/en passant), yet **Stockfish 16 and independently implemented Ethereal 14.40 each chose `c4d3` (capturing the White queen on d3) as the free reply in all depths8/12/16, both branches, two cold repetitions: 0/24 free replies selected convergence**. The twelve paired identical-FEN cold comparisons were exact (12/12); all eight targeted regressions passed. This single-source observation rejects conflating an *available* convergent path with the opponent's *selected* path; it cannot isolate passed-pawn causality or identify TT/history/LMR events. [EP8 scientific scoped receipt](c3x/receipts/c3x-013-p8ep8-three-arm-confluence-and-reply-relevance-court-20261008.json), [genuine EP8 workflow](.github/workflows/c3x-013-p8ep8-tcec-conditional.yml), [EP8 Drive source ZIP, byte-verified](https://drive.google.com/file/d/17mFrhEKVVZwkLU0d2HcA2I95174gDlhv/view).

**Separate PGN product Track B:** The original EP8 two-engine JSON was consumed by `c3x_explain` on a legal FEN-root PGN test. Six conditional-search observations appeared as `CONVENTIONAL_HEURISTIC_COMMENTARY` only; the renderer and sentence verifier passed, causal atoms=0, with no human learning/quality claim. This is real scientific-source-to-product *integration*, not a full PGN dataset demonstration or scientific PASS. [Actual evidence integration CI](https://github.com/WhoSia/C3X/actions/runs/37790118143), [scoped integration receipt](c3x/receipts/c3x-013-p8ep8-real-pgn-observation-integration-court-20261008.json), [byte-verified Drive product artifact](https://drive.google.com/file/d/1CFohwLnn8Q-GGXKQOyH5n5KG0zkcod66/view). **P8 stays OPEN / causal mechanism HOLD; 0.14 stays unopened and unnamed.**


**P8-EP9 — source-native Stockfish 16 TT cutoff reverse engineering, direct root-pair flip, strictly local authority:** [Canonical source-level court](c3x/receipts/c3x-013-p8ep9-stockfish16-main-qsearch-tt-cutoff-root-pair-court-20261008.json) · [read-only Actions #4](https://github.com/WhoSia/C3X/actions/runs/37792544422) · [byte-exact Drive scientific capsule](https://drive.google.com/file/d/1vWieStVge4a7K02GMy8VUYaSeB7WUMIL/view). From pinned official SF16 source `68e1e9b3811e16cad014b590d7443b9063b3eb52`, compiled a clean baseline and a C++-instrumented sham. Distinct early TT bound **return** sites in the main search and quiescence search were counted and independently blocked using OFF/MAIN/QSEARCH/BOTH; all other TT uses remained live. Across 28 measurements of the historically used TCEC and CECLUB games plus a synthetic starting-position control, **all clean-versus-counter-sham outcomes matched exactly**. Explicit `go depth D searchmoves f3f4 g3g4`, MultiPV2, on the *historically pre-frozen marginal CECLUB pair* yielded depth8 White gap **+29cp OFF → −5cp MAIN**, flipping `f3f4` to `g3g4`; QSEARCH-only produced +13cp and no flip; BOTH −10cp and flip. Depth12 gap OFF +31cp, MAIN +3, QSEARCH +19, BOTH +25, **no first-move flips**. Two cold repeats each. Separate unrestricted CECLUB root depth12 chose `f3f4` OFF, `b3c4` with either one cutoff channel disabled, and `f3f4` with both disabled: search-path interaction/nonadditivity. **Do not call this a chess concept explanation**: changing an entire early-return family alters global search and node budgets; this does not establish a minimal TT event certificate, a passed-pawn or center-control cause, independent holdout or cross-engine transport. Earlier G9.5 P13–P15 already established narrower local search-event mechanisms; EP9 specifically supplies a pinned SF16 main/qsearch family-falsifier and intact no-op control. P8 OPEN / conceptual-causal HOLD; 0.14 unnamed/unopened.


**P8-EP10 — one native TT early-return occurrence is locally preference-relevant, with exact scientific limits.** Official pinned Stockfish16 `sf_16`, inheriting the certified EP9 counter-sham, now allows precisely *one* otherwise-eligible bound-cutoff return to be suppressed by site and cold-execution ordinal while preserving other TT reads/ordering/writes. Under source-frozen earlier P7 CECLUB `f3f4`/`g3g4` with MultiPV2 at depth12, **MAIN occurrence #32** switched root choice `f3f4` (signed pair gap +31cp) to `g3g4` (−8cp) in both independent cold processes. All original observer-vs-new observer shams and unreachable-event sentinels passed; the fixed exploratory grid was 8 prechosen ordinals × MAIN/QSEARCH × depths8/12 and two cold repeats. **No QSEARCH single-return root flip** appeared in that grid. At depth8 MAIN#32 did NOT switch root choice. These are *execution-occurrence* interventions, not a TT key/state-independent causal mechanism or a chess-strategy concept; the target was identified inside a multi-try grid and is therefore discovery evidence only. [Precommitted design](c3x/ontology/c3x-013-p8ep10-single-tt-cutoff-occurrence-precommit.md) · [source-native scoped receipt](c3x/receipts/c3x-013-p8ep10-single-tt-return-local-root-preference-reversal-court-20261008.json) · [run #37794566744](https://github.com/WhoSia/C3X/actions/runs/37794566744) · [raw 13/13 integrity-verified Drive archive](https://drive.google.com/file/d/1I7nxO8QJjBeLpNffcJ-2HFU1wn0kLICb/view).

**Same-position post-discovery falsifier (not independent replication):** A second run reversed only UCI `searchmoves` candidate order, checking both `f3f4 g3g4` and `g3g4 f3f4`. With depth12 MAIN#32 the choice flipped in BOTH orders, two cold repeats each; at depth8 it did not flip. Native event tuple (site1, ordinal32, ply2, depth2, alpha99, beta100, return108) was identical in both orders, **but the tuple without raw TT-key and full call-path equality does not certify invariant event identity**. All shams and sentinel controls passed. [Precommit](c3x/ontology/c3x-013-p8ep10-root-order-permutation-falsifier-precommit.md) · [scoped receipt](c3x/receipts/c3x-013-p8ep10-root-order-permutation-scoped-court-20261008.json) · [run #37795943619](https://github.com/WhoSia/C3X/actions/runs/37795943619) · [raw 14/14-verified Drive archive](https://drive.google.com/file/d/1_7dLE060NsKQKKilmEPaqzZadbAB1TEz/view).

**Separate Track B integration:** The *authentic* EP10 JSON is byte-locked by SHA-256 at the PGN CLI; its single source-conditioned TT event diagnostic produces **one** traceable sentence tagged `CONVENTIONAL_HEURISTIC_COMMENTARY` only, with zero unauthorised causal atoms and a successful modified-JSON rejection test. No strategic explanation, engine-independent mechanism or human teaching benefit follows. [Source adapter](c3x_explain/p8_ep10.py) · [integration court](c3x/receipts/c3x-013-p8ep10-actual-search-path-to-pgn-integration-court-20261008.json) · [run #37796474311](https://github.com/WhoSia/C3X/actions/runs/37796474311) · [raw 6/6-verified Drive ZIP](https://drive.google.com/file/d/16AU5cL-NF7mdEBWq9bEC64sqeZ3ihATQ/view). Methods rivalry checked against Zhang & Nanda ICLR24, Geiger et al. JMLR25, and Martin et al. IST25 (DOI `10.1016/j.infsof.2025.107679`, normalized existing HAL open-access paper into Drive 10_PAPERS). **P8 OPEN / chess-native causality HOLD; 0.14 unnamed/unopened.**


**C3X 0.14 FORMALLY OPEN (2026-10-09) — Transportable Search-Mechanism Evidence, Chess-Concept Mediation & Faithful Explanation Systems.** The previous C3X 0.13 P8-EP11 was **SCOPED-HANDOFF**, *not* chess-strategy causal PASS. EP11 pinned SF16 native TT event MAIN#32 to queried board key `5794315daed72c1b`, full node FEN `2r2rk1/p1q2ppp/bp1bnn2/3pN3/2pP1P1P/1P2P1P1/PB2NRB1/R2Q2K1 w - - 1 18`, stored TT lower bound 108 vs β100, at depth12 unique legal descendant **17.f4 Qc7**. Native source key+FEN replay equaled ordinal intervention across 8/8 source/order/depth/repetition tests, without proving stored TT-entry complete provenance (Stockfish16 stores only 16-bit TT key discriminator). [C3X 0.13 canonical scoped handoff receipt](c3x/receipts/c3x-013-p8ep11-native-tt-fen-key-legal-ancestry-scoped-handoff-20261009.json) · [native 15/15-verified data](https://drive.google.com/file/d/1QmtE9N7VcVPahWrtLiA25vTW27RIMFwe/view) · [independently enumerated exact legal ancestry](https://github.com/WhoSia/C3X/actions/runs/37799330912) · [legal origin 4/4-verified ZIP](https://drive.google.com/file/d/1O-M9UGpJISboil0Pv4FHTheEePLhAwV0/view).

**C3X 0.14 P1: prospective official TCEC S29 source-game intake and first genuine development-only null.** [Formal charter](c3x/ontology/c3x-014-transportable-search-mechanism-concept-explanation-constitution.md) · [outcome-blind source precommit](c3x/ontology/c3x-014-p1-tcec-s29-source-disjoint-eligibility-precommit.md) · [native TT development precommit](c3x/ontology/c3x-014-p1-s29-dev-source-native-tt-family-transfer-precommit.md). Pinned official `TCEC-Chess/tcecgames` S29-final (`3dd69a40...`, git blob `68141d7a...`) found 100 Superfinal games, all 100 with legal same-white-pawn one-/two-square candidate at ply18, 52 distinct opening-prefix groups; deterministic source-only selection froze **4 development / 4 separately sealed heldout** groups. [Public source receipt](c3x/receipts/c3x-014-p1-official-tcec-s29-prospective-source-freeze-20261009.json) · [public source ZIP](https://drive.google.com/file/d/19W8xG5g00fmpSyHSY-EkznYhocwzz-5h/view). The heldout is **procedurally sealed** in [separate raw artifact](https://drive.google.com/file/d/1qV1EIjbwNprt6JxhdlYyg5XKT65_QnRK/view), not cryptographically inaccessible; no development code imported it. Independent source games remain within broad TCEC tournament ecology.

**P1 actual native Source-Disjoint Development Court: sham PASS / Root Preference Flip NEGATIVE.** Native separately compiled unmodified Stockfish16 versus EP9 TT early-bound-return instrumentation, 4 development games, depth8/12, 2 cold restarts each: **16/16 clean-vs-OFF sham exact, 0/16 MAIN, 0/16 QSEARCH and 0/16 BOTH root-choice reversals**, though native events were actually blocked (20,784 MAIN, 20,034 QSEARCH, counted across dependent repeats; these are not source-independent games). At S29 round29.1 depth8 MAIN score gap changed +54cp→0cp but root choice was unchanged, demonstrating output-quantity sensitivity is distinct from binary preference change. All eight world/depth panels had exact two-cold-run reproducibility in all four arms. This limits any naive transport of the previously selected marginal CECLUB event flip to prospective ordinary pawn-push candidates; with only four games and no matched near-tie pairs it does not refute TT relevance. [Scientific null receipt](c3x/receipts/c3x-014-p1-official-s29-four-game-native-tt-development-null-court-20261009.json) · [real original/source/patch/telemetry ZIP](https://drive.google.com/file/d/1vXEddoMihq6aNzoSyBpP8rsUDqclZBNX/view) · [Actions SUCCESS](https://github.com/WhoSia/C3X/actions/runs/37800898994). **Strategic chess-concept causal mediation remains HOLD; P1 sealed holdout has NOT been opened.**

**Canonical literature custody for C3X:** Méndez et al. (2023), *Metamorphic Testing of Chess Engines*, DOI 10.1016/j.infsof.2023.107263, [Drive PDF](https://drive.google.com/file/d/1jMrLzQEycFkCMIUSL2iLT1NdR1Td3ros/view); Clark et al. (2023), *Metamorphic Testing with Causal Graphs*, DOI 10.1109/ICST57152.2023.00023, [Drive PDF](https://drive.google.com/file/d/185mXmiUfuKiOCcMvFixhMMtdAQsbFpS3/view). Both original intake PDFs were positively identified, duplicate checked by names and DOIs, renamed in place and moved to `10_PAPERS`. These are explicit prior-art rivals/measurement methods, not proofs of C3X novelty. Bot-authored commits and Actions git writes forbidden.

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
