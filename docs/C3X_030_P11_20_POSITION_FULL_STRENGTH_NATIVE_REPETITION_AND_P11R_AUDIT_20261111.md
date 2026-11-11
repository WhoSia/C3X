# C3X 0.30/P11 — Full-Strength Stockfish Repeatability: Predeclared 20-Position Native Cohort and Verified Post-hoc Audit

**Date:** 2026-11-11 KST. Conversation number **C3X 32**; software version remains **C3X 0.30**, continuing P10. Scientific decision: stable outputs are NOT guaranteed merely by disabling the intentional strength-handicap PRNG; actual search state and parallel execution matter. The original Game14 same-world search-event→ancestor→root-choice→plan-value causal chain is still **HOLD**, and the prospective cohort remains **7/8 HOLD**.

## 1. Research question and source constraint

After [P10](C3X_030_P10_STOCKFISH_RANDOMNESS_FACT_CHECK_48_NATIVE_SEARCHES_20261111.md) distinguished deliberate `Skill::pick_best` PRNG selection from ordinary alpha-beta search, this experiment asks:

> Among unweakened Stockfish16 searches at the same requested node limit, does reusing the search session or enabling parallel search change the selected move or the within-setting repeatability?

Unlike P10's 2 source positions, freeze **four distinct opening histories** *before seeing results*, with checkpoints at plies 4,6,8,10,12, giving 4 related groups ×5 =20 positions. No cherry-picking positions based on instability. This is **not** 20 independent games; 5 positions share each family. Exact source JSON has every FEN and UCI history.

The four source histories are Ruy Lopez, Queen's Gambit, Sicilian Najdorf and English. The first legal-historical test CI [#42944284069 FAILED](https://github.com/WhoSia/C3X/actions/runs/42944284069) because Ruy's white bishop after Bb5,a6 had mistakenly been written `f1a4` instead of correct `b5a4`. The UCI correction was committed **before the first successful native 360-search execution**; no positions removed or replaced after outcome inspection. Original failed test remains preserved. Six source unit tests pass in the successful run.

### Fixed native settings

- **Stockfish16 original source** `68e1e9b3811e16cad014b590d7443b9063b3eb52`, native compiled in ubuntu-24.04 CI (same engine provenance as P10). **Classical evaluation** `Use NNUE=false`, `Skill Level=20`, `UCI_LimitStrength=false`, `Hash=16 MiB`. No weak-skill `Skill::pick_best` PRNG path.
- Requested `Limit(nodes=12000)` for each play; actual nodes may differ (particularly four threads), and are measured explicitly.
- 3 arms: **cold_single** = fresh engine process for each trial, one thread; **warm_single** = reuse same engine process and same python-chess game object across six trials, one thread (retained TT and search state); **cold_parallel4** = fresh engine process each trial, four threads.
- Six independent search *calls* per position×arm. Total **20×3×6=360 actual native searches**, recorded by bestmove, depth, score, 12-ply PV prefix, actual nodes. The source does not assert all trials are statistically independent because shared opening ancestry and warm engine memory violate that assumption.

[Real native P11 runner](../harness/c3x_030_p11_repeatability_cohort.py) · [six synthetic/cohort-integrity tests](../harness/test_c3x_030_p11_repeatability_cohort.py) · [actual P11 native SUCCESS #42944315234](https://github.com/WhoSia/C3X/actions/runs/42944315234).

## 2. Actual results — 360 searches, 4,575,489 nodes

| Arm (unweakened full strength) | Positions switching within six repeats | Positions where ≥1 trial differs from cold-single reference | Individual trial disagreements vs cold-single reference (out of 120) | Total actual nodes |
| --- | ---: | ---: | ---: | ---: |
| cold_single | **0/20** | 0/20 | 0/120 | 1,441,698 |
| warm_single | **13/20** | **13/20** | **44/120** | 1,441,484 |
| cold_parallel4 | **13/20** | **14/20** | **65/120** | 1,692,307 |

**Why 13 ≠ 14 for the four-thread arm:** `sicilian_najdorf_ply4` cold single chose `c2c3` in all six repetitions, while four-thread chose `d2d4` in all six. Four-thread was internally **stable** on this one position but disagreed 6/6 with the cold-single reference. Within-arm variability is not the same as cross-arm difference.

Observed fraction of 20 positions that switched within identical setting: **0%, 65%, 65%**. This is a descriptive empirical fraction from four opening families, **NOT** a population proportion estimate nor an attributable "RNG usage rate." Reported mean position-level plug-in entropy (bits, six samples/position): cold 0, warm **0.6492025053613222**, parallel **0.8831527880375468**; sample entropy biased downward when 6 repeats. Do not compare its numerical value directly to a universal engine randomness threshold.

By related opening family, number of positions with within-arm switching (out of 5 each):
| Opening family | cold_single | warm_single | cold_parallel4 |
| --- | ---: | ---: | ---: |
| Ruy Lopez | 0 | 1 | 2 |
| Queen's Gambit | 0 | 4 | 4 |
| Sicilian Najdorf | 0 | 4 | 4 |
| English | 0 | 4 | 3 |

These are descriptive family strata only. In particular many warm single-thread trials changed selected moves even though `Skill Level=20` and `UCI_LimitStrength=false`. This demonstrates search-session state sensitivity, **not** evidence of explicit learned-RL-policy sampling.

### Source and immutable provenance

- Actual original JSON SHA256 `cd48b29832a4f2fdbb031c55c97f094510e17825c5dfc04592c4eabc135488b7`.
- Actual original P11 CI ZIP digest SHA256 `a299bf8b4141b9190ae3eeeab387f9a61f80576e4ae9d8876f33ab4d435d0cc2`.
- [Original raw P11 360-search ZIP, Drive sealed courts](https://drive.google.com/file/d/128OdEJxjqgdbhV-ANsJE9pRqj1SO0ryu/view). [GitHub original SUCCESS run](https://github.com/WhoSia/C3X/actions/runs/42944315234).

## 3. Independent source-locked P11R audit (zero new chess searches)

To prevent inflated interpretation, added [P11R pure-stdlib original-record auditor](../harness/c3x_030_p11_original_reanalysis.py) with [five synthetic tests](../harness/test_c3x_030_p11_original_reanalysis.py). [Genuine read-only original P11R CI #42944850765 SUCCESS](https://github.com/WhoSia/C3X/actions/runs/42944850765):

- Download original P11 artifact from historic run `42944315234` with **read-only GitHub token**; verify **exactly one JSON** with original SHA256 `cd48b298...`; never execute Stockfish in this post-hoc job.
- Recompute exact 6-trial move counts, native nodes, per-arm number of within-setting switches, reference mismatches and family distributions.
- Verify exact `20 positions×3 arms×6 trials`, full-strength settings, original source SHA, false claimed native causal intervention, all position FENs unique and source summaries untampered.
- Source output has strict **4 opening-family ancestry** warning and never equates within-arm switch events with cross-arm disagreement.
- Original P11R JSON SHA256 **`2f76f55cecffc7b5136d120e6eac6f5a0fc6267737ae0c79c73e7c2b5f2f7df1`**; P11R ZIP digest SHA256 **`8edeb0dd54f6de38e942f5a51fa8b093a8d7ae6d3c04482f89c4f1d2d630bce9`**.
- [P11R new independent audit artifact in Drive sealed courts](https://drive.google.com/file/d/17BFfdS5uB9hvOzCLSh-cthPDJLFzZ85U/view). Actual new native engines searched by P11R audit: **zero**.

## 4. Interpretation and methodological limitations

1. The source `Stockfish16` full-strength chess move selection is **not proven to be random sampling** simply because repeated warm or multithread searches produced different actions. `Skill Level20` explicitly disables handicapped PRNG; the original `value_draw` depends on executed node count, while TT and search ordering depend on history. More powerful tests are needed to isolate each.
2. **Warm** reuses not only transposition table information but other learned-within-search engine state and same-game protocol context. Therefore P11 **cannot uniquely attribute** observed 65% variation to the TT alone. A future `Clear Hash` intervention, separate game resets, and native controlled state counters are needed to identify the mechanism.
3. **Parallel4** actual native nodes exceeded requested budget far more often than one-thread. Hence arm differences conflate scheduling, search frontier and actual work. Need match actual nodes, ensure fixed hardware, record window size, PV changes and independent repeated runs, and optionally program the native search for exact reproducibility measurements.
4. Four paths are correlated; 20-position fractional switch rate is descriptive, not an independent FEN-population estimate. Need broaden precommitted cohort beyond openings, including near-tied candidates, late middlegames, endgames and position FEN/provenance SHA.
5. **Scientific main claim remains HOLD**: P11 does NOT prove native source search event→ancestor→root mediation, strategy persistence under opponent replies, human improvement or new NNUE explanations. The real contribution is establishing operating-system and search-state sensitivity as an observable and separately measurable experimental dimension.

## 5. Research decision and engineering follow-up

**Approved next P12 focused causal factorial**:
- Split warm arm into (A) same engine+same game+TT, (B) same engine+same game but explicitly `Clear Hash`, (C) same engine+`ucinewgame` separate game objects, (D) fresh process; lock single thread and match actual native search resources. This isolates major memory components better than P11, though may still leave history buffers.
- Add paired source events `value_draw(node-count parity)` and TT instrumentation, physical intervention with exact original source and compiler commit; causal native root effects separately recorded from general output variability.
- Use P11 original 20-position cohort for dev debugging only. For publishable results, create another **unseen preregistered** independent balanced cohort and validation criteria to prevent using the same observed outcomes as both discovery and confirmation.
- Reconcile explanation UI: show `stability measured under [engine, budget, thread mode, cache policy]` rather than conflating engine stochasticity with chess plan robustness.

## 6. Newly read archive and bibliography ownership

While executing P11, nine originally user-uploaded `00_INTAKE` PDFs were first-page/abstract verified, bibliographic file metadata renamed and moved in place with original IDs and bytes unchanged (8 unrelated computational theory/mathematics/toxicology primary papers plus 1 directly chess-tutor original):
- Ron & Rubinfeld (1995), *Learning Fallible Deterministic Finite Automata*, [Drive](https://drive.google.com/file/d/1Q2d8Lg6MqC1fF4vpBGWgPAACXB53WFGE/view).
- Angluin, Krikis, Sloan & Turán (1997), *Malicious Omissions and Errors in Answers to Membership Queries*, [Drive](https://drive.google.com/file/d/1L4QsPx5ULNZmQfJ8kbyhoYQD8y0MzpSN/view).
- Jefferson, Pfeiffer, Wilson & Waldecker (2021), *Permutation Group Algorithms Based on Directed Graphs*, [Drive](https://drive.google.com/file/d/1XX3n7aoQF_sGOg5QMsv8ufR5s1IFrJSA/view).
- Mereb & Vendramin (2024 arXiv v3), *Rubik's as Galois*, [Drive](https://drive.google.com/file/d/175mqiTNreeuGbT4-CBfxSuhYpItbkTQL/view).
- Zassenhaus (1982), *Rubik's Cube: A Toy, a Galois Tool, Group Theory for Everybody*, [Drive](https://drive.google.com/file/d/1i0gVO3XuLtBYZSknKCaMChTXJ641D59U/view).
- Knuth (1992 arXiv upload of manuscript dated 1991), *Efficient Representation of Perm Groups*, [Drive](https://drive.google.com/file/d/1Thzd-fEXGIME5BwpVxaqhuXmOgnL8rb_/view).
- Leon (1991), *Permutation Group Algorithms Based on Partitions I: Theory and Algorithms*, [Drive](https://drive.google.com/file/d/1cRJ8tyDVPYsDZb1-8zHkGudyPVmgClDA/view).
- Ingelman-Sundberg (2002), *Polymorphism of Cytochrome P450 and Xenobiotic Toxicity*, [Drive](https://drive.google.com/file/d/1qtGkUo5FWhfSe-OmTn4fRLtnX4b4eXN1/view).
- **Guid, Možina, Bohak, Sadikov & Bratko (2013), *Building an Intelligent Tutoring System for Chess Endgames*, CSEDU 2013, 263–266, DOI 10.5220/0004389102630266**, [original PDF in `10_PAPERS`](https://drive.google.com/file/d/1dhJfufJnv2sTDMHVMfkfCxrkr52h40fd/view). Five-component tutor (domain model, search, tutoring model, student model, UI); do not claim the architecture is a validated learner-effect outcome from this single paper.

**No standalone exact original PDF found in accessible Drive after this cycle**:
- Björnsson (2024) *Chess and Explainable AI*, ICGA DOI 10.3233/ICG-240256 — restricted publisher; author/institutional manuscript route.
- Kopec & Bratko (1982) *The Bratko-Kopec Experiment* original book chapter DOI 10.1016/B978-0-08-026898-9.50009-7 — restricted; historical *Computer Chess Digest* updated test is held but **not identical**.
- Demura & Kaneko (2024) *Initial State Diversification for Efficient AlphaZero-style Training*, ICGA DOI 10.3233/ICG-240255 — restricted; 2023 shogi predecessor is distinct.
- Gadwal et al. (1993) *Tutoring Bishop-Pawn Endgames*, Applied Intelligence DOI 10.1007/BF00871938 — not equivalent to owned Gadwal 1991 UMRAO.
- Herbeck & Barth (1996) *An Explanation Tool for Chess Endgames Based on Rules*, ICCA 19(2), 75–82 — restricted publisher.
- Seidel (1994) *Self-Annotating Elementary Endgames*, ICCA 17(2), 51–62 — restricted publisher.
**Guid et al. 2013 is now owned and deliberately excluded from the missing-only list.** Unreadable, duplicate and unrelated older `00_INTAKE` items remain HOLD rather than being silently deleted or moved.
