# C3X 0.22-P2-R1 — Source-Matched Root Survivors, Actually-Used TT Values & Legal-Recapture Falsification

**RESEARCH CLOSED (P2-R1 PILOT) · 2026-10-10 · ACTIVE C3X 0.22**  
Official paragraph title: **Path-Dependent Candidate Emergence & Search-State Causal Transmission: Source-Matched Root Survivor Histories, TT Value-Use/Cutoff Rivalry, SEE–Recapture Microstructure Interventions & New-Ecology Exact-Move Forecasts**.

## Executive scientific decision

Stockfish16's actual cached TT values causally mediate real memory-consumption interventions in an independent tournament-chess source. But **M2**, a preregistered exact-UCI predictor combining the depth-11 surviving root leader with improved legal same-square capture–recapture exposure, **fails** in fresh heldout TWIC1664. Its literal exact-UCI accuracy is the trivial no-change model's 54/64; neither anticipates any of 10 real final bestmove switches. The source exact writer/reader and real value-use/cutoff witness infrastructure passes. The specific hypothesis that SEE-like destination-exchange risk identifies root-candidate promotion **does not** pass.

## Evidence-chain audit

1. [P2-R1 pre-source pre-native registration](c3x-022-P2-R1-path-dependent-root-survival-TT-value-SEE-newTWIC-precommit.md). New TWIC #1664 (2026-09-28) chosen before any native result; earlier TWIC #1656/April/March/J2/K4 FENs excluded. The Week in Chess says **personal use only / all rights reserved**; no source game PGN/ZIP is redistributed in GitHub.
2. [Independent source-only freeze CI #38050910527](https://github.com/WhoSia/C3X/actions/runs/38050910527) SUCCESS: 687 games scanned; 16 distinct chosen; **637 legal root moves**. Exactly six successive legal same-square capture/recapture plies plus stand-pat, attacker legality including pins; source SHA `3cc4c788eec55960921e653604b2fbb3113163862e2652271b939fb12fb9eeb3`, legal action tree SHA `321f3af0ea90625929d639142ec8f930eacee5a7c6e7d856235267bb7f908423`. Original TWIC ZIP checksum `87bcd88e628c85b6e7e5b36894738fc9e6ef4012345740e57ff05795a908940f`.
3. [Native baseline-only Stage A CI #38051283450](https://github.com/WhoSia/C3X/actions/runs/38051283450) SUCCESS: 16 cold O/F worlds, 64 source-eligible TT FIRST reader pair cells, 4/16 O/F baseline disagreement games, no suppression, 12-depth root leader extracted. Literal **192 exact UCI predictions** for three models (M0/M1/M2) SHA frozen `a84a9a2b38bacedb140724c08fc5137b98c8f0077d4754bb5f399a3c30284c35` and [committed in Git](../forecasts/c3x-022-P2-R1-TWIC1664-16game-M0-M1-M2-exact-UCI-preTT-git-seal-20261010.json) at commit `f83107e5bde70829d35fa574fb6b34ceb45a94fd` BEFORE ANY new FIRST intervention. Earlier scout run #38051055407 failed on 2,048 TT discovery-event prefix cap; fixed only technical triage so witnessed earliest source pair remains eligible, no-pair at hard cap is an explicit HOLD, never a negative case. Final all64 eligible, zero HOLD.
4. [Native source-level Stage B CI #38051511354](https://github.com/WhoSia/C3X/actions/runs/38051511354) **SUCCESS**: exact original SF16 git `68e1e9b3811e16cad014b590d7443b9063b3eb52`; Threads1, Hash16MB, NNUE off, depth12; repeated cold baseline/watched FIRST/ZERO/decoy; independently source-selected physical **full64 key, slot, epoch, root call and native candidate**; 64/64 real FIRST source reader suppressions.
5. [Canonical native results and all SHAs](../receipts/c3x-022-P2-R1-twic1664-native-valueuse-SEE-depthsurvivor-20261010.json). Stage B ZIP SHA `9f12666933e7c550719051fcd8c8a6db413044617959d67da84d0c678987f190`, native JSON `04cba55434db7b477f67f2d5cf08716e146d5c0c74f85115f5f87c4f8c28cabb`; **24/24 artifact member SHA PASS**.

## Predictions, exact 64 delivered physical TT consumer cases

| Precommitted model | Literal UCI correct | Positive flip TP/FP/FN/TN | Exact move correct among real flips | Scientific verdict |
|---|---:|---|---:|---|
| **M0** same-order baseline does not change | 54/64 | 0/0/10/54 | 0/10 | Majority reference |
| **M1** other-root-order restoration, previously TWIC1656 FAIL | 46/64 | 6/10/4/44 | 2/10 | Still worse than M0 |
| **M2** depth11 candidate + strictly lower legal recapture-risk | **54/64** | 0/0/10/54 | **0/10** | **FAIL: no improvement over M0** |

Actual categorical bestmove changed **10 role cells** in just **5 distinct games: #2, #3, #6, #12, #13**. STRICT/BROAD within each game are *not* independent observations and some share identical physical writers. Exactly **6 distinct physical source episodes** underlie the ten affected role cells when preserving original root calls and keys. Role-cell numerators are instrumentation coverage, not 64 independent scientific replications.

**Important reason M2 failed at the prediction stage**: only three of the **32 O/F game-world baselines** had depth11 native leader different from depth12 final move: TWIC #2-F (`e4e5` vs final `e2f3`), #5-F (`f1c1` vs `f1d1`), #6-O (`f6d7` vs `f8e8`). In **all three** the six-capture SEE-like destination risk for candidate and incumbent was **0**, so the frozen strict-less-than decision rule precommitted 0/64 flips. Following Stage B, **10 real flips** disconfirmed its ability to identify positive effects. The failed rule must not be retrained on #1664 and called prospective success.

## Verified native mechanism: actual TT value use, separate from cutoff

At the exact selected FIRST physical writer/reader identity, passive baseline native source watcher recorded **64 actual TT value-as-evaluation uses**: **51 main-search** and **13 quiescence-search**. Upon source-matched FIRST reader suppression it recorded **0** such uses at those watched events; controls preserved full UCI and actual source reader block was logged 64/64. These observations are stronger than raw TT hit/probe counts: they report actual source assignment, then targeted suppression.

However, **no target-specific `main_cutoff` or `qsearch_cutoff` witness** was observed in these selected 64 native uses. Do not claim the intervention propagated via a cached-score TT early-cutoff. In this experiment the directly observed native operator is **TT value used as an evaluation source (`eval=ttValue`)**. The source code can contain other TT cutoffs elsewhere, but they are not a proven mediator of this selected first-reader contrast.

This distinction matters: Stockfish can use the same TT as a move-ordering hint, score evaluation source, alpha-beta return cutoff or source of later search-history modification; recording the writer and reader alone does not identify the last causal branch. The exact watched native `used` events and controlled `reader_block` narrow the operator identity.

## First source-aligned root return and full depth-history counterexamples

Of the ten role cells with actual move switch, **eight** first aligned nonfirst child returns differed while **remaining on the same side of alpha**, recorded `SAME_GATE`. Two were on the first candidate; the nonfirst alpha eligibility predicate does not apply. None of the ten initially observed first comparable child-return differences required an immediate nonfirst alpha gate crossing. This does **not** mean downstream alpha windows and hidden memory cannot transmit effects later.

- **#2 natural O:** `e4e5 → a1a7`, changed root leader **depth12 only**. Initial aligned nonfirst return `-99→-97` at alpha `-97` (both `value>alpha` false).
- **#3 played-first F:** `e1g1 → a1d4`, leader changes at **depths6–12**. Early aligned child difference `-209→-104` at alpha211, same gate.
- **#6 natural O:** `f8e8 → f6h5`, STRICT leader changes depths9–12; BROAD depths7–12. These roles differ in earliest observed root path but agree in final move, requiring episode-specific evidence.
- **#12 natural O:** `d3d4 → e2e3`, leader changes depths6,7,8,10,12; first aligned return on candidate index1 (separate semantic class, not an alpha nonfirst gate).
- **#13 played-first F:** `d7f6 → a5c6`, leader changes depths6,7,9,11,12; first aligned return same alpha gate.

**Causal limitation**: root leader divergence is an observed descendant of a source intervention, not a uniquely isolated mediator. At the first path divergence, continued indexing is not an identity-preserving pairing of search calls.

## Chess-primitive interpretation and future falsification

The new **637 × legal-root** chess action table comprises piece-to-square attacks, pin legality and same-destination exchange-tree gain. This is a deep chess relational signature, not a named "pin/skewer" frequency chart. It is more constrained than full Stockfish `Position::see_ge`: up to six legal same-square exchanges and optional stand pat, without engine-specific pruning thresholds, non-capture threats, tempo or broader evaluation. A zero exposure to immediate legal recapture does **not** mean the move is positionally safe or that no exchange can arise later.

In current source results, six-ply static recapture risk is **not discriminative** at the critical StageA depth11/12 candidate comparisons. This is a negative result for the proposed bridge, not evidence that the real engine ignores exchanges.

### Recommended P2-R2 research gate

**C3X 0.22-P2-R2 — Operator-Level Search-Memory Mediation & Exchange-Legality Counterfactuals: Targeted Native `see_ge` Witnesses, Actual TT Score Assignment versus Cutoff, Source-Aligned Candidate Survival & Precommitted Multi-Ecology Bestmove Transfer**

1. Pin exact native `Position::see_ge(Move, threshold)` invocations to root candidate/source epoch and log actual return, caller/threshold and legally contributing capture sequence (where available) without fabricating internal SEE traces.
2. On **development-only** #1656 and #1664 effects, run guarded site-specific parameter/control counterfactuals and 2×2 TT vs SEE intervention factorial; reject effects with wrong source contact or changed legality.
3. Define prospectively one or more *genuinely positive* flip/exact-move forecasts on a **fourth, unseen ecology/issue**, frozen source/hypothesis BEFORE any new FIRST arm, and retain NO_TREATMENT/technical HOLD.
4. Report game-clustered uncertainty and legal right to release the data; TWIC original PGN private pending permission.

**No paper submitted or accepted.** The methodology and its falsification are defensible pilot results; a general chess choice law or SEE-specific mediation theorem has not been proved. Older F19.5/K4/J2–J4/PAG/CPP224 negative records remain unchanged.
