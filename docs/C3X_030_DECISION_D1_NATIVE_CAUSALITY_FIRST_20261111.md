# C3X 0.30 — Decision D1: Concentrate on Native Search-Event Causality Before Adding More Explanation Methods

**Decision date:** 2026-11-11 KST. **Status:** Research direction selected, implementation work **NOT YET executed** in this decision-only artifact. **Conversation index:** C3X 32, not a software-version change. **Canonical current version:** C3X 0.30.

## Decision

**Prioritize a narrowly scoped original Stockfish16 transposition-table event → ancestor state → root-choice causal audit over adding new literature methods or general web-app features.** Keep SARFA, small-support SHAP, Cui-inspired recursive tree, ACT-Eval chess claims, independent Berserk judgement and existing Korean commentary as supporting tools; do not pretend these are full-paper replications or validated human instruction.

**Next research unit:** `0.30/P11-S4 — Native TT Event Attribution & Root-Choice Transmission`. This identifier must not overwrite the existing historical P12 lineage.

### Why now?

- Original [P11 full-strength 360-search native results](https://github.com/WhoSia/C3X/actions/runs/42944315234) showed **cold 1-thread 0/20 switch positions**, **warm 1-thread 13/20**, **fresh 4-thread 13/20**; 20 checkpoint FENs comprise four shared opening histories, not 20 independent games.
- [P11/S1 actual 480 searches](https://github.com/WhoSia/C3X/actions/runs/42964938042): warm-state 13/20 switch; physical UCI Clear Hash 0/20 and distinct UCI new-game 0/20; both match cold reference on 120/120 bestmoves.
- [P11/S2 real 140 searches](https://github.com/WhoSia/C3X/actions/runs/42965327961): two separate Clear Hash phases each restored exact baseline bestmove and node counts **20/20**, while unreset subsequent search shifts reappeared **8/20** for each reset.
- [Independent original dual-SHA audit SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42965845034) recomputed S1/S2 data with **zero new engine calls**; all [sealed original evidence](https://github.com/WhoSia/C3X/blob/main/docs/C3X_030_P11S1_S2_S3_NATIVE_STATE_RESET_WASHOUT_ORIGINAL_AUDIT_20261111.md) preserved.
- This establishes an unusually testable **engine search-state intervention phenotype**. However **UCI Clear Hash ≠ individually identified TT cell causal mediation**; the flagship original source search event→ancestor→root→future plan claim remains unproven.

## Explicit priorities

| Track | Priority | Allocation rule |
| --- | --- | --- |
| Physical search-event attribution | **P0 / main** | Native Stockfish16 TT probe/store instrumentation and narrowly targeted interventions; every claimed new mechanism must carry source diff, input history, actual native search receipt |
| Independent confirmation | **P0 scientific gate** | A wholly unseen, preregistered chess history/FEN cohort must be frozen before selecting positions and testing mechanism; developer 20 FENs are discovery only |
| Opponent-response future strategy | **P1 / gated** | After native root causality support, freeze alternative reply families and independent Berserk evaluation, compare source-static baselines; full opponent universe not presumed |
| Chess tutoring product / learner test | **P1 / limited maintenance** | Retain existing P3–P6 app; no unsupported auto-explanation as 'Stockfish's real causal reason' or claimed educational effect |
| Additional paper replication | **P2 / conditional** | Add a method only if it resolves a specified missing causal control, falsifying alternative, or indispensable benchmark |
| Broad UI / unrelated refactor | **Defer** | No major cosmetic or architectural expansion until the central physical-mechanism gate is decided |

## 0.30/P11-S4 execution contract (planned; not yet executed)

### S4-A — Observability without changing baseline

Pin same exact Stockfish16 upstream source commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, compile *unmodified baseline* and a *read-only TT logging variant* whose patch SHA, compiler and flags are archived. Record legal FEN **with complete move history**; Threads=1, Skill Level=20, UCI_LimitStrength=false, Use NNUE=false, Hash=16 MiB; instrument actual TT probes and stores with depth, bound, score, key identity, search ply, parent correlation identifier, root candidate, node count (do not disclose unverified mapping). First prove instrumentation non-interference for move/PV/depth/evaluation and exact requested/actual node costs across a predeclared small developer set; if instrumenting changes search, **HOLD**, no attribution claim.

### S4-B — Controlled counterfactual intervention

On a source-event selected **by protocol, not by whether it produces preferred change**, compare unmodified, full Clear Hash, TT **read-only/no-hit**, TT **no-store**, targeted record mask, and *irrelevant-record sham mask* where feasible. Compile exact branch SHA, control side effects and search-budget differences. Separate before/after physical trace, parent/ancestor score propagation and root final selection. Explicitly distinguish:
- `event occurred`
- `event omission changed local search`
- `effect reached an ancestor`
- `root value/rank changed`
- `root bestmove changed`.
Don't silently skip failures, no-move-change, or missing trace.

### S4-C — Independent confirmation and stopping criteria

Freeze **new** unseen positions selected without looking at P11/S4 outcomes, spread beyond related opening checkpoints (midgame/endgame, differing near-tie gaps, colors, at least several independent complete game histories). The exact sample size and seed/provenance require preregistration before selection; avoid pretending existing 20 boards are independent. Evaluate matched paired interventions, stratified by independent game history, with exact node counts and search-depth comparisons. Keep earlier 8-eligible-game broadcast prospective cohort at **7/8 HOLD**; don't replace its denominator with this new experiment.

**Promotion requires simultaneously:** (1) identified native event with reliable source trace; (2) intervention with meaningful controls and same-world legal full history; (3) ancestor→root transmission supported in specific paired cases, not mere correlation; (4) independent game confirmation and uncertainty estimates; (5) independent future-plan evaluation **only if claiming strategic value**. Otherwise report partial or null outcome and STOP the relevant claim. A failure to observe root-choice change is a result, not a reason to retrofit the cohort.

## Explicit nondecisions / rejected shortcuts

- **Do NOT conclude** changing move implies a learned RL-policy stochastic sampler: stockfish full strength alpha-beta is distinct from Skill Level<20 `Skill::pick_best` PRNG.
- **Do NOT conclude** `Clear Hash` proved a specific TT entry's path.
- **Do NOT describe** synthetic tests as actual engine experiments, or independent Berserk leaf judgements as a complete opponent best-response universe.
- **Do NOT treat** a paper-inspired kernel as full replication of SARFA/SHAP/QUEEN/Cui unless exact algorithm and empirical protocol were run.
- **Do NOT call** P11 20 same-lineage FENs a new blind sample.
- **Do NOT promote** the existing prospective 7/8 cohort or human learning efficacy.
- **No GitHub-Actions[bot] commits** or unauthorized data overwrite. Source owner WhoSia. GitHub docs preserve methods; Drive sealed results preserve original bytes; Notion records decisions.

## Implementation gates and review cadence

1. Baseline engine SHA, exact input FENs/history, instrumentation patch and regression suite frozen. If logger perturbs search, investigate and do not proceed to TT intervention claims.
2. Sham/targeted/no-store TT arms execute with full native receipts, assertions for search legality, event identity, actual work and source code SHA. If actual event correlation cannot be followed to a parent and root, mark transmission **HOLD**.
3. Independent new cohort preregistered BEFORE outcome search, then confirmation; publish all null results and between-position uncertainty.
4. Only after confirmed causal bridge, connect independent opponent-response plan values and tested explanation quality. Product learners need an ethically appropriate blinded comprehension study, separate from native mechanism.

**Immediate next action:** implement S4-A with a small source-diff-controlled TT event logger and non-interference test on a frozen developer subset; no more broad exploratory method code until that gate is decided.

## Verification pointers

- [C3X 0.30 master](C3X_030_MECHANISTIC_STRATEGY_RECONSTRUCTION_MASTER_20261110.md)
- [Current P11/S1–S3 actual evidence](C3X_030_P11S1_S2_S3_NATIVE_STATE_RESET_WASHOUT_ORIGINAL_AUDIT_20261111.md)
- [Product scope and existing functionality](../product/README.md)

**Missing original-paper status:** unchanged from the preceding inventory: Björnsson 2024 ICGA survey; Bratko & Kopec 1982 original chapter; Gadwal et al. 1993 chess tutoring journal; Herbeck & Barth 1996 ICCA; Demura & Kaneko 2024 ICGA. None of these were acquired in this decision turn.
