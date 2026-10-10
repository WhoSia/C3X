# C3X 0.22 — Search-Order–Conditioned Decision Dynamics & Chess Microstructure Causality: Native TT Intervention Semantics, Response-Contingent Affordance Transmission, Prospective Move-Choice Predictions & Cross-Ecology Falsification

**PROPOSAL / NOT ACTIVE (2026-10-10).** C3X 0.21 remains ACTIVE. C3X 0.22 enters only after the natural-O writer–reader remapping and an explicit fresh independent cohort source/forecast precommit. No user authorization needed to propose; final activation must not reclassify earlier FAIL.

## Scientific question

Which fine-grained legal chess transitions and actual C++ search-history/memory-consumption events distinguish two otherwise identical initial-board searches that choose different legal root moves?

**Research object** is not a named tactic label, a centipawn narrative, or alpha-gate eligibility alone; it is a *move-choice transmission event* in a reproducible native alpha–beta search process. Board-level interventions (root legal admissibility or pin line unblocking) and search-state interventions (physical TT reader blocking) are distinct experimental factors and have to be audited separately.

## Frozen historical basis / theory repairs

- 0.11–0.15 explored chess opponent affordance and named/anonymous tactical microfactors, SEE pinned recapture and WeakQueen blocking. **CPP_224 / universal PAG and pin-type response transfer failed**; targeted root SEE interventions did yield bounded categorical move switches with nonmonotone broader manipulations.
- 0.16 root-order P4: \`O\` original SF16 root order, \`F\` PGN-played move rotated to first, \`Z\` no-contact; O vs F different final bestmove in **4 of the March16 games**. This is a *real search ordering treatment*, not a pure natural SF baseline.
- 0.18–0.19 full64 TT writer/slot/epoch/reader proof and genuine native assignment/cutoff measurement. Jan J2/J3/J4 FAIL; Feb F19.5 FAIL, K4 **0/4 FAIL** preserved.
- 0.20-B/C known adaptive game3 first alpha-gate source threshold \`−190↔−189\` changed final choice with precommitted ladder **6/6**; this holds for that game, not yet as a universal search law.
- 0.21 P1 March16 engine-blind **635 legal root move state-transition profiles**; from 32 STRICT/BROAD search cells, 31 actual F physical TT FIRST contacts, 2 categorical F-world bestmove flips. P1-R1 later TT probe 31/31, actual eval-as-score use 30/31, cutoff 2/31; #9 first TT suppression affects final move despite later probe-only route.
- 0.21 P2 full31 factorial (248 native cold arms): FIRST 31/31 delivered and 2/31 final changes; SECOND 31/31 delivered and 0/31 final changes; BOTH second contact only 5/31 (path-dependent opportunity). #4 and #9 both had original-O bestmoves equalling F+FIRST's bestmoves.
- 0.21 P2 chess microstructures: game4 F/V both capture identical white pawn on h4 and preserve *the same entire 29-move immediate opponent legal reply set*, yet 27/29 matched reply branches yield different next black legal move sets. Game9 knight f6→h5 exposes white bishop capture d4→g7 and all 40 shared response branches yield different subsequent black legal move sets.
- **O-native remapping P2-R1**: registered as separate source-only selection and full16 native court on 2026-10-10; pending run result at time this proposal was frozen. No results prefilled. F physical writer lineage must never be transplanted into O.

## Formal system-level object

Fix ordinary Standard Chess board+halfmove+fullmove source context \`s\`, legal root choice set \`A(s)\`, initial root order \`o\`, native search binary/parameters \`b\`, depth \`d\`, and search-state intervention \`u\`. Define

\`Y(s,o,u,b,d) := exact categorical final bestmove returned by a fresh cold UCI engine process\`.

\`M_t\` is the exact native full64 TT physical table and writer/reader lineage at internal time t, including save/reader/assigned-score/cutoff events. \`X(s,a)\` is the **source-engine-blind** vector of occupancy, piece-to-square attack delta, pinned legality, defense count, opponent legal response set and post-opponent own legal response set.

At fixed board and order:
\`D_TT(s,o,u) = 1{Y(s,o,u,b,d) != Y(s,o,ZERO,b,d)}\`, **only** counted when intervention source contact is witnessed. Natural root-order sensitivity:
\`D_order(s) = 1{Y(s,O,ZERO,b,d) != Y(s,F,ZERO,b,d)}\`.
Difference in these categorical outcomes does NOT imply a linear numeric interaction coefficient or a natural mediator by itself. The paper must directly estimate whether the same class of source intervention has stable effects when physical writer targets are **independently mapped** in O versus F.

For legal reply microstructure use a response-conditioned discrepancy:
\`A_1(s,a)\` is opponent's legal replies after root move a;
\`A_2(s,a,r)\` is own legal replies after opponent response r.
For two legal root choices a,b:
\`D_2(s;a,b) = |A_1(s,a) ∩ A_1(s,b)|^{-1} * sum_{r in intersection} 1{A_2(s,a,r) != A_2(s,b,r)}\`
when the intersection is nonempty, else report NOT_COMPARABLE. Game4 provides 27/29, game9 40/40 by this definition. This is a board-legal relation, not a causal valuation/explanation in native Stockfish until source outcome transmission is independently tested.

## Three possible paper projects and competitive position

### PAPER A — highest near-term priority
**"When Search Order Changes the Move: Source-Exact Transposition-Table Interventions in Alpha–Beta Chess Search"**

- Method: independent O/F complete native physical writer→reader mapping; first-vs-second consumer time factorial; event-level full64 lineage, genuine TT evaluation assignment/cutoff; root-depth leader transmission; source-only controls.
- Main claim to attempt *not yet demonstrated*: match a class of order-conditioned native TT source interventions that predict which held-out root moves flip, with counterexamples and no-contact rejections. Avoid universal "TT determines chess choice".
- Evidence ready: C3X0.18–0.21 P2; critical missing experiment is **natural O independent source court**, independent unseen month, multi-depth generalization and external engine family.
- Baselines: original unmodified Stockfish16 and first-source no-contact sham; root order alone; α crossing only; input board heuristic labels only; no TT.
- Primary outcome: legal final categorical bestmove and conditional accuracy on **actual source contacts**, not score/number-of-probes-only.
- Audience fit: computer games, AI search, interpretable planning and program-causal analysis.
- Verdict: **methods-oriented pilot suitable for technical preprint after O data / external cohort; journal/conference-strength claims require independent ecology.**

### PAPER B — chess decision primitives
**"Beyond Pins and Skewers: Response-Contingent Legal Affordance Signatures for Explaining Chess Move Choice"**

- Method: source-engine-blind 1/2/3-ply legal game-state transitions, positional identity and branch enumeration; compare \`D_2\`, move-specific attacker/defender changes, check/recapture legality.
- The #4 same immediate response *set*, 27/29 next-own response-set contrasts, and #9 reopened bishop capture are concrete counterexamples to label- and reply-count-only summaries.
- Missing: a much broader disjoint cohort, human adjudicated move-pair tactics, source-matched engine intervention to identify causally operative chess features; stratified vs named motif descriptors and simple heuristics.
- Do not call mere reply-set difference an *engine explanation* or say only fine-grained structures are universally predictive.
- Verdict: **second paper; publishable only when explanatory yield and transfer exceed trivial "two different positions have different legal moves" baselines.**

### PAPER C — benchmark/tooling or dataset companion
**"Causal Fidelity Benchmarks for Chess Search Explanations: From Memory-Consumer Witnesses to Legal Response Graphs"**
- Test case taxonomy: true native source contact, synthetic effect delivered, no-contact, successful final choice restoration, path-diverged interpretation, engine-blind legal response facts, generalization failure.
- Must include third-party independent reproductions from SHA-frozen binary/source, disjoint July/April-type source split, at least one other alpha–beta engine (or compare without claiming source equivalence).
- Metrics: actual-contact precision/recall, root bestmove prediction conditional on eligibility, faithfulness to native counters, invalid-attribution rate, human comprehensibility with blind annotators, computation cost.
- Verdict: **dataset/software paper once release, documentation, licenses, and benchmark protocol reach independent usability.**

## Verified adjacent literature (abstract/metadata-level; not claimed full-text review)

1. Yngvi Björnsson, *Chess and explainable AI*, ICGA Journal 46(2), 2024, DOI: 10.3233/ICG-240256. Survey framing: why human-understandable explanations are distinct from playing strength. https://doi.org/10.3233/ICG-240256
2. Patrik Hammersborg and Inga Strümke, *Information based explanation methods for deep learning agents—with applications on large open-source chess models*, Scientific Reports 14:20174 (2024), DOI: 10.1038/s41598-024-70701-2. Concept-detection / information-flow explanation for chess **neural** models, a complementary but not equivalent mechanism to alpha-beta TT source edits. https://doi.org/10.1038/s41598-024-70701-2
3. Francesco Spinnato, *Towards Piece-by-Piece Explanations for Chess Positions with SHAP*, arXiv:2510.25775 (2025 preprint), https://arxiv.org/abs/2510.25775. Board piece ablation feature attribution contrasted with same-board native TT interventional source analysis.
4. A. Bhaskar, J. Cheng, D. Chen, *Language Models that Play Chess and Explain Their Moves*, arXiv:2610.03695 (posted 2026-10-02), https://arxiv.org/abs/2610.03695. Language-model explanations and expert encoder architecture; C3X should prioritize verifiable native source effects rather than compelling post hoc natural-language narrative.
5. A. Parfenova, *Do Chess Explanations Reflect Model Decisions? Behavioral and Token-Level Tests of LLM Reasoning Faithfulness*, arXiv:2609.22245 (2026), https://arxiv.org/abs/2609.22245. Motivation for independently testing faithfulness beyond plausible chess narratives.
6. Official Stockfish terminology docs: transposition table, iterative deepening, late-move reductions and move ordering; these describe living versions and are **not substitutes for pinned SF16 source**. https://official-stockfish.github.io/docs/stockfish-wiki/Terminology.html

**Critical novelty check pending:** targeted full-text reading and citation chaining of *explainable search* (Baier/Kaisers 2020, 2021), engine-specific chess causal explanations, and contestable prior art on order sensitivity. We must not assert literature novelty from abstract-only search.

## P0–P4 research gates to *activate* 0.22

- P0: C3X 0.21-P2-R1 frozen independent natural O source/run complete, no-cold-drift and F physical target not reused; criterion is a conclusive report including **negative** outcomes, not a positive move-flip count.
- P1: Reusable structured per-root native witness \`(full64-writer, reader, value/cutoff, depth, root-call, candidate move, pre/post window)\`, exact source alignment; Source path divergence explicitly diagnosed.
- P2: Fresh independent ordinary chess broadcast PGN source (e.g. new April 2026 month, exact hash frozen, no engine outcome selection). 16 game benchmark is a **pilot**, scale to 64–128 legally eligible games after measuring feasibility with 16. Freeze units by PGN game not role-cell because STR/BROAD within game not independent.
- P3: Precommit predictive hypotheses on final choice switch, by both O and F order, new physical TT remapping, chess microstructure measures; forbid rebuilding classifiers after seeing held-out choices.
- P4: Independent replication / sanity check, source patch API tests, negative controls, all FAILs, legal move output, black/white and tactical phase stratification, effect sizes and confidence intervals; produce a limitations-aware manuscript draft.

## Licensing / release

Modified Stockfish binaries/source require provenance and compliance with Stockfish's GPLv3 licensing, and engine-free broadcast PGNs with the Lichess broadcast archive's specified attribution/share-alike obligations. Plan an auditable release with manifests, source patch, hashes, legal move data and run instructions; do not redistribute proprietary or undocumented assets.

**Current status:** PREPARATION / PAPER SCOPING. No paper has been submitted or accepted, no independent predictive law proved, C3X 0.22 not yet activated.


---

## POST-OUTCOME ADDENDUM — Natural-O TT independent source court (2026-10-10)

This post-outcome note does not change the historical precommit or the original 0.22 proposal, which was frozen before this run.

[Native Actions #38044580147](https://github.com/WhoSia/C3X/actions/runs/38044580147) SUCCESS; downloaded ZIP SHA256 25fea2dfa871f2f97f098b8e204bf99b5aa5e1aca76fc905580ee2748dfb727c; native JSON SHA256 4cb54469460f6402952b269ab123c1681c7fe1670a3d829905db6640e209d17e; 24/24 member hashes PASS. [Canonical native outcome receipt](../receipts/c3x-021-P2-R1-independent-natural-O-physical-TT-order-interaction-20261010.json).

O-world writer–reader pairs were independently selected from natural-O discovery, not F-world physical source IDs: 31/32 eligible and contacted role cells, 23/31 complete six-field UCI output changes, and 2/31 final bestmove changes in ONE distinct game. Game1 natural O selected bishop d3b5; O+FIRST source-exact physical TT reader block selected queen b3c2; source PGN-played-first F selected knight a3b5. The first recorded same-source child-return change was 119→209 with alpha418, i.e. SAME_GATE, not immediate alpha crossing. O/F physical triplets matched in 21/31 eligible role cells overall, but game4 BROAD and game9 STRICT differ. F+FIRST changed final root choice in games4 and9 while independently mapped O+FIRST did not. Root-order-conditioned source intervention sensitivity is directly observed in this bounded March cohort.

## Preliminary PAPER A abstract (draft, NOT submitted)

> Alpha–beta chess engines reuse cached search information, but a transposition-table hit does not establish that its contents influence the move ultimately played. We investigate this gap in source-instrumented Stockfish 16 through full-position-key writer–reader provenance, native score-assignment and cutoff witnesses, controlled reader suppression, and independently enumerated legal move transitions. In a fixed 16-position broadcast corpus, prioritizing a recorded move in initial root ordering altered the final move in four positions. Under this played-first context, first-reader suppression changed the final move in two of 31 contacted selector cells. Independent target reconstruction under natural root ordering also changed the move in two contacted cells, but both represented a different single game; the earlier two affected games were no longer sensitive. Separately, move-level legal analysis reveals cases where equal immediate opponent response sets conceal differences in later available moves. These bounded results support a reproducible method for interrogating search-order and memory-consumption effects. Prospective generalization and unique chess-feature mediation remain open.

**PAPER A now has a documented empirical pilot**, but role cells nested within a game are not independent observations; no generalized effect probability may be inferred from 2/31. No paper submitted or accepted.

## Updated readiness

- P0 independent natural-O native TT writer–reader remapping: COMPLETE, negative controls and SHA PASS.
- P1 unified causal trace and source-alignment semantics: PARTIAL; event identity across divergence remains unresolved.
- P2 disjoint April-month or other future source-only corpus: NOT STARTED.
- P3 risky prospective final root-choice and primitive-structure forecasts: NOT STARTED.
- P4 independent reproduction, release/legal audit, publication-ready validation: NOT STARTED.

Keep C3X 0.21 ACTIVE. C3X 0.22 remains a prepared PROPOSAL.
