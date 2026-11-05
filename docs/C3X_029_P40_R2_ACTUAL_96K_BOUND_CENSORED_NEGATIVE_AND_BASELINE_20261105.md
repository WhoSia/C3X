# C3X 0.29-P40/R2 — Critical Correction: P37 Referee Bounds Censor Three of Eight Chess Comparisons

2026-11-05 KST. ORIGINAL READ-ONLY CI #41995197419 SUCCESS. Its predecessor #41994900302 failed the correct alpha-beta bound gate, exposing an analytic error: treating source-reported `upperbound`/`lowerbound` as exact centipawn values.

## Historical inputs, exact and immutable

P39/R2 actual complete chess-law mobility JSON SHA256 `84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf`; P37/R2 native Stockfish16 96k forced-root referee JSON SHA256 `d92c33d05fa506b1a84c222b57729f76a53a95970dd61ba38f67ea1ce3f700fa`. Inputs were already seen, so strictly retrospective; the 96k reference is the SAME chess engine family in separately forced-root searches, neither a perfect-play truth nor independent model.

## Essential interval treatment

An exact 50cp evaluation is represented [50,50]; a reported 53cp upperbound is (-infinity,53]; a reported -18cp lowerbound is [-18,+infinity). A strict A>B comparison can be certified from the reported bounds only if lower(A)>upper(B). This is an engine-reported finite-search relationship, not mathematical perfect chess minimax bound. If intervals overlap, the candidate preference is **CENSORED**, never assigned by selecting raw point values. Mate scores also cannot be treated as integer centipawns. Original score-bound flags preserved unchanged.

## Verified denominators and outcome

Eight original exposed game pairs: **5/8 identified**, **3/8 censored because comparison bounds overlap** (Sahel first 50 exact/second 53 upper, Clutch first 11 exact/second -18 lower, Cerrado both upper). For the five identifiable cases (KazChess, Chinese League, Freiburger, Magdeburg, Greg Hjorth), the earlier Stockfish16 24k first-choice baseline matched the preferred deeper 96k bounded score in **5/5**. P39 R2 lower-W mobility selected a non-tied move in only 3 of these 5: **2/3 agreements** (Chinese, Magdeburg), **1/3 disagreement** (KazChess), and **2/5 abstentions** (Freiburger, Hjorth). Across all eight, mobility chooses 5 but two of its choices (Sahel and Cerrado) have no decided reference outcome. Never claim 4/5 proxy accuracy; that earlier raw-score reading was invalid under the source flags.

## Implication for paper proposals

This material is evidence **against** turning shallow response-mobility/forcing into a publishable chess-value account. A one-line Stockfish24k move ranking is already strong on this tiny same-engine subset. No statistical generalization, independent model or value explanation superiority is demonstrated. The data are small, postselected and historically seen. Avoid constructing a 'successful' subgroup from the three source-identifiable, non-tied proxy cases.

## Evidence receipts

[Original CI successful after source-bound correction](https://github.com/WhoSia/C3X/actions/runs/41995197419); [correct code](https://github.com/WhoSia/C3X/blob/main/tools/c3x_029_p40_r2_original_baseline_court.py); [tests](https://github.com/WhoSia/C3X/blob/main/tools/test_c3x_029_p40_r2_original_baseline_court.py). Both mathematical P40/R1 toy proof and authentic P40/R2 source-bound reanalysis executed in read-only CI, artifact exact JSON member SHA to be retained. Historical errors #41994900302 kept visible, not rewritten.

PI decision: Main thesis remains high ambition: a response-conditioned value-bearing plan forecast that contributes correct off-PV consequences beyond strong classical evaluation+PV, and a separate NNUE→search ancestor→root intervention when claiming internal source faithfulness. Neither has yet passed.