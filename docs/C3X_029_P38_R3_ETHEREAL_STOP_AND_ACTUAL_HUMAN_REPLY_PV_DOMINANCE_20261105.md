# C3X 0.29-P38/R3 — External-Eight-Event Archived Human-Reply Court: PV 4/6, JSON 2/6, C3X Plan 1/6

**Date:** 2026-11-05 KST. **Evidence:** authentic original P37 source-only, pre-referee forecast + separate historical human game continuations, independently executed read-only 2026-11-05 CI, Drive raw SHA verified. **Scientific label:** `POSTHOC_ACTUAL_HUMAN_REPLY_AUDIT_NOT_CONFIRMATORY`. This paper must NOT call the result a prospective blinded human outcome trial or an independent causal explanation success.

## A. Original preregistered source/forecast and preserved negative (P37)

P37/R1 originally precommitted 8 distinct late-October 2026 Lichess **event families**, one game from each, original raw PGNs and full game move histories sealed without any Stockfish move/score model outputs. This is an exploratory external event-family sample only; global historical C3X 0.28/0.25 disjointness and some source dates remain unresolved. Source 8-event original artifact SHA256 `3f16f69c6cb01029c519aeb24654913303916ce79537c1a86497bb9c84b79191`, original manifest member SHA `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`.

P37/R2 deterministic 3 fixed rival predictor outputs were **sealed before any 96k Stockfish referee run** using input with ONLY the first 30 original UCI plies, not the following played move or opponent reply; original sealed input SHA `0f6a3c371e4154342f65167dfa9afa269705999c549eec53235d8763cb18ceb9`. Original forecast ZIP SHA256 `721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6`, forecast JSON SHA256 `da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051`. Prediction methods remain unchanged: Stockfish16+PV, deterministic 1-ply capture/check conditional JSON, and 3-ply legal material-return C3X-inspired heuristic; the last is **NOT the full C3X neural causal explanation system**. The legal material search cost for C3X was 24,894 own follow-up move enumerations vs 0 for simple JSON, despite identical shared 24k native SF16 inputs.

P37/R4 same-engine 96k finite-PV reply label performance: Stockfish PV 11/15, simple JSON 2/15, C3X heuristic 4/15; one of 16 lacked reference. PV-only 7, C3X-only 0. This reference is Stockfish-labeled, not chess truth. Do not erase this negative.

## B. R1/R2 Ethereal cross-engine attempt — technically invalid, STOP

An independent historical classical-eval engine Ethereal 12.75 (official Git `b55ed96881f163940569145fbcc4e222d7272338`) was compiled from original source. P38/R1 [CI 41981821764](https://github.com/WhoSia/C3X/actions/runs/41981821764) **successfully finished at CI level** but requested 96k/192k forced-root search used only **2–5 actual nodes, depth1**, with 12/16 no opponent PV reply. The apparent C3X 4/4 vs PV 3/4 on four shallow replies is **INVALID**, not an encouraging cross-family validation.

R2 preregistered source correction: first apply candidate to historical board, then run unrestricted Ethereal at 96k and 192k, requiring >=90% requested actual nodes and depth >=3. [CI 41982222662](https://github.com/WhoSia/C3X/actions/runs/41982222662) **FAIL** under `P38_ETHEREAL_HOLD_INSUFFICIENT_NATIVE_SEARCH_NODES`. Thus no valid Ethereal reference observations were obtained. **The source prereg's STOP criterion is now enforced: do not spend additional cycles on this historical Ethereal protocol** unless a genuinely new methodological need justifies re-opening with an explicit separate preregistration. Preserve raw failed original ZIPs privately:
- [P38/R1 technically invalid ZIP](https://drive.google.com/file/d/1oCjMp9c3yjWt8sVGgrjVVfMT4Y6iJM4r/view)
- [P38/R2 native node-gate FAIL ZIP](https://drive.google.com/file/d/1ZcOHUgqR914IZxOobcpjpgT6uYUS5MT5/view).

## C. External observation: the opponent's actual move in a completed tournament game

The FULL P37/R1 original histories contain the actual played move at halfmove index30 (31st move in the UCI list), and actual opponent reply at index31. We now **looked at actual post-prefix history after the original prediction was sealed**, without modifying source or predictions. Only if the *actual human played move* appears in the presealed Stockfish top-2 candidate roots do we possess an *observed actual opponent reply for that candidate*. The unplayed foil's counterfactual opponent response is not observable in the same game: NEVER fabricate a human reference label for it.

Original read-only reproducer:
- [Auditor with SHA, exact 30-ply prefix + FEN + legal human reply gates](../tools/c3x_029_p38_r3_original_human_reply_audit.py).
- [Adversarial tests of move coverage, hallucinated foils, prefix drift and illegal reply](../tools/test_c3x_029_p38_r3_original_human_reply_audit.py).
- [Native GitHub Actions archival adjudicator 41983017226](https://github.com/WhoSia/C3X/actions/runs/41983017226) **SUCCESS**, all tests and independent recount PASS. Original artifact outer ZIP SHA256 `82de34449db592e3ba56ffbfa54afaa1f3357d831f615bb641edbb43b1c933d0`, JSON SHA256 `967256b6013c836e6ff401768ecb508852f1ef9afeeed07c46f08daa6e74d4b6`. [Drive original ZIP](https://drive.google.com/file/d/1hEW4g4S8ZmXBsIAHYNMXbg__VvU7NM_C/view), independently re-fetched and **exact SHA256 identity verified** against original GitHub Actions bytes.

**All source-eight denominator preserved:** actual played move was one of the two previously frozen SF16 candidates in **6/8** distinct event games. Other **2/8** had no observable corresponding historical opponent reply to either frozen candidate; preserve as `NO_ACTUAL_COUNTERFACTUAL_FOR_FROZEN_CANDIDATES`, not correct/wrong.

| Predictor | Exact observed tournament human reply | Wrong among evaluable | Non-covered human root |
|---|---:|---:|---:|
| SF16 24k PV | **4/6 (66.7%)** | 2 | 2 |
| Simple JSON | **2/6 (33.3%)** | 4 | 2 |
| C3X three-ply finite lawful material heuristic | **1/6 (16.7%)** | 5 | 2 |

PV-only 3, C3X-only 0, both correct 1, neither 2 among six observed. By family: Sahel all wrong; KazChess PV only; Chinese League PV only; Clutch PV only; Freiburger JSON only; Cerrado all correct; Magdeburg and Greg Hjorth no observed corresponding candidate root. Original legal outcomes and full source row IDs are in the archive. This is **small descriptive n=6**, no confidence of generalizable superiority, not paired independent player randomization, not optimal opponent play.

**Scientific implications:** current C3X-inspired shallow material heuristic shows **NO incremental exact human reply forecast benefit beyond PV**, in a second external observational label context beyond self-referential SF16 reference. This neither refutes overall C3X research origin nor NNUE machine causal hypothesis; it **strongly disfavors further iterations that just relabel shallow 3-ply material maximization as deep strategic explanation**.

## D. Ruthless-next-step research decision

**STOP** model-free shallow 3-ply opponent selection as C3X's representative theory; **do NOT** start another cosmetic tiny variant. Separate three test targets:
- `H_B`: opponent actual human reply behavior prediction — must be assessed ONLY where the played move is actually the candidate, and with game/event heldout and baseline/abstention coverage.
- `H_V`: counterfactual **chess-valued** reply-conditioned consequence — cannot be labeled from a single human continuation. Must use independently rule-verifiable adversarial certificates, tablebases or explicitly lower-quality multi-engine consensus, with separate resource/uncertainty ledger.
- `H_M`: path-faithful Stockfish internal decision mediation — separate mechanistic identification; P35 native actual NNUE/HCE dispatcher PASS is not root-level intervention proof.

Next stage **P39 hypothesis generation**: choose ONE non-tautological action-conditioned chess-valued `Q` (not equal to the three-ply heuristic's own objective), and freeze source family and strong comparable predictor cost before seeing test outputs. A genuine learned or source-grounded C3X model only promotes if it forecasts independent `Q` beyond score+PV and simple JSON with **equal total compute** or clearly improved cost/coverage tradeoff. Historical 0.28 broad game/event exclusion remains HOLD.

## Governance

All GitHub mutations by authenticated human `WhoSia`; GitHub Actions read-only contents + artifact upload, no `github-actions[bot]` source contribution. Notion semantic scientific authority; Drive immutable original byte authority; GitHub executable source/test/document authority. All failures retain original receipts, no rewriting.
