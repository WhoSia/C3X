# C3X 0.29 — P42/R29: Dynamic Events Are Not Yet Causal Strategy Explanations

**Date:** 2026-11-10 KST. **Scientific verdict: negative exploratory result, NOT prospective validation, NOT source computational mediation, NOT a new BinProp method.**

## 1. Founding problem and legitimate prior-art sources (read original owned Drive PDFs first)

C3X aims to demonstrate, on the **same original legal chess history and same alternative first moves**, that a source search mechanism physically influences the root action **because** it tracks valuable, realizable future response-conditioned plans. We have already implemented a recursive two-opponent-node k=3 source-only strategy tree over four previously selected roots (R27), judged its 36 leaves independently, and used BinProp-inspired matched nearby negatives to test eight basic *static* features (R28). However, tree existence and branch label contrasts alone do not give a causally faithful engine explanation.

Direct original primary literature:
- [**Press & Golubev (2026), BinProp, original Drive PDF**](https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view): discriminative binary propositions about resulting chess positions, evaluated on positives, negatives and **nearby negatives**, which preserve early moves of successful paths but deviate later. The full method's LM-based predicate discovery and 200k chess position corpus are **NOT reproduced** by our fixed eight binary events.
- [**Cui, Ling & Ng (2026), original Drive PDF**](https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view): source engine opponent-MultiPV recursive strategic action tree; our R27 reproduces the **branch construction procedure at two opponent levels**, not their full language or human usage tests.
- [**Parfenova (2026), original Drive PDF**](https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view): masked move and mismatched plausible explanations as evidence controls against fluent rationalization.
- [**Bhaskar, Cheng & Chen (2026), QUEEN, original Drive PDF**](https://drive.google.com/file/d/1I1HikAacandg5b75R0zymJlgxAQ41gbG/view): iterative language-model explanation distillation on a specialized expert chess encoder. No training or decoder experiment here.

## 2. Novelty attack before execution

An attractive but mostly invalid claim would be: "R28's static features failed, but comparing each identical prefix to its later endpoint transition necessarily captures higher-order temporal strategy." **Counterexample:** for any shared prefix `p` and Boolean endpoint predicate `f`, define `g(p,leaf) = not f(p) and f(leaf)`. As `p` is fixed across a matched triplet, `g` reduces to either `f(leaf)` or False; it **cannot separate a matched pair if `f(leaf)` did not**. Likewise `f(p) and f(leaf)` is only a renamed endpoint predicate within a fixed prefix. Do not create trivial source-label leaky "temporal" features that add no representation power.

R29 T1 instead declares eight actual *within-path event* predicates using the two latter plies (opponent response, own continuation) that cannot generally be reconstructed from the leaf's feature-vector alone:

1. Opponent's second response captures a piece.
2. Opponent's second response gives check.
3. Source own second response captures.
4. Source own second response gives check.
5. Source own immediate recapture on the same square as the opponent's capture.
6. Source own recovery of a material deficit created by the preceding opponent move.
7. Source own second response moved a pawn.
8. Source own second response promoted a pawn.

All are computed with legal move histories in `python-chess`, from original-root-mover perspective, **before** the existing referee-defined positive/nearby negative pair identities are considered. Thus **static endpoint feature tautology is avoided**, but not the much harder causal-mediation identification problem.

## 3. Real executed methods and source custody

- Original legal histories: P37 archival source SHA `77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361`; previously frozen R27 two-level Cui strategy tree SHA `f41e96bbf598aa824e65467cd1f1c782674aa275460211ce02b68f6eff1d4d5e`, with no referee branch ranking.
- Existing 12 matched positive/nearby negative labels from **R28-M1 SHA `c8768b6ac02e62548a61e87f18bfa4d9406136316da9ae81ee296867aa2433e4`**. Those labels were selected after independent Berserk outcomes in R28, so this is explicitly a posthoc feature probe on already known labels.
- 36 authentic source strategy leaves reconstructed from legal original UCI. 12 common prefix groups each contain 3 alternative two-ply suffixes. Positive and nearby negative case IDs, moves and common prefix validated against R28 labels; no unseen chess result data, no source new search, no independent judge new search.
- [**R29 T1 initial CI FAILED #42741802260**](https://github.com/WhoSia/C3X/actions/runs/42741802260): synthetic R27 fixture used a duplicate event label for two independent games, plus a wrong final side boundary test. Errors were retained and tests repaired; actual source joined keys remain strictly unique. Failures not recast as scientific evidence.
- [**R29 T1 corrected read-only CI SUCCESS #42741912979**](https://github.com/WhoSia/C3X/actions/runs/42741912979): 7 regression tests, actual prior artifact SHA gates, full legal pair reconstruction and rights scan all SUCCESS.
- **New audited JSON SHA256 `87c0ae935a8078600b37f089f5f89b684070117226ffe16480e01d33fbed2cb7`**. No Chat-runtime pip installs, `chess==1.11.2` installed only in runner; fixed hash and source code via normal human author commits.

## 4. Unexpected negative result: event-level features do NOT rescue discriminative signal

Across the **12 historic nearby-negative pairs**, counts of feature firing on the higher-valued only vs lower-valued only path:

| Predeclared actual temporal event | Positive only | Nearby negative only |
| --- | ---: | ---: |
| Opponent's second move captured | 0/12 | **3/12** |
| Opponent's second move checked | 0/12 | 0/12 |
| Source own second move captured | 0/12 | **3/12** |
| Source own second move checked | 0/12 | 0/12 |
| Source own reply immediately recaptured on same square | 0/12 | 1/12 |
| Source own reply recouped opponent-caused material deficit | 0/12 | 1/12 |
| Source own second move pushed a pawn | 0/12 | 0/12 |
| Source own second move promoted a pawn | 0/12 | 0/12 |

A positive-only zero count across all eight features is a substantive failure of **these eight simplistic event predicates on these particular 12 pairs**. Some capture/recapture events appear on lower-valued trajectories, so causal-strategic explanations cannot be based on naive "capture occurred, therefore good" rules. The *negative-only* count is not an independent improvement: reversing a feature's sign after seeing outcomes is posthoc feature tuning, not prospective explanation.

This supports a **research pruning decision**, not proof that temporal information in general is useless. The four preselected roots are clustered within only two games and were already exposed to many earlier experiments; no significance calculation or transfer performance claim is warranted.

## 5. Inference limits and route to truly new science

- **M1 static → T1 event baseline comparison is NOT a fair feature-class competition:** different feature sets and endpoints, labels previously known, no held-out testing. T1 was chosen due to prior failure and has no claim of prospective performance.
- Move-pair properties can be causal consequences of a plan without being causal reasons **used by the original engine**. The source engine may not explicitly encode them; chess trajectory correlations do not identify its internal decision mechanism.
- Finite-depth independent judge `cp` values approximate outcomes and can differ by search context. Source selection and independent referee were separated and SHA sealed, but neither shows root action causation.
- A same-state source-search intervention experiment must specify `Z` as a physical original-source execution site, include positive and negative controls, sham interventions, fixed full history/Chess960/draw state, root candidate intersection, exact actual move selected at *final* depth, TT/search node histories and available budget. "Changed intermediate root candidate" is not "changed final root decision".
- A strategic plan property must be sourced **pre-reference** for the same root alternative and judged at matched depth and node/time budgets, with full legal opponent coverage or rigorously bounded sampling. Require action-mediated information overlap with `Z`, not mere separate Game14/Oct/P34 effects.

## 6. RAVEL: termination and next gate

**RETAIN:** reliable negative evidence; exact source-path event extraction & tamper tests; source/judge label provenance; Drive original PDF priority. Genuine novel chess engine execution requires no new development on these four exposed roots.

**KILL:** any new tuning of "capture, open rook file, check" features against the four visible roots; an attribution/mediation claim based on 36 Cui leaf trajectories alone.

**NEXT:** two parallel tracks with greater discriminative value:

1. **Source C acquisition:** The November 9 preregistered broadcast round yielded only 7 eligible completed standard games vs frozen 8 and therefore HOLD. Recheck only the same official round under the same 8-game rule, **never** silently change sample, preserve its original raw PGN bytes in Drive with identical SHA receipt, and exclude prior exposure before engine scoring. If impossible, select a *new* genuinely preregistered independent event without learning from its future results.
2. **Source A/D/F physical same-world intervention:** design a source-level experiment at a genuinely new position where perturbation of a measured original search feature changes final root candidate selection *and* a preregistered response-conditioned future plan property. Retain the original R20 Game14 intermediate-root-change as a supported but weak precedent, not an established natural mediation proof.

## 7. Drive 미보유 원문 — 색인 검색 기준

| Previously referenced literature | Search result | Status |
| --- | --- | --- |
| SARFA arXiv:1912.12191 | No original primary PDF located; indirect references only | Drive 미확보 (색인 검색 기준) |
| Sandmann et al. arXiv:2508.21380v4 | No original primary PDF located; archive mention only | Drive 미확보 (색인 검색 기준) |
| Ciancarini & Pareschi arXiv:2609.18286 | No original primary PDF located; bibliographic identity also needs verification | Drive 미확보 (색인 검색 기준) |
