# C3X 0.29-P36/R4 — Actual Near-Pair Search-Budget Stability Court (Pre-Outcome)

**2026-11-05 KST.** **PREREGISTERED BEFORE examining any 48k or 96k Stockfish output.** This is a follow-on, outcome-aware exploratory test of the *already observed 24k* March8 candidate screen, not independent confirmatory near-tie discovery.

## Authentic prior evidence and corrections

P36/R2 [engine-blind source freeze CI 41957706609](https://github.com/WhoSia/C3X/actions/runs/41957706609) SUCCESS: official March2026 Lichess broadcast source SHA `1a5ad83fc9f440dcdadde17b11cc81a953f4895aaf8b8588470b3078209dc7fc`, eight game identities frozen from first 1000 eligible cases without engine. [Drive byte-sealed original archive](https://drive.google.com/file/d/11szqoVSHKTeIaajHjxVgn9MoxVhUDBKY/view) ZIP SHA `c2d5a646f62af3a07a3efd3bc642eccfafb5440845c8e843ebb9ef3c4e325b4a`, independently re-downloaded and verified same. Source was **previously owned by C3X in October 2026**, not a newly acquired month.

R3 [original SF16 native joint MultiPV2 CI 41959284647](https://github.com/WhoSia/C3X/actions/runs/41959284647) SUCCESS: eight fixed full-history boards, 24k requested nodes each, original `Stockfish16` git `68e1e9b3811e16cad014b590d7443b9063b3eb52`, NNUE SHA `5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b`; canonical eight-row result JSON SHA `5ce8ec253c95075cbba3a1b273236886756968778259363f1f1214fdb1c12d3f`. Nominal 24k results: **near 2** (9cp, 10cp), **intermediate 4**, **wide 1** (576cp), **native PV1 rank/score discordant 1** (PV1 77cp < PV2 93cp). The initial code deliberately failed on the rank inversion; new code preserves same native PV labels and flags `rank_unresolved` instead of sorting outcomes ex post. Both near PV1s were marked **upperbound=true**, so these are provisional search margins and should not be treated as certified move values.

**New historical-exposure audit (actual old March source recovered and compared):** C3X 0.20-C2 original 16-game March game-selection archive [native source-only CI 38038059013](https://github.com/WhoSia/C3X/actions/runs/38038059013), original ZIP SHA `6ff7873dc51d925cbf6b9c96781c0500879c343512beef208a37bc71cf3022e8` contains one full-game UCI identity shared with P36/R2: case `00f04cd20636fdc2` index 368, old selected game ID12, old root ply34 vs our ply30. Full game SHA `6eed60605065179e845cc00c29e3fbf378d9befbfff9b5ff3c1b891eb139606b`. **1/8 contaminated at full-game unit**, despite zero exact four-field FEN overlap. This is EXACTLY why FEN-only disjointness is scientifically inadequate; do not count it as external replication. Original C3X 0.18 16 game identities had zero overlap, but full older 0.28 cohort and other histories still await audit. Four of eight P36 games come from the same American Cup Blitz event.

**Old July warning:** C3X M6 already executed 64 games on a July2026 broadcast cohort; P36/R1 July official SHA mismatch also failed, do not reuse July as independent.

## Predeclared P36/R4 exact native falsifier

Test all **eight** P36-R2 frozen games, not just the two selected near pairs. On each case, repeat original-source whole-history SF16 NNUE MultiPV2 `Threads=1, Hash=16, Use NNUE=true` at **48,000 and 96,000 requested nodes**, separate fresh engine process per board/budget, same pinned SF16 code/net and evaluator route. Preserve both candidates (UCI/SAN optional), raw side-to-move scores, `lowerbound`/`upperbound`, PV and legal first opponent reply. Never silently reorder PV1/PV2.

For each previously nominal near case (IDs `00470a57672750d1` and `01af9df4f5e8e39f`), predefine **strict stability** across both higher budgets as all:
1. Exactly the same unordered **two candidate UCIs** as 24k.
2. The same winner UCI as original PV1 at 48k and 96k, and no native score-order discordance.
3. The positive absolute margin remains <20cp at both depths/budgets.
4. The 96k primary PV has neither upper nor lower score-bound flag; if it does, `CERTIFICATION_HOLD` rather than declare true value superiority.

Any failure of (1)-(3) => `REJECTED_AS_BUDGET_STABLE_NEAR_CASE` for this fixed design, not proof of universally inferior chess strategy. (4) is an epistemic authority check; no bound-free score at finite depth certifies true minimax value. Report full roots for all eight, including known full-game-overlap case as contamination-marked descriptive control.

This is **not** an explanation-improvement experiment. If near cases fail stability or are bound-limited, avoid promoting them as strong-move justification examples. Find a strictly matched compute and number-of-claims forecast comparison on new source, with `Stockfish+PV` and simple foil-aware plan JSON as serious baselines. Do not expand network-instrumentation work.

**Governance:** GitHub user `WhoSia` only for commits; GitHub Actions contents:read and artifact uploads, never github-actions[bot] commits/merges/pushes/tags/ref-moves; original raw source stays preserved in Drive and Notion conclusions stay separate from artifacts.
