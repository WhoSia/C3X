# C3X 0.30/P10 — Does Stockfish Repeat a Move Because of RL Policy Sampling? Source-Level and Real Native Controlled Test

**Date**: 2026-11-11 KST; conversation C3X 32. **Version lineage**: C3X 0.30 continued; P9 prior literature audit inherited unmodified. **Evidence class**: original official Stockfish source and **48 real pinned Stockfish16 searches** on two legal chess positions in four experimental arms; 5 unit contract tests; original JSON/ZIP SHA custody. C3X 0.29 same-world computation→ancestor→native root→future-planning causality and 7/8 prospective cohort remain HOLD. No actual RL policy training or retraining performed.

## 1. User-supplied hypothesis and exact source audit

User relayed a peer's interpretation that (a) repeated Stockfish bestmove discrepancies are "just random", (b) RL training encourages random policy sampling, and (c) deployed engines may sample for diversity even when policy converged. These claims must be distinguished:
- **Generic RL policy exploration/sampling**: correct for some algorithms and deployment choices; not a description of ordinary Stockfish16 decision algorithm.
- **Stockfish16 full strength**: NNUE is an evaluation component, and principal move determination is alpha-beta search with iterative deepening, reductions/pruning, heuristics and transposition tables; it does not ordinarily softmax-sample a learned policy over moves.
- **Stockfish16 handicap mode**: **actual PRNG exists**. In pinned [original source search.cpp](https://github.com/official-stockfish/Stockfish/blob/68e1e9b3811e16cad014b590d7443b9063b3eb52/src/search.cpp), `Skill::pick_best()` defines `static PRNG rng(now())` and adds a randomized bias to suboptimal candidate root moves. `Skill::enabled()` tests level <20 or UCI_Elo conversion; when enabled the search expands to at least four MultiPV candidate roots. Source says PRNG sequence intended non-deterministic. Official [Stockfish FAQ](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html) confirms explicitly weakened selection.
- **Draw eval 'random' comment**: pinned `value_draw(const Thread*)` returns a slight perturbation based on **thread nodes & 0x2**, not a PRNG draw. It can be variable under differing actual searches, yet is conditionally deterministic given the node count. Earlier C3X 0.27 source intervention lineage must distinguish actual draw-score node-dependence from UCI handicap randomness.
- **Other variation causes**: finite depth/time/nodes, multi-thread scheduling and search state, TT hashing, opening books or external GUI configuration. The observation of differing chosen actions cannot alone identify stochastic policy sampling.

## 2. P10 actual implementation

[Runner](../harness/c3x_030_p10_stockfish_stochasticity.py) · [five unit tests](../harness/test_c3x_030_p10_stockfish_stochasticity.py) · [read-only native CI workflow](../.github/workflows/c3x-030-p10-real-repeatability.yml) · [real SUCCESS #42942762723](https://github.com/WhoSia/C3X/actions/runs/42942762723).

A previous original [#42942625851 FAILED](https://github.com/WhoSia/C3X/actions/runs/42942625851) after compiler and tests because `python-chess==1.11.2` automatically controls `MultiPV`, which user code attempted to configure explicitly. **Fix:** remove manually specified MultiPV (no relaxed test or narrowed scientific goal), commit `7b7f395`, rerun successfully. Failure history is intentionally preserved; GitHub-Actions[bot] has no source commits.

**Exact native build and experimental constraints**:
- Unmodified Stockfish16 original commit `68e1e9b3811e16cad014b590d7443b9063b3eb52`, `ARCH=x86-64` under ubuntu-24.04; source compiled in CI.
- Measured binary SHA256 `6458324545ef0f43b5a74de75c980e08413251247bba500d9befac113a43f325`.
- `Use NNUE=false` (classical evaluation), `Hash=16 MiB`, `UCI_LimitStrength=false`, `MultiPV=1` default (left under python-chess automatic control), `Nodes requested=15,000` per trial; **actual nodes can exceed 15,000 in parallel**.
- Both positions from fully legal UCI histories with FEN recorded: opening after `e4 e5 Nf3 Nc6 Bb5 a6`; middle game after `d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O Nf3 Nbd7`.
- 4 arms per position × 6 repeats each = **48 real native searches**. (A) full `Skill=20`, one thread fresh process each trial; (B) same full strength but one thread reused same engine/game object and warm TT; (C) full fresh four threads; (D) intentional weakened `Skill=0`, one thread fresh process.
- **Observational arm comparison with controls**, NOT a fully randomized causal mediation proof. Not all other hardware nondeterminism isolated. Code reads actual nodes/depth/move and PV; no host code writes into GitHub repository.

## 3. Real results of 48 executions

| Position | Arm | Distribution across 6 trials | Distinct moves | Actual nodes | Completion depth range |
| --- | --- | --- | ---: | ---: | --- |
| Opening | full fresh 1 thread | b5c6:6 | 1 | 90,042 | 10–10 |
| Opening | full warm 1 thread | b5c6:6 | 1 | 90,042 | 9–11 |
| Opening | full fresh 4 threads | b5c6:6 | 1 | 102,665 | 7–9 |
| Opening | intentional handicap skill0 1 thread | b5c4:1; b5c6:2; b5e2:2; b5f1:1 | 4 | 90,084 | 7–7 |
| Middlegame | full fresh 1 thread | c4d5:6 | 1 | 90,144 | 10–10 |
| Middlegame | full warm 1 thread | c4d5:6 | 1 | 90,107 | 10–11 |
| Middlegame | full fresh 4 threads | c4d5:6 | 1 | 120,575 | 7–8 |
| Middlegame | intentional handicap skill0 1 thread | f1d3:1; h2h3:2; h2h4:3 | 3 | 90,216 | 7–7 |

**Total** 763,875 native nodes. Full-strength chosen action stable across all tested repeats of these two positions. Deliberately weakened choices varied; plausible, expected, and backed by direct PRNG-in-source evidence. Do not infer full-strength determinism for *every* chess position or enough support to quantify true sources of stochasticity. Four-thread actual node overrun vs 15K cap is an important observed resource variable, not an instrumentation bug to hide.

**Evidence custody**:
- Original P10 JSON SHA256 `09c61de2c900fab16021f1f574ca101fb669f1dca4cae4fcf4baf51f90e39e14`.
- Original CI ZIP SHA256 `adc5dd1b468b12d9355078d05053375309b9fef3f4de98ca9582804a01c0d1c3`.
- [GitHub SUCCESS run](https://github.com/WhoSia/C3X/actions/runs/42942762723) and [original ZIP in Drive sealed courts](https://drive.google.com/file/d/1wk1kCYr6Hi7fNzvPfziK6XEDhhRHEtxm/view), same binary untouched.

## 4. Scientific decision and research plan

**Decision**: Keep four layers separate:
1. **Intentional sampling** in strength-limited Stockfish code (observed source route and real choice variation).
2. **Finite-resource search-state sensitivity**: time/depth/nodes/scheduling/hash state; original common engine source event paths may be deterministic given an exact state, but outputs may vary under execution state changes.
3. **True search-event mediation**: physical intervention in exact native computation `value_draw` / TT / ancestor node, trace to root selection, and independent planned response evaluation; historical Game14 limitations retained.
4. **Human pedagogical explanation**: verified chess facts and learner understanding must be assessed separately from any engine causal claim.

**Follow-up experiment contracts (not yet executed)**:
- Source-controlled paired one-thread vs four-thread crossover with fixed node/time budget, warm and cold TT, repeated on ≥30 predeclared unseen FEN clusters and at least 20 trials per cell. Record actual nodes, PV, depth, hashfull where accessible, wall-time and move entropy. Pair by FEN and calculate position-cluster bootstrap intervals; no casual single percentage of "randomness".
- Intentionally toggle `Skill Level` and `UCI_LimitStrength` separately while preserving one engine version and chosen root set; verify PRNG call site with direct source instrumentation (prefer read-only execution and archive altered-source diff if done).
- Separate `value_draw(nodes & 0x2)` from stochasticity: under single-thread stable seed/resource, verify conditional deterministic draw scores; in real original source worlds intervene physical draw logic while measuring root-choice effects and check stage gate.
- Investigate whether root move switches are confined to near-tied candidates and which static features / future plan persistence predict switching, preserving no-causality conclusion unless intervention supports it.

## 5. Intake, custody, and only missing literature after recent uploads

Three PDF uploads were first-page examined and correctly moved without changing IDs to Drive `10_PAPERS`:
- [Silva, Lelis & Bowling (IJCAI-PRICAI XAI workshop 2020 label, event 2021), *Teaching Humans with Justifications of Monte Carlo Tree Search Decisions*](https://drive.google.com/file/d/1BXE5fGC6igEGi9iya5G5uMp4IJ6PqUGO/view): original workshop manuscript; CFJ curling human study n=120, **not chess tested**, and no native Stockfish alpha-beta explanation proof.
- [Gadwal, Greer & McCalla (1991), *UMRAO: A Chess Endgame Tutor*, IJCAI pp 1081–1085](https://drive.google.com/file/d/1w0jFIPg3WyuxyASjvwEXySjdoL2pEeCN/view): expert/novice strategy graphs in bishop-pawn endgames, differentiates strategies from engine minimax lines.
- [*Computer Chess Digest*, archival scan labeled 1983 but inside cover says Volume 1 No.1 1982](https://drive.google.com/file/d/1qICbZlAAxLYyy0WL1kQgT0d-MI3k1RWo/view): contains *The Updated Bratko–Kopec Test*, an important related archival report but **NOT** the original Kopec–Bratko 1982 *Advances in Computer Chess 3* chapter, which remains missing. Citation label includes edition ambiguity.

**Still truly missing exact primary originals in accessible Drive** (no false ownership from related preprints): Björnsson (2024) *Chess and Explainable AI* ICGA 46(2); Kopec & Bratko (1982) *The Bratko-Kopec Experiment* publisher chapter; Demura & Kaneko (2024) *Initial State Diversification* ICGA paper; Gadwal et al. (1993) *Tutoring Bishop-Pawn Endgames* Applied Intelligence; Herbeck & Barth (1996) *An Explanation Tool for Chess Endgames Based on Rules* ICCA; Seidel (1994) *Self-Annotating Elementary Endgames* ICCA; Guid et al. (2013) *Building an Intelligent Tutoring System for Chess Endgames* SciTePress (free [publisher PDF](https://www.scitepress.org/PublishedPapers/2013/43891/pdf/index.html), not yet owned). Silva and Gadwal (1991) originals are **now owned** and excluded.

**00_INTAKE ongoing HOLD**: ambiguous/integrity-critical older files, notably `bshouty1995.pdf` where no readable text; do not silently relabel or relocate. Other older folders not entirely audited. P9 filename survey scope only 1,000 newest, no claims of total corpus census.
