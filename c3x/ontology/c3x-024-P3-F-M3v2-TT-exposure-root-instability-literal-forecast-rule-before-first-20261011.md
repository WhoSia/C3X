# C3X 0.24-P3-F — Literal M3-v2 Decision Rule: TT-Exposed Root Instability (PRE-FIRST)

**Status: MODEL RULE GIT-FROZEN BEFORE ANY 2025-09 TT FIRST / SEE source intervention.** Sept2025 source-only cohort has 128 independently selected games and SHA `ee8265f96b055645428f2fa87b36647e1931c86c848db5725a8b0ec63596dacb`, human Git-literal source ID registry `c3x/forecasts/c3x-024-P3-Sept2025-128game-source-SHA-literal-preNative-Git-seal-20261011.json`. Native untreated StageA permitted; **NO treated outcome** may be consumed by rule authoring or literal UCI forecaster. Historical May 2 and August 16 are development-exposed; M3-v1 failed to outperform M0 (58/64 identical predictions).

## Predictand and pre-treatment features

For every pre-eligible September game `g`, root order `o∈{O,F}` and physical TT first-reader role `r∈{STRICT,BROAD}`, output the **exact UCI string** of root move after one physical TT FIRST reader suppression, at pinned Stockfish16 Threads1 Hash16, NNUE OFF, depth12, source-identical. No SEE boolean toggle in the P3-FIRST trial. An ineligible role must be recorded `NO_PREDICTION` but counted in game-level eligibility/censor reporting.

Allowed source-pre-first inputs: pristine SHA-selected legal board and played legal root move; untreated original O/F depth12 bestmove UCI, untreated depth11 native leader, passive original per-role first reader `physical` tuple, `root_candidate_native`, `source_root_call`, 32-event SEE prefix and censoring flag, native pre-intervention TT use witness. No outcomes after FIRST or SEE FLIP.

## Models — deterministic and mutually comparable

- **M0:** untreated same-order depth12 exact UCI. Null assumes no FIRST change.
- **M1 (historic FAIL):** untreated opposite-order depth12 exact UCI (if identical this equals M0).
- **M2-depth11 (historic FAIL):** same-order untouched depth11 native root leader mapped to legal UCI; if unavailable `NO_PREDICTION`.
- **M3-v1 historical rule:** only if STRICT role, untreated O/F depth12 winners disagree, first physical reader native root candidate equals same-order depth12 winner, and non-censored SAME root-call original passive SEE witness, choose opposite-order depth12 winner; otherwise M0. This is the frozen August formulation transplanted *without changing its logic*.
- **M3-v2 (new)**: eligible role *and* `STRICT` *and* `root_candidate_native` equals same-order untreated depth12 winner (using exact native Stockfish move encoding). If O/F depth12 winners differ, predict opposite-order depth12 winner. Else if same-order depth11 leader exists, is a legal UCI and differs from same-order depth12 winner, predict depth11 leader. Otherwise predict M0. **All role= BROAD predictions are M0.** Both possible positive triggers use ONLY untreated original source: root-order instability first, then depth instability. Do not invent a move if the alternate candidate is illegal or missing; fail closed. The passive SEE prefix and TT value use count must be recorded as **stratification features, not posthoc inclusion criteria**.

This model is an intervention-susceptibility heuristic, **not** natural `TT→SEE` mediation and **not** an independently verified causal explanation. The rule is intentionally more sensitive than over-constrained M3-v1 and may perform worse than M0. Nonzero predicted flips is necessary but not sufficient for success. Never switch to a more flattering fallback after seeing results.

## Freeze / evaluation contract

1. Complete source-only SHA and human Git-literal 128 game hashes *before untreated StageA*; StageA must report zero TT FIRST/SEE changes.
2. Generate and validate **all 512 role-cell exact UCI strings for M0/M1/M2/M3v1/M3v2**, with exact source and untouched StageA SHA. Publish masked source-derived literal forecasts only after BY-SA review. Human Git commit the exact ordered 128-game×4-role table and full JSON SHA **BEFORE** any September TT FIRST native treatment.
3. After literal Git seal, run paired cold original vs FIRST for every predeclared eligible role and report actual physical writer-reader proof, per-game 4-cell counts, exact-UCI scores M0 and M3-v2 and historical rivals, prediction positives and negative controls. 128 independent game clusters, up to 512 nonindependent role cells. Missing physical source contact remains denominated `NO_CONTACT`, not treated as move-unaffected.
4. Declare predictive advantage only if game-level gain over M0 on previously unexposed September source is demonstrated with uncertainty. If M3-v2 == M0 everywhere or ties/fails, explicitly record NEGATIVE rather than designing a new model on the same cohort.

Governance: Stockfish16 git `68e1e9b3811e16cad014b590d7443b9063b3eb52`, read-only Actions `permissions: contents: read`, human WhoSia authors only, source-derived BY-SA licensing and rights gates, original complete PGNs and modified GPL binaries excluded.