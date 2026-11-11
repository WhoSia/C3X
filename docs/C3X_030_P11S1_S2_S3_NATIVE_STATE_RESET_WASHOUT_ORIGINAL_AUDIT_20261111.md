# C3X 0.30/P11-S1–S3 — Physical UCI Clear Hash Reset, Reversible Bestmove Changes and Original SHA Cross-Audit

**Date:** 2026-11-11 KST. **C3X chat number remains 32**, scientific/software version **C3X 0.30**. This research cycle is P11/S1–S3 following P11's 360-run observational comparison, not a new historically numbered P12 milestone. Historical C3X 0.27 Game14 and 0.29 same-world source event→ancestor→root→future response-robust plan causal validation **HOLD**, prospective 7/8 eligible games **HOLD**.

## 1. Precise research question and predeclared constraints

P11 earlier showed that full-strength Stockfish16 using `Skill Level=20`, `UCI_LimitStrength=false`, `Use NNUE=false` can pick different bestmoves after repeated searches when the engine state is retained. Does a physical **UCI `Clear Hash` button** suppress the observed choice switching, and does the choice shift return when repeated searching resumes?

All experiments here **reuse P11's exact known 20 FENs from four related opening lineages** (Ruy Lopez, Queen's Gambit, Sicilian Najdorf, English; each at plies 4/6/8/10/12); they are DEVELOPMENT analyses of already-discovered phenomenon, NOT new independent confirmatory cohorts. Request `12000` nodes per native search; actual recorded native nodes may vary. Exact unmodified Stockfish16 source `68e1e9b3811e16cad014b590d7443b9063b3eb52`, Ubuntu24.04 compiled native, `Threads=1`, `Hash=16MiB`, classical evaluation NNUE disabled and full strength. Python chess `chess==1.11.2`, each trial checks legal bestmove, native depth/nodes.

## 2. S1 actual four-arm experiment — 480 REAL native searches, 5,766,578 nodes

[Exact source](../harness/c3x_030_p11s1_search_state_ablation.py) · [five synthetic tests](../harness/test_c3x_030_p11s1_search_state_ablation.py) · [**REAL NATIVE CI SUCCESS #42964938042**](https://github.com/WhoSia/C3X/actions/runs/42964938042).

Four conditions per position, six repeated queries each:
- `cold_fresh_process`: new Stockfish OS process per search
- `same_game_retained`: same process and same game token, persistent engine search state and TT
- `same_game_clear_hash`: same process and same game token, `setoption name Clear Hash` before every search
- `same_process_new_game`: same process, new python-chess game token for every search, prompting UCI `ucinewgame`

| Full-strength mode | 20 positions with **within-arm switching** | Individual bestmoves different from cold reference /120 | Original actual native nodes |
| --- | ---: | ---: | ---: |
| cold fresh process | 0 | 0 | **1,441,698** |
| same game, retain search state | **13** | **44** | **1,441,484** |
| same game, direct UCI Clear Hash | **0** | **0** | **1,441,698** |
| same process, new UCI game each query | **0** | **0** | **1,441,698** |

**Crucial outcome:** All 120 Clear Hash trials reproduced the cold-reference moves, and **total measured native nodes were exactly the same** as all cold trials (and all newgame trials). The same-process non-cleared arm switches in 13/20 positions. This is a **strong interface-level reset sensitivity observation**, not yet proof that a single identifiable TT entry caused a root decision.

Original S1 JSON byte SHA256 `ff12daccfef85fa66ba0c32cf3b2cf00717328b2ef8cdf5a6e389b86e41e521c`. Original S1 CI ZIP byte digest SHA256 `97a0d6196797da95cfaff94c089b6c360653cb1b1d70ce5199eb845c439ba3c2`.
[Source raw ZIP sealed at Drive 04_SEALED_RESULTS_COURTS](https://drive.google.com/file/d/1BEQgIQJg-fYsmb_698ZgIo1XUT7Efeb5/view).

## 3. S2 direct within-one-process reversible washout — 140 REAL searches, 1,681,865 nodes

[S2 original source](../harness/c3x_030_p11s2_reversible_hash_washout.py) · [four synthetic tests](../harness/test_c3x_030_p11s2_reversible_hash_washout.py) · [**REAL NATIVE CI SUCCESS #42965327961**](https://github.com/WhoSia/C3X/actions/runs/42965327961).

For each of 20 previously seen FENs the **same Stockfish process and same game token** ran exactly seven searches: `baseline → warm1 → warm2 → ClearHash/search → warm-after-clear1 → ClearHash/search → warm-after-clear2`. A `Clear Hash` native UCI button was pressed **before both reset phases**. No new engine process within each FEN, no newgame tokens, same fixed node cap.

| S2 outcome /20 related chess FENs | Observed count |
| --- | ---: |
| First warm search differs from baseline | **8/20** |
| Second consecutive warm search differs | **9/20** |
| First Clear Hash immediately restores baseline bestmove | **20/20** |
| Second Clear Hash immediately restores baseline bestmove | **20/20** |
| Both reset phases restore baseline in same FEN | **20/20** |
| First search after reset1 **without** another reset differs | **8/20** |
| First search after reset2 **without** another reset differs | **8/20** |
| At least one unreset warm phase differs from baseline | **10/20** |

**Additional exact measurement:** for all 20 FENs, native nodes at `baseline`, `clear1`, `clear2` were identical, and baseline source move and native node count matched the cold reference first search in S1. This is unusually strong repeatability under UCI reset but can be specific to this engine revision/platform/board set and exact fixed-budget protocol.

Raw S2 JSON SHA256 `582cf020c9fc276690ada7044886cb5726f0093f8ab1644dbdc8560b390afe5b`, original S2 ZIP SHA256 `11eb8682b31528a1c6f101fc7f1871b409161c51c0a3376bb7aaadb081b60792`.
[S2 native original ZIP sealed in Drive 04_SEALED_RESULTS_COURTS](https://drive.google.com/file/d/1HMmWK6qbZ6OMPEskIszkeF0gPhagpt7P/view).

## 4. S3 two-original, cross-world SHA-locked reanalysis — ZERO further engine runs

[Cross-verified source](../harness/c3x_030_p11s3_dual_original_audit.py), [four fail-closed synthetic tests](../harness/test_c3x_030_p11s3_dual_original_audit.py), [**ACTUAL READ-ONLY CI SUCCESS #42965845034**](https://github.com/WhoSia/C3X/actions/runs/42965845034).

The workflow downloads the original immutable GitHub action artifacts from S1 #42964938042 and S2 #42965327961; finds exactly **one JSON** in each matching raw SHA; recomputes all 20 original FEN + source history identities, exact Stockfish binary hash, native nodes, move count summaries, S2 baseline and two reset restorations, and cross-checks S2 baseline node identity with S1 first cold trial. **No native engine launches in S3.**

Source audit initially [#42965730706 FAILED](https://github.com/WhoSia/C3X/actions/runs/42965730706) due an audit field naming mismatch `postclear_warm1` vs original `after_clear1_warm`. Intermediate [#42965816325 FAILED](https://github.com/WhoSia/C3X/actions/runs/42965816325) before its synthetic fixtures were updated. These failures did NOT change original S1/S2 raw results or relax gate requirements. The corrected S3 [#42965845034 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42965845034) and independently attested exact source summary match.

P11/S3 audit JSON SHA256 `82d75d3958436a69cf59207c095a2ea005488dde0cbbe5ea01d9de1eb62f6474`; audit ZIP SHA256 `c5bcc121b2c990e6797c1676e590c3d588fe500c49d8bc6178724e0c515cb418`; [S3 SHA-locked read-only report ZIP Drive seal](https://drive.google.com/file/d/1o0TiAQKtq6sgswGoUxnwgttzZyl4HI1g/view). Sum of **new actual native searches this cycle** = S1 480 + S2 140 = **620**, S3 adds **0**, cumulative actual nodes **7,448,443**. P11 earlier 360 searches and P11R earlier 0 are separate historical runs, not included in this current-cycle total.

## 5. Mechanistic interpretation and unresolved research gates

The P11 discovery was robustly narrowed: **retaining search state** is associated with repeated root choice changes; the physical UCI `Clear Hash` command **suppresses those changes**, including exact baseline node counts, and they can reappear after new search state accumulates. Even the separate `ucinewgame` condition gives matching cold results. This is evidence for reset-sensitive engine-memory mediation at the UCI/control level, **not** yet for a uniquely identified TT cell/cutoff event transmitting through child→parent→root.

**Distinguish physical intervention layers:**
1. `Clear Hash` is a real UCI command, not random sampling and not just an observational correlation. But engine-side effects besides TT invalidation may exist; we have not inspected actual TT occupancy/cell provenance for every relevant root.
2. `ucinewgame` may reset more state than `Clear Hash`; full reset equality does not prove these two commands have identical internal effects.
3. Fixed *requested* 12,000 nodes and equal actual native totals for reset arms are strong controls but do not equate all internal search traversals, timing, branch order or CPU performance.
4. Four opening families share position ancestry. The 20 boards and multiple repeated searches are not 20 fully independent game cohorts; no inference of a population 65% "randomness" rate or confidence interval under false independence.
5. Reusing the *same* 20 previously observed P11 boards makes this a **developmental mechanism test**, not an independent replication. No new unseen heldout chess cohort was used.

### Next gate — propose a genuine SOURCE-SITE intervention

For a specific sealed P11/S2 FEN, instrument TT probe/hit and root search node ancestry at original Stockfish16 commit. Compare controlled **no store / probe disabled / one targeted TT slot masked / original** native builds; keep same game context and freeze every actual search receipt with source diff hash, node count and parent/root propagation. This could establish a particular physical causal path, but **has not been executed**. Independently precommit unseen FEN/game cohort before claiming general mechanistic explanation.

Separately, Guid et al. 2013 and Seidel 1994 show that a chess tutoring product requires **verified chess domain knowledge, student model and generated explanation**, not just robust search-state instrumentation; educational effect requires actual blind learner tests.

## 6. New primary PDF custody and truly missing papers

This cycle newly supplied original PDFs were first-page/full-text verified, canonically renamed and moved in place `00_INTAKE→10_PAPERS`, preserving Drive IDs/bytes:
- **Seidel (1994), *Self-Annotating Elementary Endgames*, ICCA Journal 17(2) 51–62**, [primary source owned](https://drive.google.com/file/d/1Flmaxk6sVOeeW7LhQ0ZBjnuChvqmXHGb/view). KRK, KBBK operational self-annotating chess endgames with potential tutorial feedback, relevant to product P6.
- **Delling, Pajor & Werneck (2015), *Round-Based Public Transit Routing*, Transportation Science 49(3)** [original](https://drive.google.com/file/d/1tlD0XjABxbOygx8gLzJ203BR4ab_vKrB/view), unrelated transit algorithm paper.
- **Bast et al. (2010), *Fast Routing in Very Large Public Transportation Networks Using Transfer Patterns*, ESA 2010** [original](https://drive.google.com/file/d/1X5InPCt1jkaE_bm-eCPW1JL76WrZ7BD0/view), unrelated transit algorithm paper.
- **전인우·남현우·전철민 (2018), *환승 저항을 고려한 운행시간표 기반 대중교통 다중 경로 탐색 알고리즘*, 한국ITS학회논문지 17(3) 72–86** [original](https://drive.google.com/file/d/1fLW0PHlgmL0Tf-fgX50IEphsaESrPWcL/view), transit algorithm.
- **권영우 (2020), *한국사회에서 대학은 기업인가 취업학원인가?*, 철학연구 제153집** [original](https://drive.google.com/file/d/1JJJqIaTTStqdVLsqj7t79RXl7cT8dNX3/view), philosophy of higher education, NOT C3X experimental evidence.

**Existing 10_PAPERS audit remains incomplete:** The earlier first-1000-file naming check and historical unreadable/duplicate source HOLDs remain; no unfounded claim of an exhaustive catalogue.

### Only still genuinely unheld exact primary works (Drive original identity search, not proof of all-folder absence)

| Rank | Missing exact work | Access |
| --- | --- | --- |
| 1 | Björnsson (2024), *Chess and Explainable AI*, ICGA DOI 10.3233/ICG-240256 | Publisher restricted, legal author/manuscript/library |
| 2 | Bratko & Kopec (1982), *The Bratko-Kopec Experiment*, book chapter DOI 10.1016/B978-0-08-026898-9.50009-7 | Original chapter restricted; updated Computer Chess Digest owned is not original |
| 3 | Gadwal, Greer & McCalla (1993), *Tutoring Bishop-Pawn Endgames*, Applied Intelligence DOI 10.1007/BF00871938 | Author copy or institutional library; owned UMRAO1991 not equivalent |
| 4 | Herbeck & Barth (1996), *An Explanation Tool for Chess Endgames Based on Rules*, ICCA 19(2), 75–82 | Restricted exact publisher |
| 5 | Demura & Kaneko (2024), *Initial State Diversification for Efficient AlphaZero-style Training*, ICGA DOI 10.3233/ICG-240255 | Final restricted; 2023 Japanese predecessor is distinct |

**Seidel 1994 now owned**, thus removed from missing list; Guid2013 also owned from prior turn. No bought/pirated/restricted source access claimed.
